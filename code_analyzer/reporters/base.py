"""Base reporter module."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from ..models.analysis import AnalysisResults

class BaseReporter(ABC):
    """Base class for all reporters."""

    def __init__(self, output_dir: str):
        """Initialize reporter.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
    
    @abstractmethod
    def generate(self, results: AnalysisResults) -> None:
        """Generate report from analysis results.
        
        Args:
            results: Analysis results to generate report from
        """
        pass
    
    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format metrics for display.
        
        Args:
            metrics: Raw metrics data
            
        Returns:
            Formatted metrics
        """
        formatted = {}
        
        for key, value in metrics.items():
            if isinstance(value, float):
                formatted[key] = f"{value:.2f}"
            elif isinstance(value, (int, str)):
                formatted[key] = str(value)
            elif isinstance(value, dict):
                formatted[key] = self._format_metrics(value)
            else:
                formatted[key] = value
        
        return formatted
    
    def _format_file_size(self, size_in_bytes: int) -> str:
        """Format file size for display.
        
        Args:
            size_in_bytes: File size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"
    
    def _format_complexity(self, complexity: int) -> str:
        """Format complexity score with category.
        
        Args:
            complexity: Complexity score
            
        Returns:
            Formatted complexity string
        """
        if complexity <= 5:
            return f"{complexity} (Low)"
        elif complexity <= 10:
            return f"{complexity} (Medium)"
        else:
            return f"{complexity} (High)"
    
    def _format_maintainability(self, score: float) -> str:
        """Format maintainability score with category.
        
        Args:
            score: Maintainability score
            
        Returns:
            Formatted maintainability string
        """
        if score >= 80:
            return f"{score:.1f} (Good)"
        elif score >= 60:
            return f"{score:.1f} (Fair)"
        else:
            return f"{score:.1f} (Poor)" 