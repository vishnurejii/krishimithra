"""
Comprehensive Coverage Report Generator for KrishiMitra AI.
Calculates department-wise, district-wise, and classification-wise coverage,
distinguishing collected vs. pending data without fabrication.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from registry.source_registry import SourceRegistry
from registry.coverage_matrix import SchemeCoverageMatrix

def main():
    registry = SourceRegistry()
    matrix_engine = SchemeCoverageMatrix(registry)
    md_content = matrix_engine.generate_markdown_report()

    report_path = Path(__file__).resolve().parent.parent / "COVERAGE_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Coverage report generated at: {report_path}")

if __name__ == "__main__":
    main()
