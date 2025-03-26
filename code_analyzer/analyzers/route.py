"""Route analyzer module."""

import ast
import re
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseAnalyzer

class RouteAnalyzer(BaseAnalyzer):
    """Analyzes frontend and backend routes."""
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze routes in the project.
        
        Returns:
            Dictionary containing route analysis results
        """
        results = {
            'backend_routes': self._analyze_backend_routes(),
            'frontend_routes': self._analyze_frontend_routes()
        }
        return results
        
    def _analyze_backend_routes(self) -> List[Dict[str, Any]]:
        """Analyze backend API routes."""
        routes = []
        
        # Common API route patterns
        api_patterns = [
            '**/*.py',  # Python files
        ]
        
        for pattern in api_patterns:
            for file in self.repo_path.rglob(pattern):
                if self._is_excluded_path(file):
                    continue
                    
                try:
                    content = self._get_file_content(file)
                    file_routes = self._extract_backend_routes(file, content)
                    routes.extend(file_routes)
                except Exception as e:
                    print(f"Error analyzing routes in {file}: {str(e)}")
                    
        return routes
        
    def _analyze_frontend_routes(self) -> List[Dict[str, Any]]:
        """Analyze frontend routes."""
        routes = []
        
        # Common frontend route patterns
        frontend_patterns = [
            '**/router/**/*.{js,jsx,ts,tsx}',  # Router configuration files
            '**/routes/**/*.{js,jsx,ts,tsx}',  # Route definition files
            '**/pages/**/*.{js,jsx,ts,tsx}',   # Page components
            '**/views/**/*.{js,jsx,ts,tsx}',   # View components
            '**/App.{js,jsx,ts,tsx}',          # Main App file
            '**/router.{js,jsx,ts,tsx}'        # Router configuration
        ]
        
        for pattern in frontend_patterns:
            for file in self.repo_path.glob(pattern):
                if self._is_excluded_path(file):
                    continue
                    
                try:
                    content = self._get_file_content(file)
                    file_routes = self._extract_frontend_routes(file, content)
                    routes.extend(file_routes)
                except Exception as e:
                    print(f"Error analyzing routes in {file}: {str(e)}")
                    
        return routes
        
    def _extract_backend_routes(self, file: Path, content: str) -> List[Dict[str, Any]]:
        """Extract backend routes from file content."""
        routes = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    route_info = self._extract_route_info(node, file)
                    if route_info:
                        routes.append(route_info)
                        
        except Exception as e:
            print(f"Error parsing {file}: {str(e)}")
            
        return routes
        
    def _extract_route_info(self, node: ast.FunctionDef, file: Path) -> Dict[str, Any]:
        """Extract route information from function definition."""
        route_info = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    # Handle @app.route('/path')
                    if decorator.func.id in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                        route_info = self._create_route_info(decorator, node, file)
                elif isinstance(decorator.func, ast.Attribute):
                    # Handle @blueprint.route('/path')
                    if decorator.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                        route_info = self._create_route_info(decorator, node, file)
                        
        return route_info
        
    def _create_route_info(self, decorator: ast.Call, node: ast.FunctionDef, file: Path) -> Dict[str, Any]:
        """Create route information dictionary."""
        route_info = {
            'path': self._extract_route_path(decorator),
            'method': self._extract_http_method(decorator),
            'function': node.name,
            'file': str(file.relative_to(self.repo_path)),
            'description': ast.get_docstring(node) or '',
            'parameters': self._extract_parameters(node),
            'returns': self._extract_return_info(node),
            'auth_required': self._has_auth_decorator(node),
            'middleware': self._extract_middleware(node)
        }
        
        # Extract main functionality from docstring or function body
        route_info['functionality'] = self._extract_functionality(node)
        
        return route_info
        
    def _extract_frontend_routes(self, file: Path, content: str) -> List[Dict[str, Any]]:
        """Extract frontend routes from file content."""
        routes = []
        
        # React Router patterns
        react_route_pattern = r'<Route[^>]*path=[\'"](.*?)[\'"][^>]*component=\{(.*?)\}'
        react_router_pattern = r'{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*component:\s*(.+?)\s*}'
        
        # Vue Router patterns
        vue_route_pattern = r'{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*component:\s*(.+?)\s*}'
        
        # Find React Router routes
        for match in re.finditer(react_route_pattern, content):
            path, component = match.groups()
            routes.append({
                'path': path,
                'component': component.strip(),
                'type': 'react',
                'file': str(file.relative_to(self.repo_path)),
                'layout': self._extract_layout_info(content, component),
                'guards': self._extract_route_guards(content, path),
                'lazy_loading': self._is_lazy_loaded(content, component)
            })
            
        # Find React Router object style routes
        for match in re.finditer(react_router_pattern, content):
            path, component = match.groups()
            routes.append({
                'path': path,
                'component': component.strip(),
                'type': 'react',
                'file': str(file.relative_to(self.repo_path)),
                'layout': self._extract_layout_info(content, component),
                'guards': self._extract_route_guards(content, path),
                'lazy_loading': self._is_lazy_loaded(content, component)
            })
            
        # Find Vue Router routes
        for match in re.finditer(vue_route_pattern, content):
            path, component = match.groups()
            routes.append({
                'path': path,
                'component': component.strip(),
                'type': 'vue',
                'file': str(file.relative_to(self.repo_path)),
                'layout': self._extract_layout_info(content, component),
                'guards': self._extract_route_guards(content, path),
                'lazy_loading': self._is_lazy_loaded(content, component)
            })
            
        return routes
        
    def _extract_route_path(self, node: ast.Call) -> str:
        """Extract route path from decorator."""
        if node.args:
            if isinstance(node.args[0], ast.Str):
                return node.args[0].s
        for keyword in node.keywords:
            if keyword.arg == 'path' and isinstance(keyword.value, ast.Str):
                return keyword.value.s
        return ''
        
    def _extract_http_method(self, node: ast.Call) -> str:
        """Extract HTTP method from decorator."""
        if isinstance(node.func, ast.Name):
            method = node.func.id.upper()
            if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                return method
        elif isinstance(node.func, ast.Attribute):
            method = node.func.attr.upper()
            if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                return method
        for keyword in node.keywords:
            if keyword.arg == 'methods' and isinstance(keyword.value, (ast.List, ast.Tuple)):
                methods = [m.s for m in keyword.value.elts if isinstance(m, ast.Str)]
                return methods[0] if methods else 'GET'
        return 'GET'
        
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters."""
        params = []
        
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._extract_type_annotation(arg),
                'required': True
            }
            params.append(param_info)
            
        for arg in node.args.kwonlyargs:
            param_info = {
                'name': arg.arg,
                'type': self._extract_type_annotation(arg),
                'required': False
            }
            params.append(param_info)
            
        return params
        
    def _extract_return_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function return information."""
        returns = {
            'type': 'unknown',
            'description': ''
        }
        
        # Check return annotation
        if node.returns:
            returns['type'] = self._extract_type_annotation(node)
            
        # Check docstring for return info
        docstring = ast.get_docstring(node)
        if docstring:
            return_match = re.search(r'Returns:\s*(.+?)(?:\n\n|\Z)', docstring, re.DOTALL)
            if return_match:
                returns['description'] = return_match.group(1).strip()
                
        return returns
        
    def _extract_functionality(self, node: ast.FunctionDef) -> str:
        """Extract main functionality description."""
        # First try to get it from docstring
        docstring = ast.get_docstring(node)
        if docstring:
            # Get first paragraph of docstring
            desc = docstring.split('\n\n')[0].strip()
            if desc:
                return desc
                
        # If no docstring, try to analyze function body
        functionality = []
        
        for child in node.body:
            if isinstance(child, ast.Expr) and isinstance(child.value, ast.Str):
                continue  # Skip docstring
                
            if isinstance(child, (ast.Return, ast.Assign, ast.Expr)):
                functionality.append(self._analyze_node_functionality(child))
                
        return ' '.join(filter(None, functionality))
        
    def _analyze_node_functionality(self, node: ast.AST) -> str:
        """Analyze node to extract functionality description."""
        if isinstance(node, ast.Return):
            return "Returns response"
        elif isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                return f"Processes {node.targets[0].id}"
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                return f"Calls {node.value.func.id}"
            elif isinstance(node.value.func, ast.Attribute):
                return f"Performs {node.value.func.attr}"
        return ""
        
    def _extract_type_annotation(self, node: ast.AST) -> str:
        """Extract type annotation as string."""
        if hasattr(node, 'annotation') and node.annotation:
            return self._annotation_to_string(node.annotation)
        return 'any'
        
    def _annotation_to_string(self, node: ast.AST) -> str:
        """Convert type annotation AST node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._annotation_to_string(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._annotation_to_string(node.value)}[{self._annotation_to_string(node.slice)}]"
        return 'any'
        
    def _has_auth_decorator(self, node: ast.FunctionDef) -> bool:
        """Check if function has authentication decorator."""
        auth_decorators = {'login_required', 'auth_required', 'authenticated', 'requires_auth'}
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in auth_decorators:
                    return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in auth_decorators:
                        return True
        return False
        
    def _extract_middleware(self, node: ast.FunctionDef) -> List[str]:
        """Extract middleware from route decorators."""
        middleware = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id not in {'route', 'get', 'post', 'put', 'delete', 'patch'}:
                    middleware.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id not in {'route', 'get', 'post', 'put', 'delete', 'patch'}:
                        middleware.append(decorator.func.id)
                        
        return middleware
        
    def _extract_layout_info(self, content: str, component: str) -> Dict[str, Any]:
        """Extract layout information for frontend route."""
        layout_info = {
            'name': 'default',
            'nested': False
        }
        
        # Check for layout patterns
        layout_patterns = [
            r'layout:\s*[\'"](.+?)[\'"]',
            r'component:\s*(.+?)Layout',
        ]
        
        for pattern in layout_patterns:
            match = re.search(pattern, content)
            if match:
                layout_info['name'] = match.group(1)
                break
                
        # Check if route is nested
        if re.search(r'children:\s*\[', content):
            layout_info['nested'] = True
            
        return layout_info
        
    def _extract_route_guards(self, content: str, path: str) -> List[str]:
        """Extract route guards/middleware."""
        guards = []
        
        # Common guard patterns
        guard_patterns = [
            r'beforeEnter:\s*(.+?)[,}]',
            r'guard:\s*(.+?)[,}]',
            r'middleware:\s*\[(.+?)\]'
        ]
        
        for pattern in guard_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                guard = match.group(1).strip()
                if guard:
                    guards.extend([g.strip() for g in guard.split(',')])
                    
        return list(set(guards))  # Remove duplicates
        
    def _is_lazy_loaded(self, content: str, component: str) -> bool:
        """Check if component is lazy loaded."""
        lazy_patterns = [
            r'lazy\s*\(\s*\(\s*\)\s*=>\s*import\s*\(',
            r'import\s*\(\s*[\'"]',
            r'React\.lazy\s*\(',
            r'defineAsyncComponent\s*\('
        ]
        
        return any(re.search(pattern, content) for pattern in lazy_patterns) 