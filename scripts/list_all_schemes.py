import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import get_connection

def list_schemes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            s.id,
            s.name,
            d.name as dept_name,
            s.classification,
            s.level,
            s.objective,
            s.official_portal_url,
            b.benefit_type,
            b.subsidy_percentage,
            b.subsidy_amount,
            b.max_assistance_limit,
            b.description as benefit_desc,
            e.eligible_farmer_types,
            e.caste_category,
            e.min_land_acres,
            e.max_land_acres,
            COUNT(DISTINCT doc.id) as doc_count,
            STRING_AGG(DISTINCT c.crop_name, ', ') as crops
        FROM schemes s
        JOIN government_departments d ON s.department_id = d.id
        LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
        LEFT JOIN scheme_eligibility e ON s.id = e.scheme_id
        LEFT JOIN scheme_documents doc ON s.id = doc.scheme_id
        LEFT JOIN scheme_crops c ON s.id = c.scheme_id
        GROUP BY s.id, s.name, d.name, s.classification, s.level, s.objective, s.official_portal_url,
                 b.benefit_type, b.subsidy_percentage, b.subsidy_amount, b.max_assistance_limit, b.description,
                 e.eligible_farmer_types, e.caste_category, e.min_land_acres, e.max_land_acres
        ORDER BY d.name, s.name;
    """)
    rows = cur.fetchall()
    
    by_dept = {}
    for r in rows:
        dept = r["dept_name"]
        if dept not in by_dept:
            by_dept[dept] = []
        by_dept[dept].append({
            "id": r["id"],
            "name": r["name"],
            "classification": r["classification"],
            "level": r["level"],
            "objective": r["objective"],
            "portal": r["official_portal_url"],
            "benefit_type": r["benefit_type"],
            "subsidy_pct": float(r["subsidy_percentage"]) if r["subsidy_percentage"] else None,
            "subsidy_amt": float(r["subsidy_amount"]) if r["subsidy_amount"] else None,
            "max_limit": float(r["max_assistance_limit"]) if r["max_assistance_limit"] else None,
            "benefit_desc": r["benefit_desc"],
            "farmer_types": r["eligible_farmer_types"],
            "caste": r["caste_category"],
            "min_land": float(r["min_land_acres"]) if r["min_land_acres"] is not None else None,
            "max_land": float(r["max_land_acres"]) if r["max_land_acres"] is not None else None,
            "doc_count": r["doc_count"],
            "crops": r["crops"] or "All / General"
        })
    
    total = sum(len(v) for v in by_dept.values())
    print(f"TOTAL SCHEMES FOUND & INDEXED: {total} across {len(by_dept)} Departments/Boards\n")
    
    # Save as JSON for clean programmatic review if needed
    with open("storage/all_extracted_schemes.json", "w", encoding="utf-8") as f:
        json.dump(by_dept, f, indent=2, ensure_ascii=False)

    for dept, schemes in by_dept.items():
        print(f"============================================================")
        print(f"DEPARTMENT / BOARD: {dept} ({len(schemes)} Schemes)")
        print(f"============================================================")
        for s in schemes:
            pct_str = f"{s['subsidy_pct']:.1f}%" if s['subsidy_pct'] else ""
            amt_str = f"Rs. {s['subsidy_amt']:,.0f}" if s['subsidy_amt'] else ""
            fin_info = " / ".join(filter(None, [pct_str, amt_str]))
            if not fin_info:
                fin_info = s['benefit_type'] or "Financial / Technical Assistance"
            
            land_info = []
            if s['min_land'] is not None and s['min_land'] > 0:
                land_info.append(f"Min {s['min_land']} Ac")
            if s['max_land'] is not None and s['max_land'] < 999:
                land_info.append(f"Max {s['max_land']} Ac")
            land_str = ", ".join(land_info) if land_info else "No land limit"

            types_str = ", ".join(s['farmer_types']) if s['farmer_types'] else "All Farmers"
            if s['caste'] and s['caste'] != "General":
                types_str += f" ({s['caste']})"

            print(f"  * {s['name']}")
            print(f"    - Type: {s['classification']} | Level: {s['level']}")
            print(f"    - Financial Benefit: {fin_info}")
            if s['benefit_desc']:
                print(f"    - Benefit Details: {s['benefit_desc']}")
            print(f"    - Eligible Crops: {s['crops']}")
            print(f"    - Eligibility: {types_str} | Land: {land_str}")
            print(f"    - Official Portal: {s['portal']}")
            print(f"    - Downloaded Documents Attached: {s['doc_count']} doc(s)")
            print()

if __name__ == "__main__":
    list_schemes()
