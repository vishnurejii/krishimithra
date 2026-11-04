"""
Test for Stage 7: RAG AI Farmer Assistant
Tests bilingual query handling (English and Malayalam) with strict citation verification.
"""

import sys
from pathlib import Path

# Enable UTF-8 encoding for Windows console output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.assistant import FarmerAssistant

def main():
    assistant = FarmerAssistant()

    test_queries = [
        ("What subsidies are available for pepper cultivation?", "en"),
        ("I have two acres of land in Wayanad. Which schemes can I apply for?", "en"),
        ("What documents are required for PM-KISAN?", "en"),
        ("നെൽവയൽ റോയൽറ്റിക്ക് എങ്ങനെയാണ് അപേക്ഷിക്കേണ്ടത്?", "ml")
    ]

    for q, lang in test_queries:
        print("\n" + "=" * 80)
        print(f"FARMER QUESTION ({lang.upper()}): {q}")
        print("=" * 80)
        res = assistant.answer_question(q, language=lang)
        print(res["answer"])
        print("\n[CITATIONS RETURNED]")
        for c in res["citations"]:
            print(f" - {c['scheme_name']} | Source: {c['source_document']} (Page {c['page_number']}) | Verified: {c['verified_at']}")

if __name__ == "__main__":
    main()
