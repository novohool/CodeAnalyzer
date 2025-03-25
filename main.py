import os
import ast
import re
from typing import Dict, List, Optional, Set, Tuple
import markdown
from collections import defaultdict
import json

class CodeAnalyzer:
    def __init__(self, repo_path: str , output_dir: str):
        self.repo_path = repo_path
        self.backend_functions = []
        self.frontend_functions = []
        self.api_endpoints = []
        self.frontend_flows = []
        self.component_hierarchy = defaultdict(list)
        self.readme_content = ""
        self.import_analysis = defaultdict(list)
        self.hook_usage = defaultdict(list)
        self.api_calls = []
        self.state_management = defaultdict(list)
        self.output_dir = output_dir
        
    def analyze_repository(self):
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                os.remove(file_path)
                print(f"已删除旧文件: {file_path}")
        """主分析函数，遍历代码库并分析所有文件"""
        print(f"开始分析代码库: {self.repo_path}")
        
        for root, _, files in os.walk(self.repo_path):
            # 跳过虚拟环境和node_modules目录
            if 'venv' in root or 'node_modules' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if file.lower() == 'readme.md':
                        self._analyze_readme(file_path)
                    elif self._is_backend_file(file_path):
                        print(f"分析后端文件: {file_path}")
                        self._analyze_backend_file(file_path)
                    elif self._is_frontend_file(file_path):
                        print(f"分析前端文件: {file_path}")
                        self._analyze_frontend_file(file_path)
                except Exception as e:
                    print(f"分析文件 {file_path} 时出错: {str(e)}")
    
    def _analyze_readme(self, file_path: str):
        """分析README文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.readme_content = f.read()
        
        # 提取项目标题
        title_match = re.search(r'^#\s+(.+)$', self.readme_content, re.MULTILINE)
        project_title = title_match.group(1) if title_match else "未知项目"
        
        # 提取关键部分
        sections = {
            'description': self._extract_readme_section('##? Description'),
            'features': self._extract_readme_section('##? Features'),
            'installation': self._extract_readme_section('##? Installation'),
            'usage': self._extract_readme_section('##? Usage'),
            'configuration': self._extract_readme_section('##? Configuration'),
            'api_reference': self._extract_readme_section('##? API Reference'),
            'screenshots': self._extract_readme_section('##? Screenshots'),
        }
        
        print(f"分析完成README文件: {file_path}")
    
    def _extract_readme_section(self, pattern: str) -> str:
        """从README中提取指定部分内容"""
        match = re.search(fr'{pattern}\s+(.+?)(?=\n##|\Z)', self.readme_content, re.DOTALL|re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _is_backend_file(self, file_path: str) -> bool:
        """判断是否为后端文件"""
        backend_extensions = ['.py', '.java', '.go', '.js', '.ts']
        backend_dirs = ['api', 'server', 'backend', 'controller', 'service', 'app']
        return (any(file_path.endswith(ext) for ext in backend_extensions) and
                any(dir_name in file_path.lower() for dir_name in backend_dirs))
    
    def _is_frontend_file(self, file_path: str) -> bool:
        """判断是否为前端文件"""
        frontend_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue']
        frontend_dirs = ['src', 'frontend', 'client', 'components', 'pages', 'views']
        return (any(file_path.endswith(ext) for ext in frontend_extensions) and
                any(dir_name in file_path.lower() for dir_name in frontend_dirs))
    
    def _analyze_backend_file(self, file_path: str):
        """分析后端文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if file_path.endswith('.py'):
            self._analyze_python_backend(file_path, content)
        elif file_path.endswith(('.js', '.ts')) and 'server' in file_path.lower():
            self._analyze_js_backend(file_path, content)
    
    def _analyze_python_backend(self, file_path: str, content: str):
        """分析Python后端代码"""
        try:
            tree = ast.parse(content)
            
            # 提取Pydantic模型
            models = self._extract_pydantic_models(tree)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, file_path)
                    self.backend_functions.append(func_info)
                    
                    if self._is_api_endpoint(node):
                        endpoint_info = self._extract_api_endpoint(node, file_path)
                        # 关联Pydantic模型
                        for param in endpoint_info['params']:
                            if param['type'] in models:
                                param['model'] = models[param['type']]
                        self.api_endpoints.append(endpoint_info)
                        
                elif isinstance(node, ast.ClassDef):
                    self._analyze_python_class(node, file_path)
        except SyntaxError as e:
            print(f"Python语法错误在 {file_path}: {str(e)}")
    
    def _extract_function_info(self, node: ast.FunctionDef, file_path: str) -> Dict:
        """提取函数信息"""
        return {
            'file': file_path,
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'params': self._extract_parameters(node),
            'returns': self._extract_return_annotation(node),
            'logic': self._extract_function_logic(node),
            'called_functions': self._extract_called_functions(node),
            'type': 'backend'
        }
    
    def _extract_function_logic(self, node: ast.FunctionDef) -> str:
        """提取函数逻辑摘要"""
        logic_summary = []
        
        for item in node.body:
            if isinstance(item, ast.Return):
                logic_summary.append(f"返回: {self._get_return_description(item)}")
            elif isinstance(item, ast.If):
                logic_summary.append(f"条件判断: {ast.unparse(item.test)}")
            elif isinstance(item, ast.Assign):
                logic_summary.append(f"赋值: {ast.unparse(item.targets[0])} = {ast.unparse(item.value)}")
            elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                logic_summary.append(f"调用: {ast.unparse(item.value.func)}")
            elif isinstance(item, ast.For):
                logic_summary.append(f"循环: for {ast.unparse(item.target)} in {ast.unparse(item.iter)}")
            elif isinstance(item, ast.While):
                logic_summary.append(f"循环: while {ast.unparse(item.test)}")
            elif isinstance(item, ast.Try):
                logic_summary.append("异常处理: try-except块")
            elif isinstance(item, ast.With):
                logic_summary.append(f"上下文管理: with {ast.unparse(item.items[0])}")
        
        return "\n".join(logic_summary) if logic_summary else "无显著逻辑"
    
    def _get_return_description(self, return_node: ast.Return) -> str:
        """获取返回值的描述"""
        if return_node.value is None:
            return "None"
        
        try:
            if isinstance(return_node.value, ast.Call):
                return f"调用 {ast.unparse(return_node.value.func)}"
            elif isinstance(return_node.value, ast.Dict):
                return "返回字典"
            elif isinstance(return_node.value, ast.List):
                return "返回列表"
            elif isinstance(return_node.value, ast.Constant):
                return f"常量: {return_node.value.value}"
            else:
                return ast.unparse(return_node.value)
        except:
            return "复杂返回值"
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict]:
        """提取函数参数信息"""
        params = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else 'any',
                'default': None,
                'description': ''
            }
            # 处理 Depends 依赖
            if arg.annotation and isinstance(arg.annotation, ast.Call) and isinstance(arg.annotation.func, ast.Name):
                if arg.annotation.func.id == 'Depends':
                    param['type'] = f"Depends({ast.unparse(arg.annotation.args[0])})"
            params.append(param)
        
        # 处理默认值
        if node.args.defaults:
            for i, default in enumerate(node.args.defaults, start=len(node.args.args) - len(node.args.defaults)):
                params[i]['default'] = ast.unparse(default)
        
        return params
    def _extract_pydantic_models(self, tree: ast.AST) -> Dict[str, List[Dict]]:
        """提取Pydantic模型定义"""
        models = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        model_name = node.name
                        fields = []
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                field = {
                                    'name': item.target.id,
                                    'type': ast.unparse(item.annotation),
                                    'default': ast.unparse(item.value) if item.value else None
                                }
                                fields.append(field)
                        models[model_name] = fields
        return models

    def _extract_return_annotation(self, node: ast.FunctionDef) -> Dict:
        """提取返回类型注解"""
        if node.returns:
            return {
                'type': ast.unparse(node.returns),
                'description': ''
            }
        return {'type': 'None', 'description': ''}
    
    def _extract_called_functions(self, node: ast.FunctionDef) -> List[str]:
        """提取函数中调用的其他函数"""
        called_funcs = set()
        
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Attribute):
                    called_funcs.add(ast.unparse(item.func))
                elif isinstance(item.func, ast.Name):
                    called_funcs.add(item.func.id)
        
        return sorted(called_funcs)
    
    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """判断函数是否是API端点"""
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                return True
        return False
    
    def _get_decorator_name(self, decorator: ast.AST) -> Optional[str]:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
            elif isinstance(decorator.func, ast.Name):
                return decorator.func.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Name):
            return decorator.id
        return None
    
    def _extract_api_endpoint(self, node: ast.FunctionDef, file_path: str) -> Dict:
        """提取API端点信息"""
        endpoint = {
            'file': file_path,
            'function_name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'method': 'GET',  # 默认值
            'path': '/',      # 默认值
            'params': self._extract_parameters(node),
            'responses': self._extract_responses(node),
            'called_functions': self._extract_called_functions(node),
            'security': []
        }
        
        # 从装饰器中提取方法和路径
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                endpoint['method'] = decorator_name.upper()
                if isinstance(decorator, ast.Call) and decorator.args:
                    endpoint['path'] = self._get_string_value(decorator.args[0])
        
        # 提取安全依赖（例如 OAuth2）
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and self._get_decorator_name(decorator) == 'Depends':
                if decorator.args and isinstance(decorator.args[0], ast.Name):
                    if decorator.args[0].id == 'oauth2_scheme':
                        endpoint['security'].append('OAuth2')
        
        return endpoint    
    def _analyze_python_class(self, node: ast.ClassDef, file_path: str):
        """分析Python类定义"""
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                func_info = self._extract_function_info(item, file_path)
                func_info['class'] = node.name
                self.backend_functions.append(func_info)
                
                if self._is_api_endpoint(item):
                    endpoint_info = self._extract_api_endpoint(item, file_path)
                    endpoint_info['class'] = node.name
                    self.api_endpoints.append(endpoint_info)
    
    def _analyze_js_backend(self, file_path: str, content: str):
        """分析JavaScript/TypeScript后端代码"""
        # 这里实现JS后端代码分析的逻辑
        print(f"JavaScript后端分析: {file_path}")
        # 实际项目中可以集成esprima或babel-parser进行更详细的分析
    
    def _analyze_frontend_file(self, file_path: str):
        """分析前端文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            self._analyze_react_component(file_path, content)
        elif file_path.endswith('.vue'):
            self._analyze_vue_component(file_path, content)
    
    def _analyze_react_component(self, file_path: str, content: str):
        """深度分析React组件"""
        component_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 1. 分析导入语句
        imports = self._extract_react_imports(content)
        self.import_analysis[component_name] = imports
        
        # 2. 分析Hooks使用情况
        hooks = self._extract_react_hooks(content)
        self.hook_usage[component_name] = hooks
        
        # 3. 分析API调用
        api_calls = self._extract_react_api_calls(content)
        self.api_calls.extend([{'component': component_name, **call} for call in api_calls])
        
        # 4. 分析状态管理
        state_vars = self._extract_react_state(content)
        self.state_management[component_name] = state_vars
        
        # 5. 提取组件信息
        component_info = {
            'file': file_path,
            'name': component_name,
            'type': 'react-component',
            'imports': imports,
            'hooks': hooks,
            'api_calls': api_calls,
            'state_vars': state_vars,
            'props': self._extract_react_props(content),
            'methods': self._extract_react_methods(content)
        }
        self.frontend_functions.append(component_info)
        
        # 添加到组件层次结构
        dir_path = os.path.dirname(file_path)
        self.component_hierarchy[dir_path].append(component_name)
    
    def _extract_react_imports(self, content: str) -> List[Dict]:
        """提取React组件的导入语句"""
        imports = []
        import_pattern = re.compile(r'import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]')
        
        for line in content.split('\n'):
            if line.strip().startswith('import'):
                match = import_pattern.search(line)
                if match:
                    imports.append({
                        'source': match.group(2),
                        'imports': match.group(1)
                    })
        
        return imports
    
    def _extract_react_hooks(self, content: str) -> List[Dict]:
        """提取React Hooks使用情况"""
        hooks = []
        hook_pattern = re.compile(r'useState|useEffect|useCallback|useMemo|useRef|useContext')
        
        # 提取所有Hooks调用
        hook_calls = re.finditer(
            r'const\s+\[?(.+?)\]?\s*=\s*(use\w+)\(([^)]*)\)',
            content
        )
        
        for match in hook_calls:
            hook_name = match.group(2)
            if hook_name == 'useState':
                state_var = match.group(1).split(',')[0].strip()
                hooks.append({
                    'type': 'state',
                    'name': state_var,
                    'hook': hook_name,
                    'initial_value': match.group(3)
                })
            elif hook_name == 'useEffect':
                hooks.append({
                    'type': 'effect',
                    'hook': hook_name,
                    'dependencies': match.group(3)
                })
            elif hook_name in ['useCallback', 'useMemo']:
                hooks.append({
                    'type': 'memoization',
                    'hook': hook_name,
                    'dependencies': match.group(3)
                })
            else:
                hooks.append({
                    'type': 'other',
                    'hook': hook_name,
                    'details': match.group(3)
                })
        
        return hooks
    
    def _extract_react_api_calls(self, content: str) -> List[Dict]:
        """提取React组件中的API调用"""
        api_calls = []
        
        # 1. 查找axios调用
        axios_pattern = re.compile(
            r'(axios|api)\.(get|post|put|delete|patch)\s*\(\s*[\'"`](.+?)[\'"`]',
            re.DOTALL
        )
        
        # 2. 查找fetch调用
        fetch_pattern = re.compile(
            r'fetch\s*\(\s*[\'"`](.+?)[\'"`]',
            re.DOTALL
        )
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # 检查axios调用
            for match in axios_pattern.finditer(line):
                api_calls.append({
                    'method': match.group(2).upper(),
                    'url': match.group(3),
                    'library': 'axios',
                    'line': line_num
                })
            
            # 检查fetch调用
            for match in fetch_pattern.finditer(line):
                api_calls.append({
                    'method': 'GET',  # fetch默认是GET
                    'url': match.group(1),
                    'library': 'fetch',
                    'line': line_num
                })
        
        return api_calls
    
    def _extract_react_state(self, content: str) -> List[Dict]:
        """提取React组件的状态变量"""
        state_vars = []
        
        # 查找useState调用
        state_pattern = re.compile(
            r'const\s+\[(.+?)\]\s*=\s*useState\s*\(([^)]*)\)',
            re.DOTALL
        )
        
        for match in state_pattern.finditer(content):
            state_vars.append({
                'name': match.group(1).split(',')[0].strip(),
                'initial_value': match.group(2).strip(),
                'type': 'useState'
            })
        
        # 查找useReducer调用
        reducer_pattern = re.compile(
            r'const\s+\[(.+?)\]\s*=\s*useReducer\s*\(([^)]*)\)',
            re.DOTALL
        )
        
        for match in reducer_pattern.finditer(content):
            state_vars.append({
                'name': match.group(1).split(',')[0].strip(),
                'initial_value': 'useReducer',
                'type': 'useReducer',
                'reducer': match.group(2).strip()
            })
        
        return state_vars
    
    def _extract_react_props(self, content: str) -> List[Dict]:
        """提取React组件的props"""
        props = []
        
        # 查找组件函数/箭头函数的参数
        func_pattern = re.compile(
            r'function\s+\w+\s*\((.+?)\)|const\s+\w+\s*=\s*\((.+?)\)\s*=>',
            re.DOTALL
        )
        
        for match in func_pattern.finditer(content):
            params = match.group(1) or match.group(2)
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param.startswith('{') and param.endswith('}'):  # 解构props
                        props_in_obj = param[1:-1].split(',')
                        for prop in props_in_obj:
                            prop = prop.strip()
                            if ':' in prop:
                                prop_name, prop_type = prop.split(':', 1)
                                props.append({
                                    'name': prop_name.strip(),
                                    'type': prop_type.strip(),
                                    'required': False
                                })
                            else:
                                props.append({
                                    'name': prop,
                                    'type': 'any',
                                    'required': False
                                })
                    elif param:  # 普通props参数
                        props.append({
                            'name': param,
                            'type': 'any',
                            'required': False
                        })
        
        return props
    
    def _extract_react_methods(self, content: str) -> List[Dict]:
        """提取React组件的方法"""
        methods = []
        
        # 查找组件内定义的函数
        func_pattern = re.compile(
            r'const\s+(\w+)\s*=\s*(?:useCallback\s*\()?\s*\(([^)]*)\)\s*=>\s*{([^}]*)}',
            re.DOTALL
        )
        
        for match in func_pattern.finditer(content):
            method_name = match.group(1)
            params = match.group(2)
            body = match.group(3)
            
            # 检查方法中是否包含API调用
            api_calls_in_method = self._extract_react_api_calls(body)
            
            methods.append({
                'name': method_name,
                'params': [p.strip() for p in params.split(',') if p.strip()],
                'api_calls': api_calls_in_method
            })
        
        return methods
    
    def _analyze_vue_component(self, file_path: str, content: str):
        """分析Vue组件"""
        component_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 提取组件信息
        component_info = {
            'file': file_path,
            'name': component_name,
            'type': 'vue-component',
            'props': self._extract_vue_props(content),
            'data': self._extract_vue_data(content),
            'methods': self._extract_vue_methods(content),
            'computed': self._extract_vue_computed(content),
            'watchers': self._extract_vue_watchers(content),
            'lifecycle': self._extract_vue_lifecycle(content)
        }
        self.frontend_functions.append(component_info)
        
        # 添加到组件层次结构
        dir_path = os.path.dirname(file_path)
        self.component_hierarchy[dir_path].append(component_name)
    
    def _extract_vue_props(self, content: str) -> List[Dict]:
        """提取Vue组件的props"""
        props = []
        props_section = self._extract_vue_section(content, 'props')
        
        if props_section:
            # 提取对象形式的props
            obj_props = re.finditer(
                r'(\w+)\s*:\s*{\s*type\s*:\s*(.+?)\s*,\s*required\s*:\s*(true|false)',
                props_section
            )
            for match in obj_props:
                props.append({
                    'name': match.group(1),
                    'type': match.group(2),
                    'required': match.group(3) == 'true'
                })
            
            # 提取数组形式的props
            array_props = re.finditer(
                r'props\s*:\s*\[(.+?)\]',
                props_section
            )
            for match in array_props:
                for prop in match.group(1).split(','):
                    prop = prop.strip().strip("'").strip('"')
                    if prop:
                        props.append({
                            'name': prop,
                            'type': 'any',
                            'required': False
                        })
        
        return props
    
    def _extract_vue_data(self, content: str) -> Dict:
        """提取Vue组件的data"""
        data = {}
        data_section = self._extract_vue_section(content, 'data')
        
        if data_section:
            # 提取data函数中的返回对象
            return_match = re.search(
                r'return\s*{\s*([^}]+)\s*}',
                data_section,
                re.DOTALL
            )
            if return_match:
                for line in return_match.group(1).split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip().rstrip(',')
        
        return data
    
    def _extract_vue_methods(self, content: str) -> Dict:
        """提取Vue组件的方法"""
        methods = {}
        methods_section = self._extract_vue_section(content, 'methods')
        
        if methods_section:
            # 提取方法定义
            method_matches = re.finditer(
                r'(\w+)\s*\(([^)]*)\)\s*{\s*([^}]*)\s*}',
                methods_section,
                re.DOTALL
            )
            for match in method_matches:
                methods[match.group(1)] = {
                    'params': [p.strip() for p in match.group(2).split(',') if p.strip()],
                    'body': match.group(3).strip()
                }
        
        return methods
    def _generate_api_docs(self) -> List[Dict]:
        """Generate API documentation from the collected API endpoints."""
        api_docs = []
        for endpoint in self.api_endpoints:
            api_docs.append({
                'file': endpoint['file'],
                'function_name': endpoint['function_name'],
                'method': endpoint['method'],
                'path': endpoint['path'],
                'params': endpoint['params'],
                'responses': endpoint['responses'],
                'called_functions': endpoint['called_functions'],
                'security': endpoint['security'],
                'docstring': endpoint['docstring']
            })
        return api_docs

    def _generate_frontend_docs(self) -> Dict:
        """Generate frontend documentation from collected frontend data."""
        frontend_docs = {
            'components': [],
            'component_hierarchy': dict(self.component_hierarchy),
            'import_analysis': dict(self.import_analysis),
            'hook_usage': dict(self.hook_usage),
            'api_calls': self.api_calls,
            'state_management': dict(self.state_management)
        }
    
        for component in self.frontend_functions:
            if component['type'] in ['react-component', 'vue-component']:
                frontend_docs['components'].append({
                    'name': component['name'],
                    'file': component['file'],
                    'type': component['type'],
                    'props': component.get('props', []),
                    'methods': component.get('methods', {}),
                    'hooks': component.get('hooks', []),
                    'state_vars': component.get('state_vars', []),
                    'api_calls': component.get('api_calls', []),
                    'data': component.get('data', {}),
                    'computed': component.get('computed', {}),
                    'watchers': component.get('watchers', []),
                    'lifecycle': component.get('lifecycle', [])
                })
    
        return frontend_docs
    def _extract_vue_section(self, content: str, section_name: str) -> str:
        """从Vue组件中提取指定部分内容"""
        script_match = re.search(
            r'<script[^>]*>([\s\S]*?)<\/script>',
            content
        )
        if not script_match:
            return ""
        
        script_content = script_match.group(1)
        section_match = re.search(
            fr'{section_name}\s*:\s*{{\s*([^}}]+)\s*}}|{section_name}\s*\(\s*\)\s*{{\s*([\s\S]*?)\s*}}',
            script_content,
            re.DOTALL
        )
        return section_match.group(1) or section_match.group(2) if section_match else ""

    def _generate_api_docs_md(self) -> str:
        """生成Markdown格式的API文档"""
        api_docs = ["# API 文档\n"]
        for endpoint in self.api_endpoints:
            api_docs.append(f"## {endpoint['method']} {endpoint['path']}\n")
            api_docs.append(f"**函数名称**: `{endpoint['function_name']}`\n")
            api_docs.append(f"**文件路径**: `{endpoint['file']}`\n")
            if endpoint['docstring']:
                api_docs.append(f"**描述**: {endpoint['docstring']}\n")
            
            # 参数部分
            if endpoint['params']:
                api_docs.append("### 请求参数\n")
                api_docs.append("| 参数名 | 类型 | 默认值 | 描述 |\n")
                api_docs.append("|--------|------|--------|------|\n")
                for param in endpoint['params']:
                    param_type = param['type']
                    if 'model' in param:
                        param_type = f"{param_type} (Pydantic Model)"
                        api_docs.append(f"\n**{param_type} 字段**:\n")
                        for field in param['model']:
                            api_docs.append(f"- `{field['name']}`: {field['type']} (默认: {field['default'] or '无'})\n")
                    api_docs.append(
                        f"| {param['name']} | {param_type} | {param.get('default', '无')} | {param.get('description', '无')} |\n"
                    )
            
            # 安全部分
            if endpoint['security']:
                api_docs.append("### 安全要求\n")
                api_docs.append(", ".join(endpoint['security']) + "\n")
            
            api_docs.append("\n---\n")
        return "".join(api_docs)

    def _generate_frontend_docs_md(self) -> str:
        """生成Markdown格式的前端文档"""
        frontend_docs = ["# 前端文档\n"]
        
        # 1. 组件信息
        frontend_docs.append("## 组件信息\n")
        for component in self.frontend_functions:
            frontend_docs.append(f"### {component['name']} ({component['type']})\n")
            frontend_docs.append(f"- **文件路径**: `{component['file']}`\n")
            
            # Props
            if component.get('props'):
                frontend_docs.append("#### Props\n")
                frontend_docs.append("| 名称 | 类型 | 必填 |\n")
                frontend_docs.append("|------|------|------|\n")
                for prop in component['props']:
                    frontend_docs.append(
                        f"| {prop['name']} | {prop['type']} | {'是' if prop['required'] else '否'} |\n"
                    )
            
            # 方法
            if component.get('methods'):
                frontend_docs.append("#### 方法\n")
                # Ensure methods is a dictionary
                methods = component['methods']
                if isinstance(methods, list):  # Convert list to dictionary if needed
                    methods_dict = {method['name']: method for method in methods}
                else:
                    methods_dict = methods
                
                for method_name, method_info in methods_dict.items():
                    frontend_docs.append(f"- **方法名称**: `{method_name}`\n")
                    frontend_docs.append(f"  - 参数: {', '.join(method_info.get('params', []))}\n")
                    if method_info.get('api_calls'):
                        frontend_docs.append("  - API调用:\n")
                        for api_call in method_info['api_calls']:
                            frontend_docs.append(f"    - 方法: {api_call['method']}, URL: {api_call['url']}\n")
                frontend_docs.append("\n")
            
            # 状态管理
            if component.get('state_vars'):
                frontend_docs.append("#### 状态变量\n")
                for state_var in component['state_vars']:
                    frontend_docs.append(f"- **名称**: `{state_var['name']}`\n")
                    frontend_docs.append(f"  - 初始值: {state_var['initial_value']}\n")
                    frontend_docs.append(f"  - 类型: {state_var['type']}\n")
            
            # API调用
            if component.get('api_calls'):
                frontend_docs.append("#### API调用\n")
                for api_call in component['api_calls']:
                    frontend_docs.append(f"- **方法**: {api_call['method']}\n")
                    frontend_docs.append(f"  - URL: {api_call['url']}\n")
                    frontend_docs.append(f"  - 库: {api_call['library']}\n")
            
            frontend_docs.append("\n---\n")
        
        # 2. 组件层次结构
        frontend_docs.append("## 组件层次结构\n")
        for dir_path, components in self.component_hierarchy.items():
            frontend_docs.append(f"- **目录**: `{dir_path}`\n")
            frontend_docs.append("  - 包含组件:\n")
            for component in components:
                frontend_docs.append(f"    - `{component}`\n")
        
        # 3. 导入分析
        frontend_docs.append("## 导入分析\n")
        for component, imports in self.import_analysis.items():
            frontend_docs.append(f"- **组件**: `{component}`\n")
            frontend_docs.append("  - 导入模块:\n")
            for imp in imports:
                frontend_docs.append(f"    - `{imp['source']}` (导入内容: `{imp['imports']}`)\n")
        
        # 4. Hook使用情况
        frontend_docs.append("## Hook使用情况\n")
        for component, hooks in self.hook_usage.items():
            frontend_docs.append(f"- **组件**: `{component}`\n")
            frontend_docs.append("  - 使用的Hooks:\n")
            for hook in hooks:
                frontend_docs.append(f"    - `{hook['hook']}` (类型: `{hook['type']}`)\n")
                if hook['type'] == 'state':
                    frontend_docs.append(f"      - 初始值: {hook['initial_value']}\n")
        
        # 5. API调用汇总
        frontend_docs.append("## API调用汇总\n")
        for api_call in self.api_calls:
            frontend_docs.append(f"- **组件**: `{api_call['component']}`\n")
            frontend_docs.append(f"  - 方法: {api_call['method']}\n")
            frontend_docs.append(f"  - URL: {api_call['url']}\n")
            frontend_docs.append(f"  - 库: {api_call['library']}\n")
        
        # 6. 状态管理
        frontend_docs.append("## 状态管理\n")
        for component, states in self.state_management.items():
            frontend_docs.append(f"- **组件**: `{component}`\n")
            frontend_docs.append("  - 状态变量:\n")
            for state in states:
                frontend_docs.append(f"    - `{state['name']}` (初始值: `{state['initial_value']}`)\n")
        
        return "".join(frontend_docs)
    def _generate_architecture_md(self) -> str:
        """生成Markdown格式的架构文档"""
        architecture_docs = ["# 项目架构\n"]
        
        # 1. 项目结构
        architecture_docs.append("## 项目结构\n")
        for root, dirs, files in os.walk(self.repo_path):
            if 'venv' in root or 'node_modules' in root:
                continue
            relative_path = os.path.relpath(root, self.repo_path)
            architecture_docs.append(f"- **目录**: `{relative_path}`\n")
            if dirs:
                architecture_docs.append("  - 子目录:\n")
                for dir_name in dirs:
                    architecture_docs.append(f"    - `{dir_name}`\n")
            if files:
                architecture_docs.append("  - 文件:\n")
                for file_name in files:
                    architecture_docs.append(f"    - `{file_name}`\n")
        
        # 2. 组件层次结构
        architecture_docs.append("## 组件层次结构\n")
        for dir_path, components in self.component_hierarchy.items():
            relative_dir_path = os.path.relpath(dir_path, self.repo_path)
            architecture_docs.append(f"- **目录**: `{relative_dir_path}`\n")
            architecture_docs.append("  - 包含组件:\n")
            for component in components:
                architecture_docs.append(f"    - `{component}`\n")
        
        # 3. 后端与前端交互
        architecture_docs.append("## 后端与前端交互\n")
        architecture_docs.append("### API调用汇总\n")
        for api_call in self.api_calls:
            architecture_docs.append(f"- **组件**: `{api_call['component']}`\n")
            architecture_docs.append(f"  - 方法: {api_call['method']}\n")
            architecture_docs.append(f"  - URL: {api_call['url']}\n")
            architecture_docs.append(f"  - 库: {api_call['library']}\n")
        
        # 4. 状态管理
        architecture_docs.append("## 状态管理\n")
        for component, states in self.state_management.items():
            architecture_docs.append(f"- **组件**: `{component}`\n")
            architecture_docs.append("  - 状态变量:\n")
            for state in states:
                architecture_docs.append(f"    - `{state['name']}` (初始值: `{state['initial_value']}`)\n")
        
        return "".join(architecture_docs)
    def _generate_project_overview_md(self) -> str:
        """生成Markdown格式的项目概览文档"""
        project_info = self._generate_project_info()
        overview = []
        overview.append(f"# {project_info['name']}")
        overview.append("")
        
        if project_info['description']:
            overview.append("## 描述")
            overview.append(project_info['description'])
            overview.append("")
        
        if project_info['features']:
            overview.append("## 功能特性")
            for feature in project_info['features']:
                overview.append(f"- {feature}")
            overview.append("")
        
        if project_info['installation']:
            overview.append("## 安装指南")
            overview.append("```bash")
            overview.append(project_info['installation'])
            overview.append("```")
            overview.append("")
        
        if project_info['usage']:
            overview.append("## 使用说明")
            overview.append(project_info['usage'])
            overview.append("")
        
        return "\n".join(overview)
    def generate_full_documentation(self) -> Dict:
        """生成完整的项目文档"""
        return {
            'project_info': self._generate_project_info(),
            'api_documentation': self._generate_api_docs(),
            'backend_functions': self.backend_functions,
            'frontend_documentation': self._generate_frontend_docs(),
            'component_hierarchy': dict(self.component_hierarchy),
            'import_analysis': dict(self.import_analysis),
            'hook_usage': dict(self.hook_usage),
            'api_calls': self.api_calls,
            'state_management': dict(self.state_management)
        }
    
    def _generate_project_info(self) -> Dict:
        """生成项目基本信息"""
        return {
            'name': re.search(r'^#\s+(.+)$', self.readme_content, re.MULTILINE).group(1) if self.readme_content else "未知项目",
            'description': self._extract_readme_section('##? Description'),
            'features': self._extract_readme_section('##? Features').split('\n'),
            'installation': self._extract_readme_section('##? Installation'),
            'usage': self._extract_readme_section('##? Usage')
        }
    
    def save_documentation(self):
        """保存所有文档到指定目录"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成完整文档
        full_docs = self.generate_full_documentation()
        
        # 保存为JSON
        with open(os.path.join(self.output_dir, 'full_documentation.json'), 'w', encoding='utf-8') as f:
            json.dump(full_docs, f, indent=2, ensure_ascii=False)
        
        # 保存为Markdown
        self._save_markdown_docs()
        
        print(f"文档已保存到 {os.path.abspath(self.output_dir)}")
    
    def _save_markdown_docs(self):
        """保存Markdown格式文档"""
        # 1. 项目概览文档
        with open(os.path.join(self.output_dir, 'PROJECT_OVERVIEW.md'), 'w', encoding='utf-8') as f:
            f.write(self._generate_project_overview_md())
        
        # 2. API文档
        with open(os.path.join(self.output_dir, 'API_DOCUMENTATION.md'), 'w', encoding='utf-8') as f:
            f.write(self._generate_api_docs_md())
        
        # 3. 前端文档
        with open(os.path.join(self.output_dir, 'FRONTEND_DOCUMENTATION.md'), 'w', encoding='utf-8') as f:
            f.write(self._generate_frontend_docs_md())
        
        # 4. 架构文档
        with open(os.path.join(self.output_dir, 'ARCHITECTURE.md'), 'w', encoding='utf-8') as f:
            f.write(self._generate_architecture_md())
if __name__ == "__main__":
    # 使用您的K8S多集群资源面板路径
    repo_path = "../K8S-multi-cluster-resource-panel"
    dir_path = "docs"
    analyzer = CodeAnalyzer(repo_path,dir_path)
    analyzer.analyze_repository()
    analyzer.save_documentation()
