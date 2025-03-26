"""Route analyzer module for analyzing frontend and backend routes."""

import ast
import re
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseAnalyzer

class RouteAnalyzer(BaseAnalyzer):
    """Analyzes frontend and backend routes."""
    
    def __init__(self, repo_path: str):
        super().__init__(repo_path)
        self.routes = {
            'frontend': [],
            'backend': []
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze frontend and backend routes.
        
        Returns:
            Dictionary containing route analysis results
        """
        # 分析后端路由
        for file in self.repo_path.rglob('*.py'):
            if self._is_excluded_path(file):
                continue
                
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._analyze_backend_routes(file, content)
            except Exception as e:
                print(f"Error analyzing backend routes in {file}: {str(e)}")
                
        # 分析前端路由
        frontend_patterns = [
            '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx', '**/*.vue'
        ]
        
        for pattern in frontend_patterns:
            for file in self.repo_path.glob(pattern):
                if self._is_excluded_path(file):
                    continue
                    
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self._analyze_frontend_routes(file, content)
                except Exception as e:
                    print(f"Error analyzing frontend routes in {file}: {str(e)}")
                    
        return self.routes
        
    def _analyze_backend_routes(self, file: Path, content: str) -> None:
        """Analyze backend routes in Python files."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    route_info = self._extract_backend_route(node, file)
                    if route_info:
                        self.routes['backend'].append(route_info)
        except Exception as e:
            print(f"Error parsing {file}: {str(e)}")
            
    def _extract_backend_route(self, node: ast.FunctionDef, file: Path) -> Dict[str, Any]:
        """Extract route information from a function definition."""
        route_info = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    # Flask style: @app.route('/path')
                    if decorator.func.id in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                        route_info = self._create_backend_route_info(decorator, node, file)
                elif isinstance(decorator.func, ast.Attribute):
                    # Django style: @api_view(['GET'])
                    if decorator.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch', 'api_view']:
                        route_info = self._create_backend_route_info(decorator, node, file)
                        
        return route_info
        
    def _create_backend_route_info(self, decorator: ast.Call, node: ast.FunctionDef, file: Path) -> Dict[str, Any]:
        """Create backend route information dictionary."""
        methods = self._get_http_methods(decorator)
        path = self._get_route_path(decorator)
        
        route_info = {
            'path': path,
            'methods': methods,
            'handler': node.name,
            'file': str(file.relative_to(self.repo_path)),
            'line_number': node.lineno,
            'parameters': self._get_parameters(node),
            'returns': self._get_return_type(node),
            'docstring': ast.get_docstring(node) or '',
            'auth_required': self._has_auth_decorator(node),
            'middleware': self._get_middleware(node),
            'functionality': self._extract_functionality(node)
        }
        
        return route_info
        
    def _analyze_frontend_routes(self, file: Path, content: str) -> None:
        """Analyze frontend routes in JS/TS files."""
        # React Router patterns
        react_patterns = [
            (r'<Route[^>]*path=[\'"](.*?)[\'"][^>]*component=\{(.*?)\}', 'react'),
            (r'{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*component:\s*(.+?)\s*}', 'react'),
            (r'createBrowserRouter\(\s*\[\s*{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*element:\s*(.+?)\s*}', 'react')
        ]
        
        # Vue Router patterns
        vue_patterns = [
            (r'{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*component:\s*(.+?)\s*}', 'vue'),
            (r'{\s*path:\s*[\'"](.+?)[\'"]\s*,\s*name:\s*[\'"](.+?)[\'"]\s*}', 'vue')
        ]
        
        all_patterns = react_patterns + vue_patterns
        
        for pattern, framework in all_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                route_info = self._create_frontend_route_info(match, framework, file)
                if route_info:
                    self.routes['frontend'].append(route_info)
                    
    def _create_frontend_route_info(self, match: re.Match, framework: str, file: Path) -> Dict[str, Any]:
        """Create frontend route information dictionary."""
        path = match.group(1)
        component = match.group(2) if len(match.groups()) > 1 else ''
        
        route_info = {
            'path': path,
            'component': component.strip(),
            'framework': framework,
            'file': str(file.relative_to(self.repo_path)),
            'line_number': self._get_line_number(file, match.start()),
            'layout': self._extract_layout_info(file),
            'guards': self._extract_route_guards(file),
            'lazy_loading': self._is_lazy_loaded(file),
            'meta': self._extract_route_meta(file)
        }
        
        return route_info
        
    def _get_http_methods(self, node: ast.Call) -> List[str]:
        """Extract HTTP methods from decorator."""
        methods = []
        
        # Flask style: @app.route('/path', methods=['GET', 'POST'])
        for keyword in node.keywords:
            if keyword.arg == 'methods':
                if isinstance(keyword.value, (ast.List, ast.Tuple)):
                    methods.extend(m.s for m in keyword.value.elts if isinstance(m, ast.Str))
                    
        # Django style: @api_view(['GET', 'POST'])
        if not methods and node.args:
            arg = node.args[0]
            if isinstance(arg, (ast.List, ast.Tuple)):
                methods.extend(m.s for m in arg.elts if isinstance(m, ast.Str))
                
        # Default to GET if no methods specified
        return methods if methods else ['GET']
        
    def _get_route_path(self, node: ast.Call) -> str:
        """Extract route path from decorator."""
        # Check positional arguments first
        if node.args and isinstance(node.args[0], ast.Str):
            return node.args[0].s
            
        # Check keywords
        for keyword in node.keywords:
            if keyword.arg in ['path', 'pattern'] and isinstance(keyword.value, ast.Str):
                return keyword.value.s
                
        return ''
        
    def _get_parameters(self, node: ast.FunctionDef) -> List[Dict[str, str]]:
        """Extract function parameters."""
        params = []
        
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_annotation_name(arg.annotation) if arg.annotation else 'Any',
                'required': True
            }
            params.append(param_info)
            
        for arg in node.args.kwonlyargs:
            param_info = {
                'name': arg.arg,
                'type': self._get_annotation_name(arg.annotation) if arg.annotation else 'Any',
                'required': False
            }
            params.append(param_info)
            
        return params
        
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Extract function return type."""
        if node.returns:
            return self._get_annotation_name(node.returns)
        return 'Any'
        
    def _has_auth_decorator(self, node: ast.FunctionDef) -> bool:
        """Check if function has authentication decorator."""
        auth_decorators = {
            'login_required', 'auth_required', 'authenticated',
            'requires_auth', 'jwt_required', 'token_required'
        }
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in auth_decorators:
                    return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in auth_decorators:
                        return True
                        
        return False
        
    def _get_middleware(self, node: ast.FunctionDef) -> List[str]:
        """Extract middleware from function decorators."""
        middleware = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if not decorator.id in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                    middleware.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if not decorator.func.id in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                        middleware.append(decorator.func.id)
                        
        return middleware
        
    def _extract_functionality(self, node: ast.FunctionDef) -> str:
        """Extract main functionality from function."""
        # First try docstring
        docstring = ast.get_docstring(node)
        if docstring:
            return docstring.split('\n')[0]
            
        # Then try to analyze function body
        functionality = []
        for child in node.body:
            if isinstance(child, ast.Return):
                functionality.append("Returns response")
            elif isinstance(child, ast.Assign):
                if isinstance(child.targets[0], ast.Name):
                    functionality.append(f"Processes {child.targets[0].id}")
            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                if isinstance(child.value.func, ast.Name):
                    functionality.append(f"Calls {child.value.func.id}")
                elif isinstance(child.value.func, ast.Attribute):
                    functionality.append(f"Performs {child.value.func.attr}")
                    
        return ' '.join(functionality) if functionality else "No description available"
        
    def _extract_layout_info(self, file: Path) -> Dict[str, Any]:
        """Extract layout information from frontend route file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            layout_info = {
                'name': 'default',
                'nested': False
            }
            
            # Check for layout patterns
            layout_patterns = [
                r'layout:\s*[\'"](.+?)[\'"]',
                r'component:\s*(.+?)Layout'
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
        except Exception:
            return {'name': 'default', 'nested': False}
            
    def _extract_route_guards(self, file: Path) -> List[str]:
        """Extract route guards from frontend route file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            guards = []
            guard_patterns = [
                r'beforeEnter:\s*(.+?)[,}]',
                r'guard:\s*(.+?)[,}]',
                r'canActivate:\s*\[(.+?)\]'
            ]
            
            for pattern in guard_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    guard = match.group(1).strip()
                    if guard:
                        guards.extend([g.strip() for g in guard.split(',')])
                        
            return list(set(guards))
        except Exception:
            return []
            
    def _is_lazy_loaded(self, file: Path) -> bool:
        """Check if route component is lazy loaded."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lazy_patterns = [
                r'lazy\s*\(\s*\(\s*\)\s*=>\s*import\s*\(',
                r'import\s*\(\s*[\'"]',
                r'React\.lazy\s*\(',
                r'defineAsyncComponent\s*\('
            ]
            
            return any(re.search(pattern, content) for pattern in lazy_patterns)
        except Exception:
            return False
            
    def _extract_route_meta(self, file: Path) -> Dict[str, Any]:
        """Extract route metadata."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            meta = {}
            meta_patterns = [
                (r'meta:\s*{\s*title:\s*[\'"](.+?)[\'"]', 'title'),
                (r'meta:\s*{\s*auth:\s*(true|false)', 'requiresAuth'),
                (r'meta:\s*{\s*roles:\s*\[(.+?)\]', 'roles')
            ]
            
            for pattern, key in meta_patterns:
                match = re.search(pattern, content)
                if match:
                    value = match.group(1)
                    if key == 'roles':
                        value = [r.strip().strip('"\'') for r in value.split(',')]
                    elif key == 'requiresAuth':
                        value = value.lower() == 'true'
                    meta[key] = value
                    
            return meta
        except Exception:
            return {}
            
    def _get_line_number(self, file: Path, pos: int) -> int:
        """Get line number for a position in file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content.count('\n', 0, pos) + 1
        except Exception:
            return 0
            
    def _get_annotation_name(self, node: ast.AST) -> str:
        """Convert type annotation AST node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation_name(node.value)}[{self._get_annotation_name(node.slice)}]"
        return 'Any' 