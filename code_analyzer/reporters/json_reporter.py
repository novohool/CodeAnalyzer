"""JSON reporter module."""

import json
from pathlib import Path
from typing import Dict, Any

from .base import BaseReporter

class JsonReporter(BaseReporter):
    """JSON report generator."""

    def generate(self, results: Dict[str, Any]) -> None:
        """Generate JSON report from analysis results.
        
        Args:
            results: Analysis results to report
        """
        output_file = self.output_dir / "analysis_report.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results.to_dict(), f, indent=2, ensure_ascii=False) 