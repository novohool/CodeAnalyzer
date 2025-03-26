"""Text reporter module."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, TextIO

from .base import BaseReporter
from ..models.analysis import AnalysisResults

class TextReporter(BaseReporter):
    """Text report generator."""
    
    def generate(self, results: AnalysisResults) -> None:
        """Generate text report from analysis results.
        
        Args:
            results: Analysis results to generate report from
        """
        self._ensure_output_dir()
        
        report_path = self.output_dir / 'analysis_report.txt'
        with report_path.open('w') as f:
            self._write_header(f, results)
            self._write_metrics(f, results.metrics)
            self._write_issues(f, results.issues)
            self._write_suggestions(f, results.suggestions)
            self._write_test_info(f, results)
    
    def _write_header(self, f: TextIO, results: AnalysisResults) -> None:
        """Write report header.
        
        Args:
            f: File to write to
            results: Analysis results
        """
        f.write('=' * 80 + '\n')
        f.write('CODE ANALYSIS REPORT\n')
        f.write('=' * 80 + '\n\n')
        
        f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'Repository: {results.repository}\n\n')
    
    def _write_metrics(self, f: TextIO, metrics: Dict[str, Any]) -> None:
        """Write metrics section.
        
        Args:
            f: File to write to
            metrics: Metrics data
        """
        f.write('-' * 80 + '\n')
        f.write('METRICS\n')
        f.write('-' * 80 + '\n\n')
        
        formatted = self._format_metrics(metrics)
        self._write_dict(f, formatted, indent=0)
        f.write('\n')
    
    def _write_issues(self, f: TextIO, issues: List[Dict[str, Any]]) -> None:
        """Write issues section.
        
        Args:
            f: File to write to
            issues: List of issues
        """
        f.write('-' * 80 + '\n')
        f.write('ISSUES\n')
        f.write('-' * 80 + '\n\n')
        
        if not issues:
            f.write('No issues found.\n\n')
            return
        
        grouped = self._group_issues(issues)
        for severity in ['high', 'medium', 'low']:
            if grouped[severity]:
                f.write(f'{severity.upper()} Severity Issues:\n')
                f.write('-' * 20 + '\n')
                
                for issue in grouped[severity]:
                    f.write(f"- {issue['message']}\n")
                    if 'file' in issue:
                        f.write(f"  File: {issue['file']}\n")
                    if 'line' in issue:
                        f.write(f"  Line: {issue['line']}\n")
                    f.write('\n')
    
    def _write_suggestions(self, f: TextIO, suggestions: List[str]) -> None:
        """Write suggestions section.
        
        Args:
            f: File to write to
            suggestions: List of suggestions
        """
        f.write('-' * 80 + '\n')
        f.write('SUGGESTIONS\n')
        f.write('-' * 80 + '\n\n')
        
        if not suggestions:
            f.write('No suggestions available.\n\n')
            return
        
        for suggestion in suggestions:
            f.write(f'- {suggestion}\n')
        f.write('\n')
    
    def _write_test_info(self, f: TextIO, results: AnalysisResults) -> None:
        """Write test information section.
        
        Args:
            f: File to write to
            results: Analysis results
        """
        f.write('-' * 80 + '\n')
        f.write('TEST INFORMATION\n')
        f.write('-' * 80 + '\n\n')
        
        if results.test_info:
            f.write(f'Total Tests: {results.test_info.total_tests}\n')
            f.write(f'Passed Tests: {results.test_info.passed_tests}\n')
            f.write(f'Failed Tests: {results.test_info.failed_tests}\n')
            f.write(f'Skipped Tests: {results.test_info.skipped_tests}\n')
            f.write(f'Test Duration: {results.test_info.duration:.2f}s\n\n')
        
        if results.coverage:
            f.write('Coverage Information:\n')
            f.write(f'Line Coverage: {results.coverage.line_coverage:.1f}%\n')
            f.write(f'Branch Coverage: {results.coverage.branch_coverage:.1f}%\n')
            f.write(f'Function Coverage: {results.coverage.function_coverage:.1f}%\n')
        else:
            f.write('No test coverage information available.\n')
    
    def _write_dict(self, f: TextIO, data: Dict[str, Any], indent: int = 0) -> None:
        """Write dictionary data with indentation.
        
        Args:
            f: File to write to
            data: Dictionary to write
            indent: Indentation level
        """
        for key, value in data.items():
            if isinstance(value, dict):
                f.write(' ' * indent + f'{key}:\n')
                self._write_dict(f, value, indent + 2)
            else:
                f.write(' ' * indent + f'{key}: {value}\n') 