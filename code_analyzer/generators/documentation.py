"""Documentation generator module."""

from pathlib import Path
from typing import Dict, Any, List
import json

class DocumentationGenerator:
    """Generates documentation from analysis results."""
    
    def __init__(self, output_dir: str = "docs"):
        """Initialize generator.
        
        Args:
            output_dir: Output directory for documentation
        """
        self.output_dir = Path(output_dir)
        
    def generate(self, results: Dict[str, Any]) -> None:
        """Generate documentation from analysis results.
        
        Args:
            results: Analysis results to document
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate different documentation sections
        self._generate_overview(results)
        self._generate_api_docs(results)
        self._generate_architecture_docs(results)
        self._generate_deployment_docs(results)
        
    def _generate_overview(self, results: Dict[str, Any]) -> None:
        """Generate project overview documentation."""
        overview = {
            'project_structure': results.get('structure', {}),
            'frameworks': results.get('framework', {}),
            'dependencies': results.get('dependency', {})
        }
        
        with open(self.output_dir / 'overview.json', 'w') as f:
            json.dump(overview, f, indent=2)
            
    def _generate_api_docs(self, results: Dict[str, Any]) -> None:
        """Generate API documentation."""
        api_docs = {
            'endpoints': results.get('route', {}).get('api_routes', []),
            'models': results.get('route', {}).get('models', []),
            'websockets': results.get('route', {}).get('websocket_routes', [])
        }
        
        with open(self.output_dir / 'api_docs.json', 'w') as f:
            json.dump(api_docs, f, indent=2)
            
    def _generate_architecture_docs(self, results: Dict[str, Any]) -> None:
        """Generate architecture documentation."""
        architecture = {
            'frontend': results.get('frontend', {}),
            'backend': results.get('backend', {}),
            'components': results.get('structure', {}).get('components', [])
        }
        
        with open(self.output_dir / 'architecture.json', 'w') as f:
            json.dump(architecture, f, indent=2)
            
    def _generate_deployment_docs(self, results: Dict[str, Any]) -> None:
        """Generate deployment documentation."""
        deployment = {
            'kubernetes': results.get('k8s', {}),
            'environment': results.get('structure', {}).get('env_files', []),
            'configuration': results.get('structure', {}).get('config_files', [])
        }
        
        with open(self.output_dir / 'deployment.json', 'w') as f:
            json.dump(deployment, f, indent=2) 