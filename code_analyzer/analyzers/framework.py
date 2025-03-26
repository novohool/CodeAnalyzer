"""Framework analyzer module."""

from pathlib import Path
from typing import Dict, Any
import json

from .base import BaseAnalyzer

class FrameworkAnalyzer(BaseAnalyzer):
    """Analyzes project frameworks."""

    def analyze(self) -> Dict[str, Any]:
        """Analyze project frameworks.
        
        Returns:
            Dict containing framework analysis results
        """
        frameworks = {
            'frontend': self._analyze_frontend_framework(),
            'backend': self._analyze_backend_framework()
        }
        return {'frameworks': frameworks}
    
    def _analyze_frontend_framework(self) -> Dict[str, str]:
        """Analyze frontend framework from package.json."""
        framework = {'name': None, 'version': None}
        pkg_file = self.repo_path / 'package.json'
        if pkg_file.exists():
            with open(pkg_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    if 'react' in deps:
                        framework['name'] = 'React'
                        framework['version'] = deps['react']
                    elif 'vue' in deps:
                        framework['name'] = 'Vue'
                        framework['version'] = deps['vue']
                except json.JSONDecodeError:
                    pass
        return framework
    
    def _analyze_backend_framework(self) -> Dict[str, str]:
        """Analyze backend framework from requirements.txt."""
        framework = {'name': None, 'version': None}
        req_file = self.repo_path / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if 'fastapi' in line.lower():
                        framework['name'] = 'FastAPI'
                        framework['version'] = line.split('==')[1] if '==' in line else 'latest'
                        break
                    elif 'flask' in line.lower():
                        framework['name'] = 'Flask'
                        framework['version'] = line.split('==')[1] if '==' in line else 'latest'
                        break
        return framework 