"""Structure analyzer module."""

from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from .base import BaseAnalyzer

class StructureAnalyzer(BaseAnalyzer):
    """Analyzes project structure."""

    def analyze(self) -> Dict[str, Any]:
        """Analyze project structure.
        
        Returns:
            Dict containing structure analysis results
        """
        structure = {
            'directories': self._analyze_directories(),
            'file_types': self._analyze_file_types(),
            'special_files': self._analyze_special_files()
        }
        return {'structure': structure}
    
    def _analyze_directories(self) -> Dict[str, List[str]]:
        """Analyze directory structure."""
        dirs = defaultdict(list)
        for file in self.repo_path.rglob('*'):
            if file.is_file():
                rel_path = str(file.relative_to(self.repo_path))
                parent = str(file.parent.relative_to(self.repo_path))
                dirs[parent].append(file.name)
        return dict(dirs)
    
    def _analyze_file_types(self) -> Dict[str, int]:
        """Analyze file types distribution."""
        types = defaultdict(int)
        for file in self.repo_path.rglob('*'):
            if file.is_file():
                ext = file.suffix.lower() or '(no extension)'
                types[ext] += 1
        return dict(types)
    
    def _analyze_special_files(self) -> Dict[str, List[str]]:
        """Analyze special configuration files."""
        special_files = {
            'config': [],
            'test': [],
            'documentation': []
        }
        
        for file in self.repo_path.rglob('*'):
            if file.is_file():
                name = file.name.lower()
                if name in ['config.py', 'settings.py', '.env']:
                    special_files['config'].append(str(file.relative_to(self.repo_path)))
                elif name.startswith('test_') or name.endswith('_test.py'):
                    special_files['test'].append(str(file.relative_to(self.repo_path)))
                elif name.endswith(('.md', '.rst', '.txt')):
                    special_files['documentation'].append(str(file.relative_to(self.repo_path)))
        
        return special_files 