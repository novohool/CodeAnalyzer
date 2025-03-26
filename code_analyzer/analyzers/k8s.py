"""Kubernetes analyzer module."""

from pathlib import Path
from typing import Dict, Any, List
import yaml

from .base import BaseAnalyzer

class K8sAnalyzer(BaseAnalyzer):
    """Analyzes Kubernetes configurations."""

    def analyze(self) -> Dict[str, Any]:
        """Analyze Kubernetes configurations.
        
        Returns:
            Dict containing K8s analysis results
        """
        k8s_configs = self._analyze_k8s_configs()
        return {'k8s': k8s_configs}
    
    def _analyze_k8s_configs(self) -> List[Dict[str, Any]]:
        """Analyze Kubernetes configuration files."""
        configs = []
        for file in self.repo_path.rglob('*.y*ml'):
            if self._is_k8s_file(file):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            config = {
                                'file': str(file),
                                'kind': data.get('kind', 'Unknown'),
                                'name': data.get('metadata', {}).get('name', 'Unknown'),
                                'namespace': data.get('metadata', {}).get('namespace', 'default')
                            }
                            configs.append(config)
                except Exception:
                    continue
        return configs
    
    def _is_k8s_file(self, file: Path) -> bool:
        """Check if file is a Kubernetes configuration."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'apiVersion:' in content and 'kind:' in content
        except Exception:
            return False 