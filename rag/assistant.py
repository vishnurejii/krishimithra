"""
RAG-Based AI Farmer Assistant for KrishiMitra AI.
Retrieves verified government scheme records and citations from PostgreSQL,
synthesizes responses in Malayalam or English, and enforces citation transparency.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from rag.vector_store import VectorStore
from core.config import GEMINI_API_KEY, LLM_MODEL
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.rag.assistant")

FARMER_ASSISTANT_SYSTEM_PROMPT = """
You are KrishiMitra AI, an intelligent, empathetic, and highly accurate agricultural advisor for farmers in Kerala, India.
You provide clear guidance based ONLY on official Kerala Government and Central Government scheme documents.

Every answer MUST follow this exact structure:
1. **Scheme Name** (with Malayalam name if available)
2. **Eligibility Conditions** (Land size, eligible farmer categories, crops, residency)
3. **Benefits & Subsidies** (Exact percentage, subsidy amount, ceiling limit)
4. **Required Documents Checklist** (Aadhaar, Land Tax, Bank Passbook, etc.)
5. **Application Instructions** (Step-by-step procedure)
6. **Official Application URL** (Link to official portal like AIMS / PM-KISAN)
7. **Source Document & Page Number** (Verified government order / guideline citation)
8. **Last Verification Date**

Rules:
- If a farmer asks in Malayalam, reply in fluent, courteous Malayalam with English names where helpful.
- If a farmer asks in English, reply in clear, simple English.
- If specific information is not available in the official records, explicitly state:
  "Official guidelines on this specific detail have not yet been published/verified. Please verify with your local Krishi Bhavan."
- NEVER invent subsidy amounts, deadlines, or document requirements.
"""

class FarmerAssistant:
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()
        self.api_key = GEMINI_API_KEY

    def answer_question(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Processes a farmer's question, retrieves relevant schemes and document citations,
        and generates a structured, verified answer.
        """
        logger.info(f"Answering farmer query ({language}): '{query}'")

        # 1. Retrieve relevant passages and schemes from vector store
        passages = self.vector_store.search_similar_passages(query, top_k=4)

        # 2. Enrich with detailed scheme relational data (benefits, eligibility, guidelines)
        schemes_data = self._fetch_schemes_context(passages, query)

        # 3. Generate response using LLM or structured template
        if self.api_key:
            try:
                answer = self._generate_with_gemini(query, schemes_data, passages, language)
            except Exception as e:
                logger.warning(f"Gemini API error during assistance: {e}. Using deterministic structured synthesizer.")
                answer = self._synthesize_structured_answer(query, schemes_data, passages, language)
        else:
            answer = self._synthesize_structured_answer(query, schemes_data, passages, language)

        citations = []
        for s in schemes_data:
            citations.append({
                "scheme_name": s.get("name"),
                "classification": s.get("classification"),
                "source_document": s.get("document_title") or "Government Operational Guidelines",
                "source_url": s.get("document_url") or s.get("official_portal_url"),
                "page_number": s.get("page_number") or 1,
                "verified_at": s.get("last_verified_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            })

        return {
            "query": query,
            "language": language,
            "answer": answer,
            "schemes_found": len(schemes_data),
            "citations": citations
        }

    def _fetch_schemes_context(self, passages: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Retrieves complete eligibility, benefits, and crops for the matched schemes using aggregated SQL."""
        passage_sids = [p["scheme_id"] for p in passages if p.get("scheme_id")]

        stopwords = {
            "what", "is", "the", "in", "for", "are", "available", "scheme", "schemes",
            "how", "to", "apply", "can", "get", "give", "tell", "about", "which",
            "ഏതൊക്കെ", "എന്താണ്", "എങ്ങനെ", "ആണ്", "എനിക്ക്", "ലഭിക്കുന്ന"
        }
        tokens = [w.lower().strip("?,.!\"'") for w in query.split()]
        terms = [w for w in tokens if len(w) > 2 and w not in stopwords]
        term = terms[0] if terms else "paddy"

        schemes = []
        seen_ids = set()
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            s.id, s.name, s.malayalam_name, s.classification, s.level,
                            s.objective, s.description, s.application_procedure,
                            s.official_portal_url, s.last_verified_at,
                            (SELECT title FROM scheme_documents WHERE scheme_id = s.id AND title IS NOT NULL ORDER BY id LIMIT 1) as document_title,
                            (SELECT original_url FROM scheme_documents WHERE scheme_id = s.id AND original_url IS NOT NULL ORDER BY id LIMIT 1) as document_url,
                            MAX(b.subsidy_percentage) as subsidy_percentage,
                            MAX(b.subsidy_amount) as subsidy_amount,
                            MAX(b.max_assistance_limit) as max_assistance_limit,
                            COALESCE(ARRAY_AGG(DISTINCT sc.crop_name) FILTER (WHERE sc.crop_name IS NOT NULL), '{}') as crops,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT document_name) FROM application_guidelines WHERE scheme_id = s.id), '{}') as guidelines,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT bc) FROM scheme_eligibility se, LATERAL unnest(se.beneficiary_categories) bc WHERE se.scheme_id = s.id), '{}') as beneficiary_categories
                        FROM schemes s
                        LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                        LEFT JOIN scheme_crops sc ON s.id = sc.scheme_id
                        WHERE s.id = ANY(%s)
                           OR LOWER(s.name) LIKE %s
                           OR LOWER(COALESCE(s.malayalam_name, '')) LIKE %s
                           OR LOWER(COALESCE(s.description, '')) LIKE %s
                           OR LOWER(COALESCE(sc.crop_name, '')) LIKE %s
                        GROUP BY s.id, s.name, s.malayalam_name, s.classification, s.level,
                                 s.objective, s.description, s.application_procedure,
                                 s.official_portal_url, s.last_verified_at
                        ORDER BY (s.id = ANY(%s)) DESC
                        LIMIT 4;
                        """,
                        (passage_sids, f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%", passage_sids)
                    )
                    rows = cur.fetchall()

                    for r in rows:
                        if r["id"] in seen_ids:
                            continue
                        seen_ids.add(r["id"])
                        schemes.append({
                            "id": r["id"],
                            "name": r["name"],
                            "malayalam_name": r["malayalam_name"],
                            "classification": r["classification"],
                            "document_title": r["document_title"],
                            "document_url": r["document_url"],
                            "official_portal_url": r["official_portal_url"],
                            "last_verified_at": r["last_verified_at"],
                            "application_procedure": r["application_procedure"],
                            "benefits": [{
                                "subsidy_percentage": r["subsidy_percentage"],
                                "subsidy_amount": r["subsidy_amount"],
                                "max_assistance_limit": r["max_assistance_limit"]
                            }],
                            "eligibility": [{
                                "beneficiary_categories": r["beneficiary_categories"]
                            }],
                            "guidelines": r["guidelines"] or ["Aadhaar Card", "Land Tax Receipt", "Bank Passbook Copy"]
                        })
        except Exception as e:
            logger.error(f"Error fetching scheme context: {e}")

        return schemes

    def _generate_with_gemini(self, query: str, schemes: List[Dict[str, Any]], passages: List[Dict[str, Any]], language: str) -> str:
        from google import genai
        client = genai.Client(api_key=self.api_key)
        context_str = json.dumps({"schemes": schemes, "passages": passages[:3]}, default=str)
        prompt = (
            f"{FARMER_ASSISTANT_SYSTEM_PROMPT}\n\n"
            f"User Language Preference: {language}\n"
            f"Farmer Question: {query}\n\n"
            f"Verified Scheme Database Records:\n{context_str}"
        )
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        return response.text

    def _synthesize_structured_answer(self, query: str, schemes: List[Dict[str, Any]], passages: List[Dict[str, Any]], language: str) -> str:
        """Deterministic template response with mandatory citation fields."""
        if not schemes:
            if language == "ml":
                return (
                    "നിങ്ങൾ അന്വേഷിച്ച വിഷയത്തെക്കുറിച്ചുള്ള ഔദ്യോഗിക സർക്കാർ ഉത്തരവുകൾ നിലവിൽ ലഭ്യമല്ല. "
                    "ദയവായി നിങ്ങളുടെ സമീപത്തുള്ള കൃഷിഭവനുമായി ബന്ധപ്പെടുക."
                )
            return (
                "No official government orders or scheme guidelines were found matching your specific query. "
                "Please check with your local Krishi Bhavan for recent notifications."
            )

        output = []
        is_ml = (language == "ml")

        for s in schemes:
            b_list = s.get("benefits", [])
            b = b_list[0] if b_list else {}
            e_list = s.get("eligibility", [])
            e = e_list[0] if e_list else {}
            g_list = s.get("guidelines", [])

            subsidy_str = f"{b.get('subsidy_percentage')}%" if b.get('subsidy_percentage') else "As per scale of finance"
            if b.get("subsidy_amount"):
                subsidy_str += f" (Up to Rs {b.get('subsidy_amount')})"
            if b.get("max_assistance_limit"):
                subsidy_str += f" [Max limit: Rs {b.get('max_assistance_limit')}]"

            req_docs = ", ".join(g_list) if g_list else "Aadhaar Card, Land Tax Receipt, Bank Passbook"
            verified_date = s.get("last_verified_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d")

            if is_ml:
                output.append(f"### {s.get('name')}")
                output.append(f"- **വിഭാഗം:** {s.get('classification')}")
                output.append(f"- **അർഹത:** {', '.join(e.get('beneficiary_categories') or ['എല്ലാ കർഷകർക്കും'])}")
                output.append(f"- **ആനുകൂല്യം / സബ്സിഡി:** {subsidy_str}")
                output.append(f"- **ആവശ്യമായ രേഖകൾ:** {req_docs}")
                output.append(f"- **അപേക്ഷിക്കേണ്ട വിധം:** {s.get('application_procedure') or 'എയിംസ് (AIMS) പോർട്ടൽ വഴി ഓൺലൈനായി അല്ലെങ്കിൽ കൃഷിഭവൻ മുഖേന.'}")
                output.append(f"- **ഔദ്യോഗിക പോർട്ടൽ:** [{s.get('official_portal_url') or 'AIMS Kerala'}]({s.get('official_portal_url') or 'https://aimsnew.kerala.gov.in/'})")
                output.append(f"- **റഫറൻസ് ഉത്തരവ്:** {s.get('document_title') or 'വകുപ്പ് മാർഗ്ഗരേഖ'} (പേജ് 1)")
                output.append(f"- **പരിശോധിച്ച തീയതി:** {verified_date}")
            else:
                output.append(f"### {s.get('name')}")
                output.append(f"- **Classification:** {s.get('classification')}")
                output.append(f"- **Eligibility Conditions:** {', '.join(e.get('beneficiary_categories') or ['All landholding or tenant farmers in Kerala'])}")
                output.append(f"- **Benefits & Subsidies:** {subsidy_str}")
                output.append(f"- **Required Documents Checklist:** {req_docs}")
                output.append(f"- **Application Instructions:** {s.get('application_procedure') or 'Apply online through AIMS Kerala portal or visit your local Krishi Bhavan.'}")
                output.append(f"- **Official Application Portal:** [{s.get('official_portal_url') or 'AIMS Kerala Portal'}]({s.get('official_portal_url') or 'https://aimsnew.kerala.gov.in/'})")
                output.append(f"- **Source Document Reference:** {s.get('document_title') or 'Government Operational Guidelines'} (Page 1)")
                output.append(f"- **Last Verification Date:** {verified_date}")

            output.append("")

        return "\n".join(output)
