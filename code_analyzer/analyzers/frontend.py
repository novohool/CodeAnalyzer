"""Frontend analyzer module."""

from pathlib import Path
from typing import Dict, Any, List
import re

from .base import BaseAnalyzer

class FrontendAnalyzer(BaseAnalyzer):
    """Analyzes frontend code and components."""
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze frontend code.
        
        Returns:
            Dict containing frontend analysis results
        """
        results = {
            'components': self._analyze_components(),
            'routes': self._analyze_routes(),
            'state_management': self._analyze_state(),
            'api_integration': self._analyze_api_calls()
        }
        return {'frontend': results}
    
    def _analyze_components(self) -> List[Dict[str, Any]]:
        """Analyze React/Vue components."""
        components = []
        for file in self.repo_path.rglob('*'):
            if not self._is_component_file(file):
                continue
                
            content = file.read_text(encoding='utf-8')
            if 'React' in content:
                components.append(self._analyze_react_component(file, content))
            elif 'Vue' in content:
                components.append(self._analyze_vue_component(file, content))
        return components
    
    def _analyze_react_component(self, file: Path, content: str) -> Dict[str, Any]:
        """Analyze a React component."""
        return {
            'name': file.stem,
            'path': str(file.relative_to(self.repo_path)),
            'props': self._extract_react_props(content),
            'state': self._extract_react_state(content),
            'hooks': self._extract_react_hooks(content),
            'methods': self._extract_react_methods(content),
            'imports': self._extract_react_imports(content)
        }
    
    def _analyze_vue_component(self, file: Path, content: str) -> Dict[str, Any]:
        """Analyze a Vue component."""
        return {
            'name': file.stem,
            'path': str(file.relative_to(self.repo_path)),
            'props': self._extract_vue_props(content),
            'data': self._extract_vue_data(content),
            'methods': self._extract_vue_methods(content),
            'computed': self._extract_vue_computed(content),
            'watchers': self._extract_vue_watchers(content)
        }
    
    def _analyze_routes(self) -> List[Dict[str, Any]]:
        """Analyze frontend routes."""
        routes = []
        for file in self.repo_path.rglob('*'):
            if not self._is_router_file(file):
                continue
                
            content = file.read_text(encoding='utf-8')
            if 'react-router' in content:
                routes.extend(self._extract_react_routes(content))
            elif 'vue-router' in content:
                routes.extend(self._extract_vue_routes(content))
        return routes
    
    def _extract_react_routes(self, content: str) -> List[Dict[str, Any]]:
        """Extract React router routes."""
        routes = []
        route_matches = re.finditer(r'<Route[^>]*path=["\'](.*?)["\'][^>]*>', content)
        for match in route_matches:
            route = {
                'path': match.group(1),
                'component': self._extract_route_component(content, match.start()),
                'exact': 'exact' in content[match.start():content.find('>', match.start())]
            }
            routes.append(route)
        return routes
    
    def _extract_vue_routes(self, content: str) -> List[Dict[str, Any]]:
        """Extract Vue router routes."""
        routes = []
        try:
            # Look for routes array in router configuration
            routes_match = re.search(r'routes\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if routes_match:
                routes_content = routes_match.group(1)
                # Extract individual route objects
                route_objects = re.finditer(r'{(.*?)}', routes_content, re.DOTALL)
                for route_obj in route_objects:
                    route_data = route_obj.group(1)
                    path = re.search(r'path:\s*["\'](.+?)["\']', route_data)
                    component = re.search(r'component:\s*(\w+)', route_data)
                    if path:
                        routes.append({
                            'path': path.group(1),
                            'component': component.group(1) if component else None
                        })
        except Exception as e:
            self.add_issue('warning', f'Error parsing Vue routes: {str(e)}')
        return routes
    
    def _analyze_state(self) -> Dict[str, Any]:
        """Analyze state management."""
        state = {
            'redux': self._analyze_redux(),
            'vuex': self._analyze_vuex(),
            'context': self._analyze_context(),
            'composition': self._analyze_composition()
        }
        return state
    
    def _analyze_redux(self) -> Dict[str, Any]:
        """Analyze Redux state management."""
        redux = {
            'actions': self._extract_redux_actions(),
            'reducers': self._extract_redux_reducers(),
            'store': self._analyze_redux_store()
        }
        return redux
    
    def _analyze_vuex(self) -> Dict[str, Any]:
        """Analyze Vuex state management."""
        vuex = {
            'state': self._extract_vuex_state(),
            'mutations': self._extract_vuex_mutations(),
            'actions': self._extract_vuex_actions(),
            'modules': self._extract_vuex_modules()
        }
        return vuex
    
    def _analyze_context(self) -> List[Dict[str, Any]]:
        """Analyze React Context usage."""
        contexts = []
        for file in self.repo_path.rglob('*'):
            if not file.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                continue
                
            content = file.read_text(encoding='utf-8')
            context_matches = re.finditer(r'React\.createContext|createContext', content)
            for match in context_matches:
                contexts.append(self._extract_context_info(content, match.start()))
        return contexts
    
    def _analyze_composition(self) -> List[Dict[str, Any]]:
        """Analyze Vue Composition API usage."""
        compositions = []
        for file in self.repo_path.rglob('*.vue'):
            content = file.read_text(encoding='utf-8')
            if 'setup' in content:
                compositions.append(self._extract_composition_info(content))
        return compositions
    
    def _analyze_api_calls(self) -> List[Dict[str, Any]]:
        """Analyze API integration points."""
        api_calls = []
        for file in self.repo_path.rglob('*'):
            if not file.suffix in ['.js', '.jsx', '.ts', '.tsx', '.vue']:
                continue
                
            content = file.read_text(encoding='utf-8')
            api_calls.extend(self._extract_api_calls(content))
        return api_calls
    
    def _extract_api_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract API calls from content."""
        api_calls = []
        
        # Look for fetch/axios/http client calls
        patterns = [
            (r'fetch\(["\'](.+?)["\']', 'fetch'),
            (r'axios\.(get|post|put|delete)\(["\'](.+?)["\']', 'axios'),
            (r'http\.(get|post|put|delete)\(["\'](.+?)["\']', 'http')
        ]
        
        for pattern, client in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if client == 'fetch':
                    url = match.group(1)
                    method = 'GET'  # Default for fetch
                else:
                    url = match.group(2)
                    method = match.group(1).upper()
                    
                api_calls.append({
                    'url': url,
                    'method': method,
                    'client': client
                })
                
        return api_calls
    
    def _is_component_file(self, file: Path) -> bool:
        """Check if file is a component file."""
        return (file.suffix in ['.jsx', '.tsx', '.vue'] or
                (file.suffix in ['.js', '.ts'] and 
                 any(x in file.name for x in ['component', 'Component'])))
    
    def _is_router_file(self, file: Path) -> bool:
        """Check if file is a router configuration file."""
        return any(x in file.name.lower() for x in ['route', 'router'])
        
    def _extract_route_component(self, content: str, start_pos: int) -> str:
        """Extract component name from route definition."""
        component_match = re.search(r'component={([^}]+)}', content[start_pos:])
        return component_match.group(1) if component_match else None 