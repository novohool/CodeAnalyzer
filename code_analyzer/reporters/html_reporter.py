"""HTML report generator."""

import os
from typing import Dict, Any
from pathlib import Path
import json

class HTMLReporter:
    """Generates HTML reports from analysis results."""
    
    def __init__(self, output_dir: str = "docs"):
        """Initialize HTML reporter.
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = Path(output_dir)
        
    def generate(self, results: Dict[str, Any]) -> None:
        """Generate HTML report from results.
        
        Args:
            results: Analysis results to report
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = self.output_dir / "analysis_report.html"
        
        # Convert results to dictionary if needed
        if hasattr(results, 'to_dict'):
            results = results.to_dict()
            
        html = self._generate_html(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
    def _generate_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML content.
        
        Args:
            results: Analysis results
            
        Returns:
            HTML content as string
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #333;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        pre {{
            background: #f8f8f8;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Analysis Report</h1>
        
        {self._generate_sections(results)}
    </div>
    
    <script>
        // Add any interactive features here
        console.log('Report loaded');
    </script>
</body>
</html>
"""
            
    def _generate_sections(self, results: Dict[str, Any]) -> str:
        """Generate HTML for each section.
        
        Args:
            results: Analysis results
            
        Returns:
            HTML content for sections
        """
        sections = []
        
        for section, data in results.items():
            if not data:
                continue
                
            sections.append(f"""
            <div class="section">
                <h2>{section.title()}</h2>
                <pre>{json.dumps(data, indent=2)}</pre>
            </div>
            """)
            
        return '\n'.join(sections) 