"""Dependency analyzer module."""

from pathlib import Path
from typing import Dict, Any
import json

from .base import BaseAnalyzer

class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes project dependencies."""

    def analyze(self) -> Dict[str, Any]:
        """Analyze project dependencies.
        
        Returns:
            Dict containing dependency analysis results
        """
        dependencies = {
            'python': self._analyze_python_deps(),
            'node': self._analyze_node_deps()
        }
        return {'dependencies': dependencies}
    
    def _analyze_python_deps(self) -> Dict[str, str]:
        """Analyze Python dependencies from requirements.txt."""
        deps = {}
        req_file = self.repo_path / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        name = line.split('==')[0] if '==' in line else line
                        version = line.split('==')[1] if '==' in line else 'latest'
                        deps[name] = version
        return deps
    
    def _analyze_node_deps(self) -> Dict[str, Dict[str, str]]:
        """Analyze Node.js dependencies from package.json."""
        deps = {'dependencies': {}, 'devDependencies': {}}
        pkg_file = self.repo_path / 'package.json'
        if pkg_file.exists():
            with open(pkg_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    deps['dependencies'] = data.get('dependencies', {})
                    deps['devDependencies'] = data.get('devDependencies', {})
                except json.JSONDecodeError:
                    pass
        return deps 