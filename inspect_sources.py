"""
Stage 1: Official Source Inspector & Health Checker for KrishiMitra AI
Probes official Kerala & Central Government portals for accessibility, SSL behavior,
headers, response times, and basic scheme/PDF link discovery.
"""

import sys
import json
import time
import urllib.parse
from datetime import datetime, timezone
import requests
import urllib3

# Suppress insecure request warnings for government sites with custom/outdated cert chains when testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 KrishiMitraBot/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ml;q=0.8",
}

SOURCES_TO_INSPECT = [
    # Kerala State Government - Core Agriculture
    {
        "id": "KL_AGRI_DEPT",
        "name": "Agriculture Development and Farmers' Welfare Department, Kerala",
        "level": "State",
        "category": "Agriculture and Farmers' Welfare",
        "url": "https://keralaagriculture.gov.in/",
        "scheme_url": "https://keralaagriculture.gov.in/en/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_AIMS",
        "name": "AIMS Kerala (Agricultural Information Management System)",
        "level": "State",
        "category": "Farmer Registration & Subsidies",
        "url": "https://aimsnew.kerala.gov.in/",
        "scheme_url": "https://aimsnew.kerala.gov.in/",
        "type": "Portal"
    },
    {
        "id": "KL_KATHIR",
        "name": "KATHIR Kerala (Kerala Agriculture Technology Hub and Information Repository)",
        "level": "State",
        "category": "Integrated Agri Platform",
        "url": "https://kathir.kerala.gov.in/",
        "scheme_url": "https://kathir.kerala.gov.in/",
        "type": "Portal"
    },
    {
        "id": "KL_GO_PORTAL",
        "name": "Kerala Government Orders Portal",
        "level": "State",
        "category": "Government Orders & Notifications",
        "url": "https://document.kerala.gov.in/",
        "scheme_url": "https://document.kerala.gov.in/",
        "type": "Orders Repository"
    },
    {
        "id": "KL_SPB",
        "name": "Kerala State Planning Board",
        "level": "State",
        "category": "Planning & Plan Schemes",
        "url": "https://spb.kerala.gov.in/",
        "scheme_url": "https://spb.kerala.gov.in/economic-review-schemes",
        "type": "Statutory Board"
    },
    # Allied Sectors
    {
        "id": "KL_AHD",
        "name": "Kerala Animal Husbandry Department",
        "level": "State",
        "category": "Animal Husbandry & Livestock",
        "url": "https://ahd.kerala.gov.in/",
        "scheme_url": "https://ahd.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_DAIRY",
        "name": "Kerala Dairy Development Department",
        "level": "State",
        "category": "Dairy Development",
        "url": "https://dairydevelopment.kerala.gov.in/",
        "scheme_url": "https://dairydevelopment.kerala.gov.in/index.php/schemes",
        "type": "Department"
    },
    {
        "id": "KL_FISHERIES",
        "name": "Kerala Fisheries Department",
        "level": "State",
        "category": "Fisheries and Aquaculture",
        "url": "https://fisheries.kerala.gov.in/",
        "scheme_url": "https://fisheries.kerala.gov.in/schemes",
        "type": "Department"
    },
    {
        "id": "KL_COOPERATION",
        "name": "Kerala Department of Cooperation",
        "level": "State",
        "category": "Cooperation & Credit",
        "url": "https://cooperation.kerala.gov.in/",
        "scheme_url": "https://cooperation.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_SOIL_CONS",
        "name": "Kerala Soil Survey and Soil Conservation",
        "level": "State",
        "category": "Soil Survey & Watershed Management",
        "url": "https://soilconservation.kerala.gov.in/",
        "scheme_url": "https://soilconservation.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_KUDUMBASHREE",
        "name": "Kudumbashree State Mission (Agri programmes & JLGs)",
        "level": "State",
        "category": "Community Agriculture & JLGs",
        "url": "https://kudumbashree.org/",
        "scheme_url": "https://kudumbashree.org/pages/53",
        "type": "Agency"
    },
    {
        "id": "KL_LSGD",
        "name": "Kerala Local Self Government Department (LSGD)",
        "level": "Local/State",
        "category": "Local Self Government & Panchayat Projects",
        "url": "https://lsgkerala.gov.in/",
        "scheme_url": "https://lsgkerala.gov.in/en/schemes",
        "type": "Department"
    },
    {
        "id": "KL_KSCARDB",
        "name": "Kerala State Co-operative Agricultural and Rural Development Bank",
        "level": "State",
        "category": "Agricultural Loans & Rural Credit",
        "url": "https://kscardb.com/",
        "scheme_url": "https://kscardb.com/schemes/",
        "type": "Financial Institution"
    },
    {
        "id": "KL_FOREST",
        "name": "Kerala Forest and Wildlife Department",
        "level": "State",
        "category": "Agroforestry & Eco-Development",
        "url": "https://forest.kerala.gov.in/",
        "scheme_url": "https://forest.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_SCDD",
        "name": "Kerala Scheduled Castes Development Department",
        "level": "State",
        "category": "SC Farmer Assistance & Subsidies",
        "url": "https://scdd.kerala.gov.in/",
        "scheme_url": "https://scdd.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_STDD",
        "name": "Kerala Scheduled Tribes Development Department",
        "level": "State",
        "category": "ST Agriculture & Traditional Cultivation",
        "url": "https://stdd.kerala.gov.in/",
        "scheme_url": "https://stdd.kerala.gov.in/schemes/",
        "type": "Department"
    },
    {
        "id": "KL_IRRIGATION",
        "name": "Kerala Water Resources & Irrigation Department",
        "level": "State",
        "category": "Irrigation & Water Management",
        "url": "https://irrigation.kerala.gov.in/",
        "scheme_url": "https://irrigation.kerala.gov.in/schemes",
        "type": "Department"
    },
    {
        "id": "KL_KAU",
        "name": "Kerala Agricultural University",
        "level": "State/Academic",
        "category": "Advisory, Seeds & Extension",
        "url": "https://kau.in/",
        "scheme_url": "https://kau.in/programmes",
        "type": "University"
    },
    # Central Government & Commodity Boards
    {
        "id": "CEN_PM_KISAN",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "level": "Central",
        "category": "Direct Income Support",
        "url": "https://pmkisan.gov.in/",
        "scheme_url": "https://pmkisan.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "CEN_PMFBY",
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "level": "Central",
        "category": "Crop Insurance",
        "url": "https://pmfby.gov.in/",
        "scheme_url": "https://pmfby.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "CEN_MOAFW",
        "name": "Ministry of Agriculture & Farmers Welfare, India",
        "level": "Central",
        "category": "Central Schemes & Guidelines",
        "url": "https://agriwelfare.gov.in/",
        "scheme_url": "https://agriwelfare.gov.in/en/Major",
        "type": "Ministry"
    },
    {
        "id": "CEN_MIDH",
        "name": "Mission for Integrated Development of Horticulture (MIDH)",
        "level": "Central",
        "category": "Horticulture Development",
        "url": "https://midh.gov.in/",
        "scheme_url": "https://midh.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "CEN_AIF",
        "name": "Agriculture Infrastructure Fund (AIF)",
        "level": "Central",
        "category": "Infrastructure Financing & Credit",
        "url": "https://agriinfra.dac.gov.in/",
        "scheme_url": "https://agriinfra.dac.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "CEN_SOIL_HEALTH",
        "name": "Soil Health Card Scheme",
        "level": "Central",
        "category": "Soil Testing & Nutrient Management",
        "url": "https://soilhealth.dac.gov.in/",
        "scheme_url": "https://soilhealth.dac.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "CEN_PM_KUSUM",
        "name": "PM-KUSUM (Solar Pumps and Grid-connected Solar)",
        "level": "Central",
        "category": "Solar Irrigation & Green Energy",
        "url": "https://pmkusum.mnre.gov.in/",
        "scheme_url": "https://pmkusum.mnre.gov.in/",
        "type": "Central Scheme"
    },
    {
        "id": "BD_RUBBER",
        "name": "Rubber Board India (Kottayam, Kerala)",
        "level": "Commodity Board",
        "category": "Plantation & Rubber Subsidies",
        "url": "https://rubberboard.gov.in/",
        "scheme_url": "https://rubberboard.gov.in/",
        "type": "Board"
    },
    {
        "id": "BD_COCONUT",
        "name": "Coconut Development Board (Kochi, Kerala)",
        "level": "Commodity Board",
        "category": "Coconut Schemes & Subsidies",
        "url": "https://coconutboard.gov.in/",
        "scheme_url": "https://coconutboard.gov.in/schemes.aspx",
        "type": "Board"
    },
    {
        "id": "BD_SPICES",
        "name": "Spices Board India (Kochi, Kerala)",
        "level": "Commodity Board",
        "category": "Spices Schemes (Cardamom, Pepper, Ginger)",
        "url": "https://indianspices.com/",
        "scheme_url": "https://indianspices.com/schemes",
        "type": "Board"
    },
    {
        "id": "BD_NABARD",
        "name": "NABARD Kerala Regional Office Programmes",
        "level": "Central/Financial",
        "category": "Refinance, RIDF, FPO Support",
        "url": "https://nabard.org/",
        "scheme_url": "https://nabard.org/",
        "type": "Development Bank"
    }
]


def test_source(source):
    url = source["url"]
    start_time = time.time()
    result = {
        "id": source["id"],
        "name": source["name"],
        "url": url,
        "level": source["level"],
        "category": source["category"],
        "type": source["type"],
        "accessible": False,
        "status_code": None,
        "response_time_ms": None,
        "ssl_verified": True,
        "content_type": None,
        "notes": "",
        "error": None,
    }

    # First attempt: standard HTTPS with SSL verification
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, verify=True, allow_redirects=True)
        result["accessible"] = (resp.status_code == 200 or resp.status_code < 400)
        result["status_code"] = resp.status_code
        result["content_type"] = resp.headers.get("Content-Type", "")
        result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
        result["notes"] = f"Accessible (HTTP {resp.status_code})"
        return result
    except requests.exceptions.SSLError as ssl_err:
        result["ssl_verified"] = False
        # Retry with verify=False (common for NIC/State certificates on Windows)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12, verify=False, allow_redirects=True)
            result["accessible"] = (resp.status_code == 200 or resp.status_code < 400)
            result["status_code"] = resp.status_code
            result["content_type"] = resp.headers.get("Content-Type", "")
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
            result["notes"] = f"Accessible with SSL bypass (Custom NIC/State CA) - HTTP {resp.status_code}"
            return result
        except Exception as retry_err:
            result["error"] = f"SSL Error and bypass failed: {str(retry_err)[:150]}"
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
            return result
    except requests.exceptions.Timeout:
        result["error"] = "Connection Timeout (>12s)"
        result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
        return result
    except requests.exceptions.ConnectionError as conn_err:
        result["error"] = f"Connection Error: {str(conn_err)[:150]}"
        result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
        return result
    except Exception as e:
        result["error"] = f"Unexpected Error: {str(e)[:150]}"
        result["response_time_ms"] = round((time.time() - start_time) * 1000, 1)
        return result


def main():
    print("=" * 80)
    print("STAGE 1: Official Source Inspection for KrishiMitra AI")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Total Sources to Test: {len(SOURCES_TO_INSPECT)}")
    print("=" * 80)

    results = []
    accessible_count = 0
    ssl_bypass_needed_count = 0
    inaccessible_count = 0

    for idx, src in enumerate(SOURCES_TO_INSPECT, start=1):
        print(f"[{idx:02d}/{len(SOURCES_TO_INSPECT)}] Testing {src['name']} ({src['url']})...", end=" ", flush=True)
        res = test_source(src)
        results.append(res)
        if res["accessible"]:
            accessible_count += 1
            if not res["ssl_verified"]:
                ssl_bypass_needed_count += 1
                print(f"[OK - SSL Bypass] HTTP {res['status_code']} ({res['response_time_ms']} ms)")
            else:
                print(f"[OK] HTTP {res['status_code']} ({res['response_time_ms']} ms)")
        else:
            inaccessible_count += 1
            print(f"[FAILED] {res['error']}")

    print("\n" + "=" * 80)
    print(f"INSPECTION SUMMARY:")
    print(f"  Total Sources: {len(SOURCES_TO_INSPECT)}")
    print(f"  Accessible: {accessible_count} ({accessible_count / len(SOURCES_TO_INSPECT) * 100:.1f}%)")
    print(f"  Accessible via Custom SSL Bypass: {ssl_bypass_needed_count}")
    print(f"  Inaccessible / Blocked / Down: {inaccessible_count}")
    print("=" * 80)

    # Save results to JSON file
    out_path = "source_inspection_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "inspected_at": datetime.now(timezone.utc).isoformat(),
            "total_inspected": len(SOURCES_TO_INSPECT),
            "accessible_count": accessible_count,
            "ssl_bypass_needed_count": ssl_bypass_needed_count,
            "inaccessible_count": inaccessible_count,
            "sources": results
        }, f, indent=2)

    print(f"Detailed inspection results saved to: {out_path}")


if __name__ == "__main__":
    main()
