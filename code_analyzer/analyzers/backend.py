"""Backend analyzer module."""

from pathlib import Path
from typing import Dict, Any, List
import ast
import re

from .base import BaseAnalyzer

class BackendAnalyzer(BaseAnalyzer):
    """Analyzes backend code and APIs."""
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze backend code.
        
        Returns:
            Dict containing backend analysis results
        """
        results = {
            'endpoints': self._analyze_endpoints(),
            'models': self._analyze_models(),
            'services': self._analyze_services(),
            'database': self._analyze_database()
        }
        return {'backend': results}
    
    def _analyze_endpoints(self) -> List[Dict[str, Any]]:
        """Analyze API endpoints."""
        endpoints = []
        for file in self.repo_path.rglob('*.py'):
            try:
                content = file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                endpoints.extend(self._extract_endpoints(tree, file))
            except Exception:
                continue
        return endpoints
    
    def _extract_endpoints(self, tree: ast.AST, file: Path) -> List[Dict[str, Any]]:
        """Extract API endpoints from AST."""
        endpoints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                endpoint = self._extract_endpoint_info(node, file)
                if endpoint:
                    endpoints.append(endpoint)
        return endpoints
    
    def _extract_endpoint_info(self, node: ast.FunctionDef, file: Path) -> Dict[str, Any]:
        """Extract endpoint information from function definition."""
        for decorator in node.decorator_list:
            if self._is_route_decorator(decorator):
                return {
                    'path': self._get_route_path(decorator),
                    'method': self._get_http_method(decorator),
                    'function': node.name,
                    'file': str(file.relative_to(self.repo_path)),
                    'params': self._extract_params(node),
                    'response': self._extract_response_type(node),
                    'auth': self._has_auth_decorator(node)
                }
        return None
    
    def _analyze_models(self) -> List[Dict[str, Any]]:
        """Analyze data models."""
        models = []
        for file in self.repo_path.rglob('*.py'):
            if not self._is_model_file(file):
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                models.extend(self._extract_models(tree, file))
            except Exception:
                continue
        return models
    
    def _extract_models(self, tree: ast.AST, file: Path) -> List[Dict[str, Any]]:
        """Extract model definitions from AST."""
        models = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                model = self._extract_model_info(node, file)
                if model:
                    models.append(model)
        return models
    
    def _extract_model_info(self, node: ast.ClassDef, file: Path) -> Dict[str, Any]:
        """Extract model information from class definition."""
        if self._is_model_class(node):
            return {
                'name': node.name,
                'file': str(file.relative_to(self.repo_path)),
                'fields': self._extract_model_fields(node),
                'relationships': self._extract_relationships(node),
                'methods': self._extract_model_methods(node)
            }
        return None
    
    def _analyze_services(self) -> List[Dict[str, Any]]:
        """Analyze service layer."""
        services = []
        for file in self.repo_path.rglob('*.py'):
            if not self._is_service_file(file):
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                services.extend(self._extract_services(tree, file))
            except Exception:
                continue
        return services
    
    def _extract_services(self, tree: ast.AST, file: Path) -> List[Dict[str, Any]]:
        """Extract service definitions from AST."""
        services = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                service = self._extract_service_info(node, file)
                if service:
                    services.append(service)
        return services
    
    def _extract_service_info(self, node: ast.ClassDef, file: Path) -> Dict[str, Any]:
        """Extract service information from class definition."""
        if self._is_service_class(node):
            return {
                'name': node.name,
                'file': str(file.relative_to(self.repo_path)),
                'methods': self._extract_service_methods(node),
                'dependencies': self._extract_dependencies(node)
            }
        return None
    
    def _analyze_database(self) -> Dict[str, Any]:
        """Analyze database configuration and usage."""
        database = {
            'engine': self._detect_database_engine(),
            'models': self._get_database_models(),
            'migrations': self._get_migrations()
        }
        return database
    
    def _detect_database_engine(self) -> str:
        """Detect database engine from configuration."""
        # Check common database configuration files
        config_files = [
            'config.py',
            'settings.py',
            'database.py',
            '.env'
        ]
        
        for file in config_files:
            try:
                content = (self.repo_path / file).read_text()
                if 'postgresql' in content.lower():
                    return 'postgresql'
                elif 'mysql' in content.lower():
                    return 'mysql'
                elif 'sqlite' in content.lower():
                    return 'sqlite'
            except:
                continue
                
        return 'unknown'
    
    def _get_database_models(self) -> List[Dict[str, Any]]:
        """Get all database models."""
        models = []
        for file in self.repo_path.rglob('*.py'):
            if not self._is_model_file(file):
                continue
                
            try:
                content = file.read_text()
                if 'SQLAlchemy' in content or 'Base.metadata' in content:
                    tree = ast.parse(content)
                    models.extend(self._extract_sqlalchemy_models(tree, file))
            except:
                continue
        return models
    
    def _get_migrations(self) -> List[Dict[str, Any]]:
        """Get database migration information."""
        migrations = []
        migration_dir = self.repo_path / 'migrations'
        
        if not migration_dir.exists():
            return migrations
            
        for file in migration_dir.rglob('*.py'):
            if 'env.py' in str(file):
                continue
                
            try:
                content = file.read_text()
                migrations.append({
                    'file': str(file.relative_to(self.repo_path)),
                    'revision': self._extract_migration_revision(content),
                    'operations': self._extract_migration_operations(content)
                })
            except:
                continue
                
        return migrations
    
    def _is_model_file(self, file: Path) -> bool:
        """Check if file contains data models."""
        return ('model' in file.name.lower() or
                'schema' in file.name.lower())
    
    def _is_service_file(self, file: Path) -> bool:
        """Check if file contains services."""
        return ('service' in file.name.lower() or
                'repository' in file.name.lower())
                
    def _is_model_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a data model."""
        return any(base.id in ['Model', 'BaseModel'] 
                  for base in node.bases 
                  if isinstance(base, ast.Name))
                  
    def _is_service_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a service."""
        return ('Service' in node.name or
                'Repository' in node.name) 