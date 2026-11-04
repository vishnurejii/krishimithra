"""
Bilingual (English & Malayalam) Keyword Registry for Scheme & Document Discovery.
"""

from typing import List, Set, Tuple

# English Agriculture & Scheme Keywords
ENGLISH_KEYWORDS: List[str] = [
    # Schemes & Financial Terms
    "scheme", "subsid", "assistance", "grant", "incentive", "royalty", "pension",
    "benefit", "compensation", "insurance", "loan", "credit", "interest subvention",
    # Crops & Farming Domains
    "agriculture", "farmer", "paddy", "rice", "coconut", "rubber", "spices",
    "pepper", "cardamom", "ginger", "banana", "vegetable", "tuber", "horticulture",
    "plantation", "dairy", "cow", "cattle", "milma", "goat", "poultry",
    "fisheries", "aquaculture", "biofloc", "fish farming",
    # Farming Practices & Inputs
    "organic farming", "natural farming", "soil health", "soil test", "irrigation",
    "micro-irrigation", "drip", "sprinkler", "borewell", "pump", "solar pump",
    "mechanization", "tractor", "tiller", "harvester", "machinery",
    "seed", "fertilizer", "manure", "vermicompost", "biofertilizer",
    "fallow land", "jlg", "joint liability group", "kudumbashree", "fpo",
    # Document Types & Official Terms
    "government order", "g.o.", "circular", "guideline", "notification",
    "application form", "amendment", "order no", "eligibility", "deadline",
    "krishi bhavan", "pm-kisan", "pmfby", "rkvy", "midh", "kcc"
]

# Malayalam Agriculture & Scheme Keywords
MALAYALAM_KEYWORDS: List[str] = [
    # Schemes & Benefits
    "പദ്ധതി", "സബ്സിഡി", "ധനസഹായം", "ഗ്രാന്റ്", "റോയൽറ്റി", "പെൻഷൻ",
    "ആനുകൂല്യം", "നഷ്ടപരിഹാരം", "ഇൻഷുറൻസ്", "വായ്പ", "പലിശ ഇളവ്",
    # Farmers & Cultivation
    "കർഷക", "കർഷകൻ", "കൃഷി", "നെൽകൃഷി", "നെല്ല്", "തെങ്ങ്", "നാളികേരം",
    "റബ്ബർ", "സുഗന്ധവ്യഞ്ജന", "കുരുമുളക്", "ഏലം", "ഇഞ്ചി", "വാഴ",
    "പച്ചക്കറി", "കിഴങ്ങുവർഗ്ഗ", "ഹോർട്ടികൾച്ചർ", "തോട്ടവിള",
    # Allied Sectors
    "ക്ഷീര", "പശു", "കന്നുകാലി", "ആട്", "കോഴി", "മൃഗസംരക്ഷണം",
    "മത്സ്യകൃഷി", "ഉൾനാടൻ മത്സ്യകൃഷി", "കൂട് കൃഷി",
    # Inputs, Infrastructure & Machinery
    "ജൈവകൃഷി", "പ്രകൃതി കൃഷി", "മണ്ണ് പരിശോധന", "ജലസേചനം", "സൂക്ഷ്മ ജലസേചനം",
    "തുള്ളി നന", "ബോർവെൽ", "സോളാർ പമ്പ്", "കാർഷിക യന്ത്രങ്ങൾ", "ട്രാക്ടർ",
    "വിത്ത്", "വളം", "ജൈവവളം", "തരിശുരഹിത", "തരിശുഭൂമി", "കുടുംബശ്രീ",
    # Official Documents
    "ഉത്തരവ്", "സർക്കുലർ", "മാർഗ്ഗരേഖ", "വിജ്ഞാപനം", "അപേക്ഷാ ഫോറം",
    "മാനദണ്ഡങ്ങൾ", "കൃഷി ഭവൻ", "എയിംസ്", "കതിർ"
]

ALL_KEYWORDS: List[str] = ENGLISH_KEYWORDS + MALAYALAM_KEYWORDS

def match_keywords(text: str) -> Tuple[int, List[str]]:
    """
    Evaluates text against bilingual keywords and returns match score and matched terms.
    """
    if not text:
        return 0, []
    text_lower = text.lower()
    matches = []
    for kw in ALL_KEYWORDS:
        if kw in text_lower:
            matches.append(kw)
    return len(matches), matches
