"""Base analyzer class for code analysis."""

from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from ..models.project import (
    AnalysisResults,
    CodeMetrics,
    Frameworks,
    IssueInfo,
    ProjectInfo,
    ProjectStructure,
    SuggestionInfo,
    TestInfo,
    TestCoverage
)

class BaseAnalyzer(ABC):
    """Base class for all code analyzers."""

    def __init__(self, repo_path: Union[str, Path], config: Optional[Dict] = None):
        """Initialize the analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            config: Optional configuration dictionary
        """
        self.repo_path = Path(repo_path)
        self.config = config or {}
        
        # Initialize results containers
        self.project_info = ProjectInfo(name=self.repo_path.name)
        self.structure = ProjectStructure(root=str(self.repo_path))
        self.frameworks = Frameworks()
        self.metrics = CodeMetrics()
        self.test_info = TestInfo()
        self.test_coverage = TestCoverage()
        self._issues: List[IssueInfo] = []
        self._suggestions: List[SuggestionInfo] = []

    def add_issue(self, severity: str, message: str, file: Optional[str] = None,
                 line: Optional[int] = None, column: Optional[int] = None) -> None:
        """Add an issue to the analysis results.
        
        Args:
            severity: Issue severity level
            message: Description of the issue
            file: Optional file path where the issue was found
            line: Optional line number
            column: Optional column number
        """
        issue = IssueInfo(
            severity=severity,
            message=message,
            file=file,
            line=line,
            column=column
        )
        self._issues.append(issue)

    def add_suggestion(self, category: str, suggestion: str, 
                      priority: str = 'medium', file: Optional[str] = None) -> None:
        """Add a suggestion to the analysis results.
        
        Args:
            category: Type of suggestion
            suggestion: The actual suggestion text
            priority: Suggestion priority level
            file: Optional file path the suggestion relates to
        """
        suggestion_info = SuggestionInfo(
            category=category,
            suggestion=suggestion,
            priority=priority,
            file=file
        )
        self._suggestions.append(suggestion_info)

    def get_results(self) -> AnalysisResults:
        """Get the complete analysis results.
        
        Returns:
            AnalysisResults object containing all analysis data
        """
        return AnalysisResults(
            project_info=self.project_info,
            structure=self.structure,
            frameworks=self.frameworks,
            metrics=self.metrics,
            test_info=self.test_info,
            test_coverage=self.test_coverage,
            issues=self._issues,
            suggestions=self._suggestions
        )

    def _is_excluded_path(self, path: Union[str, Path]) -> bool:
        """Check if a path should be excluded from analysis.
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be excluded, False otherwise
        """
        path_str = str(path)
        exclude_patterns = self.config.get('exclude_patterns', [])
        return any(pattern in path_str for pattern in exclude_patterns)

    def _is_valid_file_size(self, file_path: Union[str, Path]) -> bool:
        """Check if a file's size is within acceptable limits.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file size is acceptable, False otherwise
        """
        max_size = self.config.get('max_file_size_mb', 10) * 1024 * 1024  # Convert to bytes
        return Path(file_path).stat().st_size <= max_size

    @abstractmethod
    def analyze(self) -> None:
        """Perform the analysis. Must be implemented by subclasses."""
        pass

    def get_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get issues found during analysis.
        
        Returns:
            Dictionary mapping severity to list of issues
        """
        return {
            'high': [],
            'medium': [],
            'low': []
        }

    def get_suggestions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get suggestions for improvements.
        
        Returns:
            Dictionary mapping category to list of suggestions
        """
        return {
            'code_quality': [],
            'performance': [],
            'security': [],
            'maintainability': []
        }

    def _get_file_content(self, file_path: Path) -> str:
        """Read and return file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
        """
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return "" 