"""Main analyzer class that orchestrates the code analysis process."""

import os
from typing import Dict, Optional
from collections import defaultdict

from .config import DEFAULT_CONFIG
from .analyzers.frontend import FrontendAnalyzer
from .analyzers.backend import BackendAnalyzer
from .analyzers.k8s import K8sAnalyzer
from .analyzers.structure import StructureAnalyzer
from .generators.documentation import DocumentationGenerator
from .models.project import ProjectInfo
from .utils.file_utils import is_excluded_path

class CodeAnalyzer:
    """Main class for analyzing code repositories."""
    
    def __init__(self, repo_path: str, config: Optional[Dict] = None):
        """Initialize the code analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            config: Optional configuration to override defaults
        """
        self.repo_path = repo_path
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Initialize project info
        self.project_info = ProjectInfo(
            name=os.path.basename(repo_path),
            description='',
            version='',
            author='',
            license=''
        )
        
        # Initialize analyzers
        self.structure_analyzer = StructureAnalyzer(repo_path, self.config)
        self.frontend_analyzer = FrontendAnalyzer(repo_path, self.config)
        self.backend_analyzer = BackendAnalyzer(repo_path, self.config)
        self.k8s_analyzer = K8sAnalyzer(repo_path, self.config)
        
        # Initialize documentation generator
        self.doc_generator = DocumentationGenerator(self.config['output_dir'])
        
        # Analysis results
        self.results = {
            'project_info': self.project_info.dict(),
            'structure': {},
            'frontend': {},
            'backend': {},
            'k8s': {},
            'documentation': {}
        }
    
    def analyze_repository(self) -> Dict:
        """Analyze the entire repository.
        
        Returns:
            Dict containing all analysis results
        """
        # Analyze project structure
        self.results['structure'] = self.structure_analyzer.analyze()
        
        # Analyze frontend code
        if os.path.exists(os.path.join(self.repo_path, 'frontend')):
            self.results['frontend'] = self.frontend_analyzer.analyze()
        
        # Analyze backend code
        if os.path.exists(os.path.join(self.repo_path, 'backend')):
            self.results['backend'] = self.backend_analyzer.analyze()
        
        # Analyze K8s configurations
        self.results['k8s'] = self.k8s_analyzer.analyze()
        
        # Generate documentation
        self.results['documentation'] = self.doc_generator.generate(self.results)
        
        return self.results
    
    def save_documentation(self) -> None:
        """Save the generated documentation to files."""
        self.doc_generator.save(self.results)
    
    def get_summary(self) -> Dict:
        """Get a summary of the analysis results.
        
        Returns:
            Dict containing summary information
        """
        return {
            'project_name': self.project_info.name,
            'total_files': len(self.structure_analyzer.get_all_files()),
            'frontend_components': len(self.results.get('frontend', {}).get('components', [])),
            'backend_endpoints': len(self.results.get('backend', {}).get('endpoints', [])),
            'k8s_resources': len(self.results.get('k8s', {}).get('resources', [])),
            'documentation_files': len(self.results.get('documentation', {}).get('files', []))
        }
    
    def get_issues(self) -> Dict:
        """Get any issues found during analysis.
        
        Returns:
            Dict containing issues categorized by severity
        """
        issues = defaultdict(list)
        
        # Collect issues from all analyzers
        for analyzer in [self.frontend_analyzer, self.backend_analyzer, 
                        self.k8s_analyzer, self.structure_analyzer]:
            analyzer_issues = analyzer.get_issues()
            for severity, items in analyzer_issues.items():
                issues[severity].extend(items)
        
        return dict(issues)
    
    def get_suggestions(self) -> Dict:
        """Get suggestions for improvements.
        
        Returns:
            Dict containing improvement suggestions
        """
        suggestions = defaultdict(list)
        
        # Collect suggestions from all analyzers
        for analyzer in [self.frontend_analyzer, self.backend_analyzer,
                        self.k8s_analyzer, self.structure_analyzer]:
            analyzer_suggestions = analyzer.get_suggestions()
            for category, items in analyzer_suggestions.items():
                suggestions[category].extend(items)
        
        return dict(suggestions) 