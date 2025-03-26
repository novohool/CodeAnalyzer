import os
import ast
import re
from typing import Dict, List, Optional, Set
from collections import defaultdict
import json
import glob

class CodeAnalyzer:
    def __init__(self, repo_path: str, output_dir: str = "docs"):
        """Initialize code analyzer"""
        self.repo_path = repo_path
        self.output_dir = output_dir
        
        # Basic info
        self.project_info = {
            'name': os.path.basename(repo_path),
            'description': '',
            'version': '',
            'author': '',
            'license': ''
        }
        
        # Frontend and Backend functions
        self.frontend_functions = []
        self.backend_functions = []
        
        # Framework info
        self.frameworks = {
            'web': {
                'name': None,
                'version': None,
                'major_packages': [],
                'build_tools': []
            },
            'server': {
                'name': None,
                'version': None,
                'major_packages': [],
                'database': {},
                'orm': {}
            }
        }
        
        # 路由分析
        self.route_analysis = {
            'frontend': {
                'base_routes': [],
                'resource_routes': [],
                'auth_routes': []
            },
            'backend': {
                'api_routes': [],
                'resource_routes': [],
                'auth_routes': [],
                'websocket_routes': []
            },
            'matching': {
                'route_pairs': [],
                'unmatched_frontend': [],
                'unmatched_backend': [],
                'match_score': 0
            }
        }
        
        # 目录结构分析
        self.directory_analysis = {
            'frontend': {
                'components': [],
                'pages': [],
                'services': [],
                'utils': [],
                'styles': []
            },
            'backend': {
                'api': [],
                'services': [],
                'models': [],
                'utils': [],
                'core': []
            },
            'matching': {
                'structure_score': 0,
                'suggestions': []
            }
        }
        
        # 代码质量分析
        self.code_metrics = {}
        
        # API端点
        self.api_endpoints = []
        
        # 路由信息
        self.routes = {
            'react': [],
            'fastapi': []
        }
        
        # WebSocket端点
        self.websocket_endpoints = []
        
        # 其他分析字段
        self.dependencies = {
            'frontend': defaultdict(list),
            'backend': defaultdict(list)
        }
        
        self.api_docs = []
        self.frontend_docs = []
        self.component_hierarchy = defaultdict(list)
        self.import_analysis = defaultdict(list)
        self.hook_usage = defaultdict(list)
        self.api_calls = []
        self.state_management = defaultdict(list)
        self.k8s_configs = []
        self.k8s_panel_analysis = []
        self.test_coverage = {}
        self.code_quality = []
        self.routing_info = []
        self.config_info = []
        self.xterm_components = []
        self.env_configs = {}
        self.nginx_config = {}
        
        # 初始化readme内容
        self.readme_content = ""
        
        # 初始化路由配置
        self.route_config = {
            'client': {
                'patterns': [
                    'src/App.{js,jsx,ts,tsx}',
                    'src/router/**/*.{js,jsx,ts,tsx}',
                    'src/routes/**/*.{js,jsx,ts,tsx}',
                    'src/pages/**/*.{js,jsx,ts,tsx}'
                ],
                'base_dir': 'client'  # 默认前端目录名
            },
            'server': {
                'patterns': [
                    'app/api/**/*.py',
                    'app/routers/**/*.py',
                    'routes/**/*.py',
                    'controllers/**/*.py'
                ],
                'base_dir': 'server'  # 默认后端目录名
            }
        }
    
    def analyze_repository(self):
        """分析代码仓库"""
        # 分析项目结构
        self._analyze_project_structure()
        
        # 分析依赖
        self._analyze_dependencies()
        
        # 分析前端文件
        self._analyze_frontend_files()
        
        # 分析后端文件
        self._analyze_backend_files()
        
        # 分析目录结构
        self._analyze_directory_structure()
        
        # 分析前端路由
        client_routes = []
        for pattern in self.route_config['client']['patterns']:
            full_pattern = os.path.join(self.repo_path, self.route_config['client']['base_dir'], pattern)
            client_routes.extend(glob.glob(full_pattern, recursive=True))
        
        for route_file in client_routes:
            self._analyze_frontend_routes(route_file)
            
        # 分析后端路由
        server_routes = []
        for pattern in self.route_config['server']['patterns']:
            full_pattern = os.path.join(self.repo_path, self.route_config['server']['base_dir'], pattern)
            server_routes.extend(glob.glob(full_pattern, recursive=True))
        
        for route_file in server_routes:
            self._analyze_backend_routes(route_file)
            
        # 分析路由匹配度
        self._analyze_route_matching()
        
        # 生成文档
        self.generate_full_documentation()
    
    def _analyze_frameworks(self):
        """分析前后端框架信息"""
        # 分析前端框架
        package_json = os.path.join(self.repo_path, 'package.json')
        if os.path.exists(package_json):
            with open(package_json, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    
                    # 检测前端框架
                    if 'react' in deps:
                        self.frameworks['frontend']['name'] = 'React'
                        self.frameworks['frontend']['version'] = deps['react']
                        # 主要包
                        self.frameworks['frontend']['major_packages'] = {
                            'react-dom': deps.get('react-dom', ''),
                            'react-router-dom': deps.get('react-router-dom', ''),
                            'redux': deps.get('redux', ''),
                            'react-redux': deps.get('react-redux', ''),
                            '@reduxjs/toolkit': deps.get('@reduxjs/toolkit', '')
                        }
                        # 构建工具
                        self.frameworks['frontend']['build_tools'] = {
                            'webpack': dev_deps.get('webpack', ''),
                            'babel': dev_deps.get('@babel/core', ''),
                            'typescript': dev_deps.get('typescript', ''),
                            'eslint': dev_deps.get('eslint', '')
                        }
                    elif 'vue' in deps:
                        self.frameworks['frontend']['name'] = 'Vue'
                        self.frameworks['frontend']['version'] = deps['vue']
                        # 主要包
                        self.frameworks['frontend']['major_packages'] = {
                            'vue-router': deps.get('vue-router', ''),
                            'vuex': deps.get('vuex', ''),
                            'pinia': deps.get('pinia', '')
                        }
                        # 构建工具
                        self.frameworks['frontend']['build_tools'] = {
                            'vite': dev_deps.get('vite', ''),
                            'vue-cli': dev_deps.get('@vue/cli-service', ''),
                            'typescript': dev_deps.get('typescript', '')
                        }
                except json.JSONDecodeError:
                    print(f"Error parsing package.json")

        # 分析后端框架
        requirements_txt = os.path.join(self.repo_path, 'requirements.txt')
        if os.path.exists(requirements_txt):
            with open(requirements_txt, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                
                # 检测后端框架
                for req in requirements:
                    if 'fastapi' in req.lower():
                        self.frameworks['backend']['name'] = 'FastAPI'
                        self.frameworks['backend']['version'] = req.split('==')[1] if '==' in req else ''
                        # 主要包
                        self.frameworks['backend']['major_packages'] = {
                            'uvicorn': next((r.split('==')[1] for r in requirements if r.startswith('uvicorn')), ''),
                            'pydantic': next((r.split('==')[1] for r in requirements if r.startswith('pydantic')), ''),
                            'starlette': next((r.split('==')[1] for r in requirements if r.startswith('starlette')), '')
                        }
                        break
                    elif 'flask' in req.lower():
                        self.frameworks['backend']['name'] = 'Flask'
                        self.frameworks['backend']['version'] = req.split('==')[1] if '==' in req else ''
                        # 主要包
                        self.frameworks['backend']['major_packages'] = {
                            'flask-sqlalchemy': next((r.split('==')[1] for r in requirements if r.startswith('Flask-SQLAlchemy')), ''),
                            'flask-restful': next((r.split('==')[1] for r in requirements if r.startswith('Flask-RESTful')), '')
                        }
                        break
                    elif 'django' in req.lower():
                        self.frameworks['backend']['name'] = 'Django'
                        self.frameworks['backend']['version'] = req.split('==')[1] if '==' in req else ''
                        # 主要包
                        self.frameworks['backend']['major_packages'] = {
                            'djangorestframework': next((r.split('==')[1] for r in requirements if r.startswith('djangorestframework')), ''),
                            'django-cors-headers': next((r.split('==')[1] for r in requirements if r.startswith('django-cors-headers')), '')
                        }
                        break
                
                # 检测数据库和ORM
                for req in requirements:
                    # 数据库
                    if 'psycopg2' in req.lower() or 'psycopg-binary' in req.lower():
                        self.frameworks['backend']['database']['postgresql'] = req.split('==')[1] if '==' in req else ''
                    elif 'pymysql' in req.lower() or 'mysqlclient' in req.lower():
                        self.frameworks['backend']['database']['mysql'] = req.split('==')[1] if '==' in req else ''
                    elif 'sqlite3' in req.lower():
                        self.frameworks['backend']['database']['sqlite'] = req.split('==')[1] if '==' in req else ''
                    elif 'mongodb' in req.lower():
                        self.frameworks['backend']['database']['mongodb'] = req.split('==')[1] if '==' in req else ''
                    
                    # ORM
                    if 'sqlalchemy' in req.lower():
                        self.frameworks['backend']['orm']['sqlalchemy'] = req.split('==')[1] if '==' in req else ''
                    elif 'peewee' in req.lower():
                        self.frameworks['backend']['orm']['peewee'] = req.split('==')[1] if '==' in req else ''
                    elif 'tortoise' in req.lower():
                        self.frameworks['backend']['orm']['tortoise'] = req.split('==')[1] if '==' in req else ''

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
        try:
            return {
                'file': file_path,
                'name': node.name,
                'docstring': ast.get_docstring(node) or "",
                'params': self._extract_parameters(node),
                'returns': self._extract_return_annotation(node),
                'logic': self._extract_function_logic(node),
                'called_functions': self._extract_called_functions(node),
                'complexity': self._calculate_function_complexity(node),
                'type': 'backend',
                'logic_flow': self._analyze_function_flow(node),
                'variables': self._extract_variables(node),
                'imports': self._extract_function_imports(node, file_path)
            }
        except Exception as e:
            print(f"Error extracting function info from {file_path}: {str(e)}")
            return {
                'file': file_path,
                'name': node.name,
                'error': str(e)
            }
    
    def _extract_function_logic(self, node: ast.FunctionDef) -> Dict:
        """提取函数逻辑的详细信息"""
        logic_info = {
            'summary': [],
            'control_flow': [],
            'operations': [],
            'data_operations': [],
            'api_calls': [],
            'database_operations': [],
            'error_handling': []  # Add initialized key
        }
        
        for item in node.body:
            # 基本逻辑摘要
            if isinstance(item, ast.Return):
                logic_info['summary'].append({
                    'type': 'return',
                    'description': f"返回: {self._get_return_description(item)}"
                })
            elif isinstance(item, ast.If):
                logic_info['control_flow'].append({
                    'type': 'condition',
                    'test': ast.unparse(item.test),
                    'has_else': bool(item.orelse)
                })
            elif isinstance(item, ast.Assign):
                logic_info['data_operations'].append({
                    'type': 'assignment',
                    'target': ast.unparse(item.targets[0]),
                    'value': ast.unparse(item.value)
                })
            elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                call_info = self._analyze_function_call(item.value)
                if call_info['type'] == 'api':
                    logic_info['api_calls'].append(call_info)
                elif call_info['type'] == 'database':
                    logic_info['database_operations'].append(call_info)
                else:
                    logic_info['operations'].append(call_info)
            elif isinstance(item, ast.For):
                logic_info['control_flow'].append({
                    'type': 'loop',
                    'target': ast.unparse(item.target),
                    'iter': ast.unparse(item.iter)
                })
            elif isinstance(item, ast.While):
                logic_info['control_flow'].append({
                    'type': 'while_loop',
                    'test': ast.unparse(item.test)
                })
            elif isinstance(item, ast.Try):
                logic_info['error_handling'].append(self._analyze_try_except(item))
        
        return logic_info
    
    def _analyze_function_call(self, node: ast.Call) -> Dict:
        """分析函数调用"""
        call_info = {
            'name': '',
            'args': [],
            'keywords': {},
            'type': 'general'
        }
        
        try:
            # 获取函数名
            if isinstance(node.func, ast.Name):
                call_info['name'] = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # 使用 ast.unparse 来处理复杂的属性访问
                call_info['name'] = ast.unparse(node.func)
            else:
                # 处理其他类型的函数调用
                call_info['name'] = ast.unparse(node.func)
            
            # 分析参数
            call_info['args'] = [ast.unparse(arg) for arg in node.args]
            call_info['keywords'] = {
                kw.arg: ast.unparse(kw.value) for kw in node.keywords
            }
            
            # 判断调用类型
            name_lower = call_info['name'].lower()
            if any(api_pattern in name_lower 
                   for api_pattern in ['request', 'http', 'fetch', 'axios']):
                call_info['type'] = 'api'
            elif any(db_pattern in name_lower 
                    for db_pattern in ['query', 'insert', 'update', 'delete', 'select']):
                call_info['type'] = 'database'
            elif 'jwt' in name_lower or 'token' in name_lower:
                call_info['type'] = 'auth'
            elif 'log' in name_lower or 'print' in name_lower:
                call_info['type'] = 'logging'
            elif 'test' in name_lower or 'assert' in name_lower:
                call_info['type'] = 'testing'
            
        except Exception as e:
            # 如果解析失败，至少尝试获取一些基本信息
            call_info['name'] = ast.unparse(node)
            call_info['error'] = str(e)
        
        return call_info
    
    def _analyze_try_except(self, node: ast.Try) -> Dict:
        """分析try-except块"""
        return {
            'try_body': [ast.unparse(item) for item in node.body],
            'handlers': [{
                'type': handler.type.id if handler.type else 'Exception',
                'name': handler.name if handler.name else None,
                'body': [ast.unparse(item) for item in handler.body]
            } for handler in node.handlers],
            'has_finally': bool(node.finalbody),
            'has_else': bool(node.orelse)
        }
    
    def _analyze_function_flow(self, node: ast.FunctionDef) -> List[Dict]:
        """分析函数的执行流程"""
        flow = []
        
        for item in ast.walk(node):
            if isinstance(item, ast.If):
                flow.append({
                    'type': 'branch',
                    'condition': ast.unparse(item.test),
                    'then_branch': [ast.unparse(stmt) for stmt in item.body],
                    'else_branch': [ast.unparse(stmt) for stmt in item.orelse] if item.orelse else []
                })
            elif isinstance(item, (ast.For, ast.While)):
                flow.append({
                    'type': 'loop',
                    'setup': ast.unparse(item.target if isinstance(item, ast.For) else item.test),
                    'body': [ast.unparse(stmt) for stmt in item.body]
                })
            elif isinstance(item, ast.Try):
                flow.append({
                    'type': 'error_handling',
                    'try_block': [ast.unparse(stmt) for stmt in item.body],
                    'except_blocks': [{
                        'exception': handler.type.id if handler.type else 'Exception',
                        'handler': [ast.unparse(stmt) for stmt in handler.body]
                    } for handler in item.handlers]
                })
        
        return flow
    
    def _extract_variables(self, node: ast.FunctionDef) -> List[Dict]:
        """提取函数中的变量信息"""
        variables = []
        
        for item in ast.walk(node):
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            'name': target.id,
                            'value': ast.unparse(item.value),
                            'type': self._infer_variable_type(item.value)
                        })
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                variables.append({
                    'name': item.target.id,
                    'type': ast.unparse(item.annotation),
                    'value': ast.unparse(item.value) if item.value else None
                })
        
        return variables
    
    def _infer_variable_type(self, value_node: ast.AST) -> str:
        """推断变量类型"""
        if isinstance(value_node, ast.Constant):
            if isinstance(value_node.value, (int, float)):
                return 'number'
            elif isinstance(value_node.value, str):
                return 'string'
        elif isinstance(value_node, ast.List):
            return 'list'
        elif isinstance(value_node, ast.Dict):
            return 'dict'
        elif isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name):
                return value_node.func.id
            elif isinstance(value_node.func, ast.Attribute):
                return f"{ast.unparse(value_node.func.value)}.{value_node.func.attr}"
        return 'unknown'
    
    def _extract_function_imports(self, node: ast.FunctionDef, file_path: str) -> List[Dict]:
        """提取函数依赖的导入"""
        imports = []
        module = ast.Module(body=[], type_ignores=[])
        
        # 获取文件级别的导入
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                module = ast.parse(f.read())
        except Exception as e:
            print(f"Error reading file {file_path} for imports: {str(e)}")
            pass
        
        # 分析导入
        for item in ast.walk(module):
            if isinstance(item, ast.Import):
                for name in item.names:
                    imports.append({
                        'type': 'import',
                        'name': name.name,
                        'asname': name.asname
                    })
            elif isinstance(item, ast.ImportFrom):
                for name in item.names:
                    imports.append({
                        'type': 'from_import',
                        'module': item.module,
                        'name': name.name,
                        'asname': name.asname
                    })
        
        return imports
    
    def _analyze_error_handling(self, node: ast.FunctionDef) -> List[Dict]:
        """分析错误处理"""
        error_handling = []
        
        for item in ast.walk(node):
            if isinstance(item, ast.Try):
                error_info = {
                    'try_block': [ast.unparse(stmt) for stmt in item.body],
                    'handlers': []
                }
                
                for handler in item.handlers:
                    handler_info = {
                        'exception': handler.type.id if handler.type else 'Exception',
                        'variable': handler.name,
                        'body': [ast.unparse(stmt) for stmt in handler.body]
                    }
                    error_info['handlers'].append(handler_info)
                
                if item.finalbody:
                    error_info['finally'] = [ast.unparse(stmt) for stmt in item.finalbody]
                if item.orelse:
                    error_info['else'] = [ast.unparse(stmt) for stmt in item.orelse]
                
                error_handling.append(error_info)
        
        return error_handling
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> Dict:
        """计算函数的复杂度指标"""
        metrics = {
            'cyclomatic': 1,  # 基础复杂度
            'cognitive': 0,   # 认知复杂度
            'nesting': 0,    # 最大嵌套深度
            'statements': 0,  # 语句数量
            'parameters': len(node.args.args)  # 参数数量
        }
        
        def calculate_nesting(node, current_depth=0):
            max_depth = current_depth
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                current_depth += 1
                max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = calculate_nesting(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        # 计算圈复杂度
        for item in ast.walk(node):
            if isinstance(item, (ast.If, ast.While, ast.For)):
                metrics['cyclomatic'] += 1
            elif isinstance(item, ast.BoolOp) and isinstance(item.op, (ast.And, ast.Or)):
                metrics['cyclomatic'] += len(item.values) - 1
        
        # 计算认知复杂度
        for item in ast.walk(node):
            if isinstance(item, ast.If):
                metrics['cognitive'] += 1
                if item.orelse:
                    metrics['cognitive'] += 1
            elif isinstance(item, (ast.For, ast.While)):
                metrics['cognitive'] += 2
        
        # 计算最大嵌套深度
        metrics['nesting'] = calculate_nesting(node)
        
        # 计算语句数量
        for item in ast.walk(node):
            if isinstance(item, (ast.Assign, ast.AugAssign, ast.Return, ast.Expr)):
                metrics['statements'] += 1
        
        return metrics
    
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
            if arg.annotation and isinstance(arg.annotation, ast.Call):
                if isinstance(arg.annotation.func, ast.Name):
                    if arg.annotation.func.id == 'Depends':
                        param['type'] = f"Depends({ast.unparse(arg.annotation.args[0])})"
                elif isinstance(arg.annotation.func, ast.Attribute):
                    if arg.annotation.func.attr == 'Depends':
                        param['type'] = f"{ast.unparse(arg.annotation.func)}({ast.unparse(arg.annotation.args[0])})"
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
                is_pydantic_model = False
                
                # 检查是否继承自BaseModel（包括直接继承和从模块导入的情况）
                for base in node.bases:
                    # 直接使用BaseModel的情况
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        is_pydantic_model = True
                        break
                    # 使用pydantic.BaseModel的情况
                    elif isinstance(base, ast.Attribute) and base.attr == 'BaseModel':
                        is_pydantic_model = True
                        break
                
                if is_pydantic_model:
                    model_name = node.name
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
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
        try:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    return decorator.func.attr
                elif isinstance(decorator.func, ast.Name):
                    return decorator.func.id
                else:
                    # 处理更复杂的装饰器表达式
                    return ast.unparse(decorator.func)
            elif isinstance(decorator, ast.Attribute):
                return decorator.attr
            elif isinstance(decorator, ast.Name):
                return decorator.id
            return ast.unparse(decorator)
        except Exception:
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
                if decorator.args:
                    if isinstance(decorator.args[0], ast.Name):
                        if decorator.args[0].id == 'oauth2_scheme':
                            endpoint['security'].append('OAuth2')
                    elif isinstance(decorator.args[0], ast.Attribute):
                        auth_arg = ast.unparse(decorator.args[0])
                        if 'oauth2_scheme' in auth_arg:
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
        
        try:
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
            
        except Exception as e:
            print(f"Error analyzing React component {file_path}: {str(e)}")
            return {
                'file': file_path,
                'name': component_name,
                'error': str(e)
            }
    
    def _extract_react_imports(self, content: str) -> List[Dict]:
        """提取React组件的导入语句"""
        imports = []
        import_pattern = re.compile(r'import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]')
        
        for match in import_pattern.finditer(content):
            import_statement = match.group(1).strip()
            source = match.group(2)
            
            # 处理不同类型的导入
            if import_statement.startswith('{'):
                # 解构导入
                named_imports = [
                    imp.strip() 
                    for imp in import_statement.strip('{}').split(',')
                    if imp.strip()
                ]
                imports.append({
                    'type': 'named',
                    'imports': named_imports,
                    'source': source
                })
            elif import_statement.startswith('*'):
                # 命名空间导入
                imports.append({
                    'type': 'namespace',
                    'alias': import_statement.split('as')[1].strip() if 'as' in import_statement else '*',
                    'source': source
                })
            else:
                # 默认导入
                imports.append({
                    'type': 'default',
                    'name': import_statement,
                    'source': source
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

    def _extract_vue_computed(self, content: str) -> Dict:
        """提取Vue组件的计算属性"""
        computed = {}
        computed_section = self._extract_vue_section(content, 'computed')
        
        if computed_section:
            # 提取计算属性定义
            computed_matches = re.finditer(
                r'(\w+)\s*\(?\)\s*{\s*([^}]*)\s*}',
                computed_section,
                re.DOTALL
            )
            for match in computed_matches:
                property_name = match.group(1)
                property_body = match.group(2).strip()
                computed[property_name] = {
                    'body': property_body,
                    'dependencies': self._extract_computed_dependencies(property_body)
                }
    
        return computed

    def _extract_vue_watchers(self, content: str) -> List[Dict]:
        """提取Vue组件的侦听器"""
        watchers = []
        watch_section = self._extract_vue_section(content, 'watch')
        
        if watch_section:
            # 提取侦听器定义
            watcher_matches = re.finditer(
                r'(\w+)\s*:\s*{\s*handler\s*\(\s*([^)]*)\s*\)\s*{\s*([^}]*)\s*}(?:\s*,\s*immediate\s*:\s*(true|false))?(?:\s*,\s*deep\s*:\s*(true|false))?\s*}',
                watch_section,
                re.DOTALL
            )
            for match in watcher_matches:
                watchers.append({
                    'target': match.group(1),
                    'params': [p.strip() for p in match.group(2).split(',') if p.strip()],
                    'body': match.group(3).strip(),
                    'immediate': match.group(4) == 'true' if match.group(4) else False,
                    'deep': match.group(5) == 'true' if match.group(5) else False
                })
    
        return watchers

    def _extract_vue_lifecycle(self, content: str) -> List[Dict]:
        """提取Vue组件的生命周期钩子"""
        lifecycle_hooks = []
        lifecycle_methods = [
            'beforeCreate', 'created',
            'beforeMount', 'mounted',
            'beforeUpdate', 'updated',
            'beforeDestroy', 'destroyed',
            'errorCaptured'
        ]
        
        for hook in lifecycle_methods:
            hook_content = self._extract_vue_section(content, hook)
            if hook_content:
                lifecycle_hooks.append({
                    'name': hook,
                    'body': hook_content.strip()
                })
    
        return lifecycle_hooks

    def _extract_computed_dependencies(self, body: str) -> List[str]:
        """提取计算属性的依赖"""
        dependencies = []
        # 匹配 this. 开头的变量引用
        this_refs = re.finditer(r'this\.(\w+)', body)
        for match in this_refs:
            dependency = match.group(1)
            if dependency not in dependencies:
                dependencies.append(dependency)
        
        # 匹配 store. 开头的状态引用
        store_refs = re.finditer(r'(?:this\.|)store\.(?:state\.|getters\.|)(\w+)', body)
        for match in store_refs:
            dependency = f"store.{match.group(1)}"
            if dependency not in dependencies:
                dependencies.append(dependency)
        
        return dependencies

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
        """
        从Vue组件中提取指定的部分（如computed、methods、watch等）
        支持Options API和Composition API两种格式
        """
        # Options API格式
        options_pattern = rf'{section_name}\s*:\s*(\{{|\[)([^}}|\]]*?)(\}}|\])'
        options_match = re.search(options_pattern, content, re.DOTALL)
        if options_match:
            return options_match.group(2).strip()
        
        # Composition API格式
        composition_pattern = rf'(?:export\s+)?(?:async\s+)?function\s+{section_name}\s*\([^)]*\)\s*\{{([^}}]*?)\}}'
        composition_match = re.search(composition_pattern, content, re.DOTALL)
        if composition_match:
            return composition_match.group(1).strip()
        
        return ''

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




    def generate_full_documentation(self) -> Dict:
        """生成完整的项目文档"""
        return {
            'project_info': self._generate_project_info(),
            'project_structure': self._analyze_project_structure(),
            'frameworks': self.frameworks,  # 添加框架信息
            'api_documentation': self._generate_api_docs(),
            'backend_functions': self.backend_functions,
            'frontend_documentation': self._generate_frontend_docs(),
            'component_hierarchy': dict(self.component_hierarchy),
            'import_analysis': dict(self.import_analysis),
            'hook_usage': dict(self.hook_usage),
            'api_calls': self.api_calls,
            'state_management': dict(self.state_management),
            'k8s_configuration': self._generate_k8s_docs(),
            'k8s_panel_analysis': self._analyze_k8s_panel_specific(),
            'dependencies': self.dependencies,
            'code_quality': self._generate_code_quality_report(),
            'test_coverage': self._generate_test_coverage_report(),
            'routes': {
                'react': self.routes['react'],
                'fastapi': self.routes['fastapi'],
                'websocket': self.websocket_endpoints
            },
            'configurations': {
                'env': self.env_configs,
                'nginx': self.nginx_config
            },
            'terminal': {
                'xterm_components': self.xterm_components
            }
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
        
        # 将所有Markdown格式的文档内容添加到JSON中
        full_docs['markdown_content'] = {
            'api_docs': self._generate_api_docs_md(),
            'k8s_docs': self._generate_k8s_docs_md(),
            'code_quality_report': self._generate_code_quality_report_md(),
            'project_structure': self._generate_structure_md(),
            'k8s_panel_analysis': self._generate_panel_analysis_md()
        }
        
        # 保存为单个JSON文件
        with open(os.path.join(self.output_dir, 'full_documentation.json'), 'w', encoding='utf-8') as f:
            json.dump(full_docs, f, indent=2, ensure_ascii=False)
            
    def _generate_structure_md(self) -> str:
        """生成项目结构Markdown文档"""
        structure = self._analyze_project_structure()
        docs = ["# 项目结构文档\n\n"]
        
        # 文件类型统计
        docs.append("## 文件类型统计\n")
        for ext, count in sorted(structure['file_types'].items()):
            docs.append(f"- {ext or '(无扩展名)'}: {count}个文件\n")
        
        # 特殊文件列表
        docs.append("\n## 特殊文件\n")
        for category, files in structure['special_files'].items():
            if files:
                docs.append(f"\n### {category.replace('_', ' ').title()}\n")
                for file in sorted(files):
                    docs.append(f"- {file}\n")
        
        # 目录结构
        docs.append("\n## 目录结构\n")
        for dir_path, files in sorted(structure['directories'].items()):
            if not dir_path:
                docs.append("\n### 根目录\n")
            else:
                docs.append(f"\n### /{dir_path}\n")
            for file in sorted(files):
                docs.append(f"- {file}\n")
        
        return "".join(docs)
    
    def _generate_panel_analysis_md(self) -> str:
        """生成K8S面板分析Markdown文档"""
        analysis = self._analyze_k8s_panel_specific()
        docs = ["# K8S资源面板分析\n\n"]
        
        # 资源类型
        docs.append("## 支持的资源类型\n")
        for resource_type in sorted(analysis['resource_types']):
            docs.append(f"- {resource_type}\n")
        
        # UI组件
        docs.append("\n## UI组件\n")
        for component in analysis['ui_components']:
            docs.append(f"### {component['name']}\n")
            docs.append(f"处理的资源类型: {', '.join(component['resource_types'])}\n")
            if component['api_dependencies']:
                docs.append("\nAPI依赖:\n")
                for api in component['api_dependencies']:
                    docs.append(f"- {api['method']} {api['url']}\n")
            if component['state_management']:
                docs.append("\n状态管理:\n")
                for state in component['state_management']:
                    docs.append(f"- {state['name']}: {state['type']}\n")
            docs.append("\n")
        
        # API端点
        docs.append("## API端点\n")
        for endpoint in analysis['api_endpoints']:
            docs.append(f"### {endpoint['method']} {endpoint['path']}\n")
            docs.append(f"处理函数: {endpoint['handler']}\n")
            if endpoint['params']:
                docs.append("\n参数:\n")
                for param in endpoint['params']:
                    docs.append(f"- {param['name']}: {param['type']}\n")
            docs.append("\n")
        
        # 数据模型
        docs.append("## 数据模型\n")
        for model in analysis['data_models']:
            docs.append(f"### {model['name']}\n")
            if model['fields']:
                docs.append("\n字段:\n")
                for field in model['fields']:
                    docs.append(f"- {field['name']}: {field['type']}")
                    if field['description']:
                        docs.append(f" - {field['description']}")
                    docs.append("\n")
            docs.append("\n")
        
        # 集群配置
        docs.append("## 集群配置\n")
        for config in analysis['cluster_configs']:
            docs.append(f"### {config['type']}: {config['name']}\n")
            docs.append(f"命名空间: {config['namespace']}\n")
            if config['spec']:
                docs.append("\n规格:\n")
                docs.append(f"```yaml\n{json.dumps(config['spec'], indent=2)}\n```\n")
            docs.append("\n")
        
        return "".join(docs)

    def _generate_k8s_docs(self) -> Dict:
        """生成 K8S 配置文档"""
        k8s_docs = {
            'resources': [],
            'dependencies': defaultdict(list),
            'summary': {
                'total_resources': len(self.k8s_configs),
                'resource_types': defaultdict(int)
            }
        }
        
        for config in self.k8s_configs:
            resource_type = config['type']
            k8s_docs['summary']['resource_types'][resource_type] += 1
            
            resource_doc = {
                'file': config['file'],
                'type': resource_type,
                'name': config['metadata'].get('name', ''),
                'namespace': config['metadata'].get('namespace', 'default'),
                'labels': config['metadata'].get('labels', {}),
                'annotations': config['metadata'].get('annotations', {}),
                'spec_summary': self._summarize_k8s_spec(config['spec']),
                'dependencies': config['dependencies']
            }
            
            k8s_docs['resources'].append(resource_doc)
            
            # 记录依赖关系
            for dep in config['dependencies']:
                k8s_docs['dependencies'][resource_type].append(dep)
        
        return k8s_docs
    
    def _summarize_k8s_spec(self, spec: Dict) -> Dict:
        """总结 K8S 资源规格"""
        summary = {}
        
        if 'replicas' in spec:
            summary['replicas'] = spec['replicas']
        
        if 'containers' in spec:
            summary['containers'] = [
                {
                    'name': container.get('name', ''),
                    'image': container.get('image', ''),
                    'resources': container.get('resources', {})
                }
                for container in spec['containers']
            ]
        
        if 'selector' in spec:
            summary['selector'] = spec['selector']
            
        return summary
    
    def _generate_code_quality_report(self) -> Dict:
        """生成代码质量报告"""
        report = {
            'summary': {
                'total_files': len(self.code_metrics),
                'total_lines': sum(m['total_lines'] for m in self.code_metrics.values()),
                'total_code_lines': sum(m['code_lines'] for m in self.code_metrics.values()),
                'total_comment_lines': sum(m['comment_lines'] for m in self.code_metrics.values()),
                'average_complexity': sum(m['complexity'] for m in self.code_metrics.values()) / len(self.code_metrics) if self.code_metrics else 0
            },
            'files': self.code_metrics,
            'high_complexity_files': [
                {'file': file, 'complexity': metrics['complexity']}
                for file, metrics in self.code_metrics.items()
                if metrics['complexity'] > 10  # 复杂度阈值
            ]
        }
        
        return report
    
    def _generate_test_coverage_report(self) -> Dict:
        """生成测试覆盖率报告"""
        report = {
            'summary': {
                'total_test_files': len(self.test_coverage),
                'total_test_cases': sum(info['total_tests'] for info in self.test_coverage.values()),
                'total_assertions': sum(
                    sum(case['assertions'] for case in info['test_cases'])
                    for info in self.test_coverage.values()
                )
            },
            'test_files': self.test_coverage
        }
        
        return report
    
    def _generate_k8s_docs_md(self) -> str:
        """生成Markdown格式的K8S文档"""
        docs = ["# Kubernetes 资源配置文档\n\n"]
        
        # 添加概述
        docs.append("## 资源概述\n")
        k8s_info = self._generate_k8s_docs()
        for resource_type, count in k8s_info['summary']['resource_types'].items():
            docs.append(f"- {resource_type}: {count}个\n")
        
        # 添加详细资源信息
        docs.append("\n## 资源详情\n")
        for resource in k8s_info['resources']:
            docs.append(f"### {resource['type']}: {resource['name']}\n")
            docs.append(f"- 命名空间: {resource['namespace']}\n")
            if resource['labels']:
                docs.append("- 标签:\n")
                for key, value in resource['labels'].items():
                    docs.append(f"  - {key}: {value}\n")
            if resource['dependencies']:
                docs.append("- 依赖:\n")
                for dep in resource['dependencies']:
                    docs.append(f"  - {dep}\n")
            docs.append("\n")
        
        return "".join(docs)
    
    def _generate_code_quality_report_md(self) -> str:
        """生成Markdown格式的代码质量报告"""
        report = ["# 代码质量报告\n\n"]
        
        # 添加总体统计
        quality_info = self._generate_code_quality_report()
        report.append("## 总体统计\n")
        report.append(f"- 总文件数: {quality_info['summary']['total_files']}\n")
        report.append(f"- 总代码行数: {quality_info['summary']['total_code_lines']}\n")
        report.append(f"- 总注释行数: {quality_info['summary']['total_comment_lines']}\n")
        report.append(f"- 平均复杂度: {quality_info['summary']['average_complexity']:.2f}\n\n")
        
        # 添加高复杂度文件警告
        if quality_info['high_complexity_files']:
            report.append("## 高复杂度文件\n")
            for file_info in quality_info['high_complexity_files']:
                report.append(f"- {file_info['file']}: 复杂度 {file_info['complexity']}\n")
        
        return "".join(report)

    def _analyze_k8s_configs(self, file_path: str):
        """分析 Kubernetes 配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        config_info = {
            'file': file_path,
            'type': self._determine_k8s_resource_type(content),
            'metadata': self._extract_k8s_metadata(content),
            'spec': self._extract_k8s_spec(content),
            'dependencies': self._extract_k8s_dependencies(content)
        }
        
        self.k8s_configs.append(config_info)
    
    def _determine_k8s_resource_type(self, content: str) -> str:
        """确定 K8S 资源类型"""
        try:
            import yaml
            config = yaml.safe_load(content)
            return config.get('kind', 'Unknown')
        except:
            return 'Unknown'
    
    def _extract_k8s_metadata(self, content: str) -> Dict:
        """提取 K8S 资源元数据"""
        try:
            import yaml
            config = yaml.safe_load(content)
            return config.get('metadata', {})
        except:
            return {}
    
    def _extract_k8s_spec(self, content: str) -> Dict:
        """提取 K8S 资源规格"""
        try:
            import yaml
            config = yaml.safe_load(content)
            return config.get('spec', {})
        except:
            return {}
    
    def _extract_k8s_dependencies(self, content: str) -> List[str]:
        """提取 K8S 资源依赖"""
        dependencies = []
        try:
            import yaml
            config = yaml.safe_load(content)
            
            # 检查 ConfigMap 依赖
            if 'configMapRef' in str(config):
                dependencies.extend(self._find_configmap_refs(config))
            
            # 检查 Secret 依赖
            if 'secretRef' in str(config):
                dependencies.extend(self._find_secret_refs(config))
            
            # 检查 Service 依赖
            if 'serviceName' in str(config):
                dependencies.extend(self._find_service_refs(config))
                
        except:
            pass
        return dependencies
    
    def _find_configmap_refs(self, config: Dict) -> List[str]:
        """查找 ConfigMap 引用"""
        refs = []
        if isinstance(config, dict):
            if 'configMapRef' in config:
                refs.append(config['configMapRef'].get('name', ''))
            for value in config.values():
                refs.extend(self._find_configmap_refs(value))
        elif isinstance(config, list):
            for item in config:
                refs.extend(self._find_configmap_refs(item))
        return [ref for ref in refs if ref]
    
    def _find_secret_refs(self, config: Dict) -> List[str]:
        """查找 Secret 引用"""
        refs = []
        if isinstance(config, dict):
            if 'secretRef' in config:
                refs.append(config['secretRef'].get('name', ''))
            for value in config.values():
                refs.extend(self._find_secret_refs(value))
        elif isinstance(config, list):
            for item in config:
                refs.extend(self._find_secret_refs(item))
        return [ref for ref in refs if ref]
    
    def _find_service_refs(self, config: Dict) -> List[str]:
        """查找 Service 引用"""
        refs = []
        if isinstance(config, dict):
            if 'serviceName' in config:
                refs.append(config['serviceName'])
            for value in config.values():
                refs.extend(self._find_service_refs(value))
        elif isinstance(config, list):
            for item in config:
                refs.extend(self._find_service_refs(item))
        return [ref for ref in refs if ref]

    def _analyze_dependencies(self):
        """分析项目依赖关系"""
        # 分析 Python 依赖
        requirements_file = os.path.join(self.repo_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r', encoding='utf-8') as f:
                self.dependencies['python'] = [
                    line.strip() for line in f.readlines()
                    if line.strip() and not line.startswith('#')
                ]
        
        # 分析 Node.js 依赖
        package_json = os.path.join(self.repo_path, 'package.json')
        if os.path.exists(package_json):
            with open(package_json, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.dependencies['node'] = {
                        'dependencies': data.get('dependencies', {}),
                        'devDependencies': data.get('devDependencies', {})
                    }
                except json.JSONDecodeError:
                    print(f"Error parsing package.json")
    
    def _analyze_code_quality(self, file_path: str):
        """分析代码质量指标"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'empty_lines': len([l for l in lines if not l.strip()]),
            'complexity': self._calculate_complexity(content)
        }
        
        self.code_metrics[file_path] = metrics
    
    def _calculate_complexity(self, content: str) -> int:
        """计算代码复杂度（圈复杂度）"""
        complexity = 1  # 基础复杂度
        
        # 计算条件语句和循环
        keywords = ['if', 'elif', 'for', 'while', 'except', 'with', 'and', 'or']
        for keyword in keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content))
            
        return complexity
    
    def _analyze_test_coverage(self):
        """分析测试覆盖率"""
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            test_path = os.path.join(self.repo_path, test_dir)
            if os.path.exists(test_path):
                for root, _, files in os.walk(test_path):
                    for file in files:
                        if file.startswith('test_') and file.endswith('.py'):
                            self._analyze_test_file(os.path.join(root, file))
    
    def _analyze_test_file(self, file_path: str):
        """分析测试文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            test_cases = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (
                    node.name.startswith('test_') or
                    any(base.id == 'TestCase' for base in getattr(node, 'bases', []))
                ):
                    test_cases.append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "",
                        'assertions': len([n for n in ast.walk(node) 
                                        if isinstance(n, ast.Call) and 
                                        any(n.func.id.startswith('assert') for n in ast.walk(n.func)
                                        if isinstance(n, ast.Name))])
                    })
            
            self.test_coverage[file_path] = {
                'test_cases': test_cases,
                'total_tests': len(test_cases)
            }
        except Exception as e:
            print(f"Error analyzing test file {file_path}: {str(e)}")

    def _is_k8s_file(self, file_path: str) -> bool:
        """判断是否为 K8S 配置文件"""
        if not file_path.endswith(('.yaml', '.yml')):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import yaml
                config = yaml.safe_load(content)
                return isinstance(config, dict) and 'apiVersion' in config and 'kind' in config
        except:
            return False

    def _analyze_project_structure(self):
        """分析项目结构"""
        structure = {
            'root': self.repo_path,
            'directories': defaultdict(list),
            'file_types': defaultdict(int),
            'special_files': {
                'k8s_configs': [],
                'docker_files': [],
                'ci_cd_files': [],
                'package_files': [],
                'test_files': [],
                'docs': []
            }
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            rel_path = os.path.relpath(root, self.repo_path)
            if rel_path == '.':
                rel_path = ''
                
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file)
                
                # 记录文件类型
                ext = os.path.splitext(file)[1].lower()
                structure['file_types'][ext] += 1
                
                # 分类特殊文件
                if file.endswith(('.yaml', '.yml')) and self._is_k8s_file(file_path):
                    structure['special_files']['k8s_configs'].append(rel_file_path)
                elif file.startswith('Dockerfile') or file.endswith('.dockerfile'):
                    structure['special_files']['docker_files'].append(rel_file_path)
                elif file in ['.gitlab-ci.yml', '.github/workflows/main.yml', 'jenkins.groovy']:
                    structure['special_files']['ci_cd_files'].append(rel_file_path)
                elif file in ['package.json', 'requirements.txt', 'setup.py']:
                    structure['special_files']['package_files'].append(rel_file_path)
                elif file.startswith('test_') or file.endswith('_test.py'):
                    structure['special_files']['test_files'].append(rel_file_path)
                elif file.endswith(('.md', '.rst', '.txt')):
                    structure['special_files']['docs'].append(rel_file_path)
                
                # 添加到目录结构
                structure['directories'][rel_path].append(file)
        
        return structure

    def _analyze_k8s_panel_specific(self):
        """分析K8S资源面板特定功能"""
        panel_analysis = {
            'resource_types': set(),  # 临时使用set进行去重
            'api_endpoints': [],
            'ui_components': [],
            'data_models': [],
            'cluster_configs': []
        }
        
        # 分析前端组件中的资源类型
        for component in self.frontend_functions:
            if 'resource' in component['name'].lower() or 'k8s' in component['name'].lower():
                # 提取组件处理的资源类型
                resource_types = self._extract_resource_types_from_component(component)
                panel_analysis['resource_types'].update(resource_types)
                panel_analysis['ui_components'].append({
                    'name': component['name'],
                    'resource_types': list(resource_types),  # 转换为list
                    'api_dependencies': component.get('api_calls', []),
                    'state_management': component.get('state_vars', [])
                })
        
        # 分析后端API端点
        for endpoint in self.api_endpoints:
            if 'k8s' in endpoint['path'].lower() or 'cluster' in endpoint['path'].lower():
                panel_analysis['api_endpoints'].append({
                    'path': endpoint['path'],
                    'method': endpoint['method'],
                    'handler': endpoint['function_name'],
                    'params': endpoint['params']
                })
        
        # 分析数据模型
        for func in self.backend_functions:
            if isinstance(func, dict) and 'class' in func:
                if 'model' in func['class'].lower() and ('resource' in func['class'].lower() or 'k8s' in func['class'].lower()):
                    panel_analysis['data_models'].append({
                        'name': func['class'],
                        'fields': self._extract_model_fields(func)
                    })
        
        # 分析集群配置
        for config in self.k8s_configs:
            if config['type'] in ['Deployment', 'Service', 'ConfigMap']:
                panel_analysis['cluster_configs'].append({
                    'type': config['type'],
                    'name': config['metadata'].get('name', ''),
                    'namespace': config['metadata'].get('namespace', 'default'),
                    'spec': self._summarize_k8s_spec(config['spec'])
                })
        
        # 在返回之前将resource_types转换为list
        panel_analysis['resource_types'] = sorted(list(panel_analysis['resource_types']))
        return panel_analysis
    
    def _extract_resource_types_from_component(self, component: Dict) -> List[str]:
        """从组件中提取处理的资源类型"""
        resource_types = set()  # 临时使用set进行去重
        
        # 从组件名称中提取
        name = component['name'].lower()
        k8s_resources = ['pod', 'deployment', 'service', 'configmap', 'secret', 'namespace', 
                        'node', 'ingress', 'volume', 'persistentvolume', 'persistentvolumeclaim']
        
        for resource in k8s_resources:
            if resource in name:
                resource_types.add(resource.title())
        
        # 从代码内容中提取
        if 'api_calls' in component:
            for call in component['api_calls']:
                url = call['url'].lower()
                for resource in k8s_resources:
                    if resource in url:
                        resource_types.add(resource.title())
        
        return sorted(list(resource_types))  # 返回排序后的list
    
    def _extract_model_fields(self, func: Dict) -> List[Dict]:
        """提取模型字段信息"""
        fields = []
        if 'params' in func:
            for param in func['params']:
                fields.append({
                    'name': param['name'],
                    'type': param['type'],
                    'required': param.get('required', True),
                    'description': param.get('description', '')
                })
        return fields

    def _analyze_react_router(self, content: str, file_path: str):
        """分析React Router路由配置"""
        routes = []
        
        # 分析Route组件
        route_pattern = re.compile(
            r'<Route\s+(?:path=[\'"]([^\'"]+)[\'"])?\s*(?:element={([^}]+)})?'
        )
        
        # 分析useNavigate和useLocation hooks
        navigation_hooks = re.compile(
            r'(?:const|let|var)\s+(\w+)\s*=\s*use(?:Navigate|Location)\(\)'
        )
        
        # 分析路由配置对象
        router_config = re.compile(
            r'const\s+(\w+)\s*=\s*\[\s*{([^}]+)}\s*\]'
        )
        
        for match in route_pattern.finditer(content):
            path = match.group(1)
            element = match.group(2)
            if path or element:
                routes.append({
                    'type': 'component_route',
                    'path': path,
                    'element': element,
                    'file': file_path
                })
        
        # 添加到routes集合
        if routes:
            self.routes['react'].extend(routes)

    def _analyze_websocket_endpoint(self, node: ast.FunctionDef, file_path: str):
        """分析WebSocket端点"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr') and decorator.func.attr == 'websocket':
                    endpoint = {
                        'file': file_path,
                        'function_name': node.name,
                        'path': self._get_websocket_path(decorator),
                        'params': self._extract_parameters(node),
                        'docstring': ast.get_docstring(node) or "",
                        'handlers': self._extract_websocket_handlers(node)
                    }
                    self.websocket_endpoints.append(endpoint)

    def _extract_websocket_handlers(self, node: ast.FunctionDef) -> Dict:
        """提取WebSocket处理函数的信息"""
        handlers = {
            'on_connect': False,
            'on_disconnect': False,
            'on_message': False
        }
        
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Attribute):
                    method = item.func.attr
                    if method in handlers:
                        handlers[method] = True
        
        return handlers

    def _get_websocket_path(self, decorator: ast.Call) -> str:
        """获取WebSocket路径"""
        if decorator.args:
            return ast.unparse(decorator.args[0]).strip("'").strip('"')
        return "/"

    def _analyze_env_config(self, file_path: str):
        """分析环境变量配置文件"""
        if not file_path.endswith(('.env', '.env.development', '.env.production')):
            return
        
        env_type = os.path.basename(file_path).replace('.env.', '')
        if env_type == '.env':
            env_type = 'default'
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        self.env_configs[env_type] = config

    def _analyze_nginx_config(self, file_path: str):
        """分析nginx配置文件"""
        if not file_path.endswith('nginx.conf'):
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {
            'server_blocks': [],
            'locations': [],
            'upstream': [],
            'general_settings': {}
        }
        
        # 分析server块
        server_blocks = re.finditer(
            r'server\s*{([^}]+)}',
            content,
            re.DOTALL
        )
        
        for block in server_blocks:
            listen_match = re.search(r'listen\s+([^;]+);', block.group(1))
            server_name_match = re.search(r'server_name\s+([^;]+);', block.group(1))
            root_match = re.search(r'root\s+([^;]+);', block.group(1))
            
            server_config = {
                'listen': listen_match.group(1) if listen_match else None,
                'server_name': server_name_match.group(1) if server_name_match else None,
                'root': root_match.group(1) if root_match else None
            }
            config['server_blocks'].append(server_config)
        
        # 分析location块
        locations = re.finditer(
            r'location\s+([^{]+){([^}]+)}',
            content,
            re.DOTALL
        )
        
        for loc in locations:
            config['locations'].append({
                'path': loc.group(1).strip(),
                'config': loc.group(2).strip()
            })
        
        # 分析upstream块
        upstreams = re.finditer(
            r'upstream\s+([^{]+){([^}]+)}',
            content,
            re.DOTALL
        )
        
        for up in upstreams:
            config['upstream'].append({
                'name': up.group(1).strip(),
                'servers': re.findall(r'server\s+([^;]+);', up.group(2))
            })
        
        self.nginx_config = config

    def _analyze_xterm_component(self, content: str, file_path: str):
        """分析xterm终端组件"""
        if 'xterm' not in content.lower():
            return
        
        component = {
            'file': file_path,
            'addons': [],
            'options': {},
            'event_handlers': []
        }
        
        # 分析xterm插件
        addon_pattern = re.compile(
            r'import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]@xterm/addon-([^\'"]+)[\'"]'
        )
        
        for match in addon_pattern.finditer(content):
            component['addons'].append({
                'name': match.group(2),
                'imports': [imp.strip() for imp in match.group(1).split(',')]
            })
        
        # 分析xterm配置选项
        options_pattern = re.compile(
            r'new\s+Terminal\s*\(({[^}]+})\)'
        )
        
        for match in options_pattern.finditer(content):
            options_str = match.group(1)
            # 解析配置对象
            options = {}
            for option in re.finditer(r'(\w+):\s*([^,}]+)', options_str):
                options[option.group(1)] = option.group(2).strip()
            component['options'] = options
        
        # 分析事件处理器
        event_pattern = re.compile(
            r'terminal\.on\([\'"](\w+)[\'"]\s*,\s*([^)]+)\)'
        )
        
        for match in event_pattern.finditer(content):
            component['event_handlers'].append({
                'event': match.group(1),
                'handler': match.group(2).strip()
            })
        
        # 分析WebSocket连接
        ws_pattern = re.compile(
            r'new\s+WebSocket\([\'"]([^\'"]+)[\'"]\)'
        )
        
        for match in ws_pattern.finditer(content):
            component['websocket_url'] = match.group(1)
        
        self.xterm_components.append(component)

    def _analyze_frontend_routes(self, file_path: str):
        """分析前端路由配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 分析 React Router 路由
        route_pattern = re.compile(
            r'<Route\s+(?:path=[\'"]([^\'"]+)[\'"])?\s*(?:element={([^}]+)})?'
        )
        
        for match in route_pattern.finditer(content):
            path = match.group(1)
            element = match.group(2)
            if path:
                route_info = {
                    'path': path,
                    'component': element.strip() if element else None,
                    'file': file_path,
                    'auth_required': 'RequireAuth' in content,
                    'params': self._extract_route_params(path)
                }
                
                if 'login' in path.lower():
                    self.route_analysis['frontend']['auth_routes'].append(route_info)
                elif any(resource in path.lower() for resource in ['pod', 'deployment', 'service', 'configmap', 'secret']):
                    self.route_analysis['frontend']['resource_routes'].append(route_info)
                else:
                    self.route_analysis['frontend']['base_routes'].append(route_info)

    def _analyze_backend_routes(self, file_path: str):
        """分析后端路由配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            
            # 分析 FastAPI 路由装饰器
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    route_info = self._extract_fastapi_route(node, file_path)
                    if route_info:
                        if 'auth' in route_info['path'].lower():
                            self.route_analysis['backend']['auth_routes'].append(route_info)
                        elif 'ws' in route_info['method'].lower():
                            self.route_analysis['backend']['websocket_routes'].append(route_info)
                        elif any(resource in route_info['path'].lower() for resource in ['pod', 'deployment', 'service', 'configmap', 'secret']):
                            self.route_analysis['backend']['resource_routes'].append(route_info)
                        else:
                            self.route_analysis['backend']['api_routes'].append(route_info)
                            
        except SyntaxError as e:
            print(f"Python语法错误在 {file_path}: {str(e)}")

    def _extract_fastapi_route(self, node: ast.FunctionDef, file_path: str) -> Optional[Dict]:
        """提取 FastAPI 路由信息"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr') and decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch', 'websocket']:
                    return {
                        'path': self._get_route_path(decorator),
                        'method': decorator.func.attr.upper(),
                        'function': node.name,
                        'file': file_path,
                        'auth_required': self._has_auth_dependency(node),
                        'params': self._extract_function_params(node)
                    }
        return None

    def _extract_route_params(self, path: str) -> List[str]:
        """提取路由参数"""
        return re.findall(r'{([^}]+)}', path)

    def _has_auth_dependency(self, node: ast.FunctionDef) -> bool:
        """检查是否有认证依赖"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'Depends':
                    return True
        return False

    def _analyze_route_matching(self):
        """分析前后端路由匹配度"""
        # 分析资源路由匹配
        for frontend_route in self.route_analysis['frontend']['resource_routes']:
            matched = False
            for backend_route in self.route_analysis['backend']['resource_routes']:
                if self._routes_match(frontend_route, backend_route):
                    self.route_analysis['matching']['route_pairs'].append({
                        'frontend': frontend_route,
                        'backend': backend_route,
                        'match_type': 'resource'
                    })
                    matched = True
                    break
            if not matched:
                self.route_analysis['matching']['unmatched_frontend'].append(frontend_route)

        # 分析认证路由匹配
        for frontend_route in self.route_analysis['frontend']['auth_routes']:
            matched = False
            for backend_route in self.route_analysis['backend']['auth_routes']:
                if self._routes_match(frontend_route, backend_route):
                    self.route_analysis['matching']['route_pairs'].append({
                        'frontend': frontend_route,
                        'backend': backend_route,
                        'match_type': 'auth'
                    })
                    matched = True
                    break
            if not matched:
                self.route_analysis['matching']['unmatched_frontend'].append(frontend_route)

        # 计算匹配分数
        total_routes = len(self.route_analysis['frontend']['resource_routes']) + \
                      len(self.route_analysis['frontend']['auth_routes'])
        matched_routes = len(self.route_analysis['matching']['route_pairs'])
        
        if total_routes > 0:
            self.route_analysis['matching']['match_score'] = matched_routes / total_routes * 100

    def _routes_match(self, frontend_route: Dict, backend_route: Dict) -> bool:
        """判断前后端路由是否匹配"""
        # 提取路由路径的关键部分
        frontend_path = frontend_route['path'].lower().replace('-', '').replace('_', '')
        backend_path = backend_route['path'].lower().replace('-', '').replace('_', '')
        
        # 移除API前缀
        backend_path = backend_path.replace('/api/', '/')
        
        # 标准化参数
        frontend_path = re.sub(r':[^/]+', '{param}', frontend_path)
        backend_path = re.sub(r'{[^}]+}', '{param}', backend_path)
        
        # 检查路径匹配
        path_match = frontend_path in backend_path or backend_path in frontend_path
        
        # 检查认证要求匹配
        auth_match = frontend_route['auth_required'] == backend_route['auth_required']
        
        return path_match and auth_match

    def _analyze_directory_structure(self):
        """分析目录结构"""
        for root, dirs, files in os.walk(self.repo_path):
            rel_path = os.path.relpath(root, self.repo_path)
            
            # 前端目录分析
            if 'frontend' in rel_path:
                if 'components' in rel_path:
                    self.directory_analysis['frontend']['components'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'pages' in rel_path:
                    self.directory_analysis['frontend']['pages'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'services' in rel_path:
                    self.directory_analysis['frontend']['services'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'utils' in rel_path:
                    self.directory_analysis['frontend']['utils'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'styles' in rel_path:
                    self.directory_analysis['frontend']['styles'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
            
            # 后端目录分析
            elif 'backend' in rel_path:
                if 'api' in rel_path:
                    self.directory_analysis['backend']['api'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'services' in rel_path:
                    self.directory_analysis['backend']['services'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'models' in rel_path:
                    self.directory_analysis['backend']['models'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'utils' in rel_path:
                    self.directory_analysis['backend']['utils'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )
                elif 'core' in rel_path:
                    self.directory_analysis['backend']['core'].extend(
                        [os.path.join(rel_path, f) for f in files]
                    )

        # 计算目录结构匹配分数
        self._calculate_directory_match_score()
        
    def _calculate_directory_match_score(self):
        """计算目录结构匹配分数"""
        # 检查关键目录的存在
        key_directories = {
            'frontend': ['components', 'services', 'utils'],
            'backend': ['api', 'services', 'utils']
        }
        existing_directories = 0
        total_directories = len(key_directories['frontend'])
        
        for directory in key_directories['frontend']:
            if (self.directory_analysis['frontend'][directory] and 
                self.directory_analysis['backend'][key_directories['backend'][key_directories['frontend'].index(directory)]]):
                existing_directories += 1
                
        # 计算匹配分数
        if total_directories > 0:
            self.directory_analysis['matching']['structure_score'] = \
                (existing_directories / total_directories) * 100
            
        # 生成改进建议
        self._generate_directory_suggestions()
        
    def _generate_directory_suggestions(self):
        """生成目录结构改进建议"""
        suggestions = []
        
        # 检查前端目录
        if not self.directory_analysis['frontend']['components']:
            suggestions.append("建议在前端创建 components 目录存放可复用组件")
        if not self.directory_analysis['frontend']['pages']:
            suggestions.append("建议在前端创建 pages 目录存放页面组件")
        if not self.directory_analysis['frontend']['services']:
            suggestions.append("建议在前端创建 services 目录管理 API 调用")
            
        # 检查后端目录
        if not self.directory_analysis['backend']['api']:
            suggestions.append("建议在后端创建 api 目录管理路由")
        if not self.directory_analysis['backend']['services']:
            suggestions.append("建议在后端创建 services 目录管理业务逻辑")
        if not self.directory_analysis['backend']['models']:
            suggestions.append("建议在后端创建 models 目录管理数据模型")
            
        self.directory_analysis['matching']['suggestions'] = suggestions

    def _analyze_frontend_files(self):
        """分析前端文件"""
        for root, _, files in os.walk(os.path.join(self.repo_path, 'frontend')):
            # 跳过 node_modules
            if 'node_modules' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if self._is_frontend_file(file_path):
                        self._analyze_frontend_file(file_path)
                        self._analyze_code_quality(file_path)
                        
                        # 分析组件
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self._analyze_react_router(content, file_path)
                            self._analyze_xterm_component(content, file_path)
                except Exception as e:
                    print(f"分析前端文件 {file_path} 时出错: {str(e)}")

    def _analyze_backend_files(self):
        """分析后端文件"""
        for root, _, files in os.walk(os.path.join(self.repo_path, 'backend')):
            # 跳过虚拟环境
            if 'venv' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if self._is_backend_file(file_path):
                        self._analyze_backend_file(file_path)
                        self._analyze_code_quality(file_path)
                    elif file.endswith(('.yaml', '.yml')) and self._is_k8s_file(file_path):
                        self._analyze_k8s_configs(file_path)
                    elif file.endswith('.env') or file.startswith('.env.'):
                        self._analyze_env_config(file_path)
                    elif file == 'nginx.conf':
                        self._analyze_nginx_config(file_path)
                except Exception as e:
                    print(f"分析后端文件 {file_path} 时出错: {str(e)}")

    def _get_route_path(self, decorator: ast.Call) -> str:
        """从装饰器中提取路由路径"""
        for arg in decorator.args:
            if isinstance(arg, ast.Str):
                return arg.s
        for keyword in decorator.keywords:
            if keyword.arg == 'path' and isinstance(keyword.value, ast.Str):
                return keyword.value.s
        return '/'

    def _extract_function_params(self, node: ast.FunctionDef) -> List[str]:
        """提取函数参数"""
        params = []
        for arg in node.args.args:
            if arg.arg != 'self':
                params.append(arg.arg)
        return params

    def _extract_responses(self, node: ast.FunctionDef) -> List[Dict]:
        """提取API响应信息"""
        responses = []
        
        # 从返回类型注解中提取响应类型
        if node.returns:
            response_type = ast.unparse(node.returns)
            responses.append({
                'status_code': 200,  # 默认成功状态码
                'type': response_type,
                'description': '成功响应'
            })
        
        # 从函数体中提取错误响应
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Name) and item.func.id == 'HTTPException':
                    status_code = None
                    detail = None
                    
                    for kw in item.keywords:
                        if kw.arg == 'status_code':
                            if isinstance(kw.value, ast.Num):
                                status_code = kw.value.n
                        elif kw.arg == 'detail':
                            if isinstance(kw.value, ast.Str):
                                detail = kw.value.s
                            elif isinstance(kw.value, ast.JoinedStr):  # f-string
                                detail = ast.unparse(kw.value)
                        
                    if status_code:
                        responses.append({
                            'status_code': status_code,
                            'type': 'HTTPException',
                            'description': detail or f'HTTP {status_code} 错误'
                        })
        
        # 如果没有找到任何响应，添加默认响应
        if not responses:
            responses.append({
                'status_code': 200,
                'type': 'Any',
                'description': '默认响应'
            })
        
        return responses

    def _get_string_value(self, node: ast.AST) -> str:
        """从AST节点中提取字符串值"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.JoinedStr):
            # 处理 f-string
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    parts.append('{...}')  # 用占位符替代表达式
            return ''.join(parts)
        elif isinstance(node, ast.Call):
            # 处理函数调用,返回函数名
            if isinstance(node.func, ast.Name):
                return f"{node.func.id}(...)"
            elif isinstance(node.func, ast.Attribute):
                return f"{ast.unparse(node.func.value)}.{node.func.attr}(...)"
        return ast.unparse(node)

if __name__ == "__main__":
    repo_path = "./K8S-multi-cluster-resource-panel"
    dir_path = "docs"
    analyzer = CodeAnalyzer(repo_path,dir_path)
    analyzer.analyze_repository()
    analyzer.save_documentation()
