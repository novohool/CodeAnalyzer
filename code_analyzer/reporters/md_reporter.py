"""Markdown report generator."""

import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

class MarkdownReporter:
    """Generates Markdown reports from analysis results."""
    
    def __init__(self, output_dir: str = "docs"):
        """Initialize Markdown reporter.
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = Path(output_dir)
        
    def generate(self, results: Dict[str, Any]) -> None:
        """Generate Markdown report from results.
        
        Args:
            results: Analysis results to report
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = self.output_dir / "analysis_report.md"
        
        # Convert results to dictionary if needed
        if hasattr(results, 'to_dict'):
            results = results.to_dict()
            
        markdown = self._generate_markdown(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
    def _generate_markdown(self, results: Dict[str, Any]) -> str:
        """Generate Markdown content.
        
        Args:
            results: Analysis results
            
        Returns:
            Markdown content as string
        """
        sections = [
            "# Code Analysis Report\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]
        
        # Add sections
        for section, data in results.items():
            if not data:
                continue
                
            sections.extend([
                f"\n## {section.title()}\n",
                self._format_section(data)
            ])
            
        return '\n'.join(sections)
    
    def _format_section(self, data: Any) -> str:
        """Format section data as Markdown.
        
        Args:
            data: Section data to format
            
        Returns:
            Formatted Markdown string
        """
        if isinstance(data, dict):
            return self._format_dict(data)
        elif isinstance(data, list):
            return self._format_list(data)
        else:
            return f"{data}\n"
            
    def _format_dict(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary as Markdown.
        
        Args:
            data: Dictionary to format
            indent: Indentation level
            
        Returns:
            Formatted Markdown string
        """
        lines = []
        prefix = '  ' * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}- **{key}**:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}- **{key}**:")
                lines.append(self._format_list(value, indent + 1))
            else:
                lines.append(f"{prefix}- **{key}**: {value}")
                
        return '\n'.join(lines)
        
    def _format_list(self, data: list, indent: int = 0) -> str:
        """Format list as Markdown.
        
        Args:
            data: List to format
            indent: Indentation level
            
        Returns:
            Formatted Markdown string
        """
        lines = []
        prefix = '  ' * indent
        
        for item in data:
            if isinstance(item, dict):
                lines.append(self._format_dict(item, indent))
            elif isinstance(item, list):
                lines.append(self._format_list(item, indent))
            else:
                lines.append(f"{prefix}- {item}")
                
        return '\n'.join(lines) 