"""Code metrics analyzer module."""

import ast
import json
import os
from typing import Dict, Any, List, Set
from pathlib import Path
from ..config import Config 

from .base import BaseAnalyzer

class CodeMetricsAnalyzer(BaseAnalyzer):
    """Analyzer for code metrics like complexity, maintainability etc."""
    
    def __init__(self, repo_path: str, config: Config):
        """Initialize code metrics analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
        """
        super().__init__(repo_path, config)
        self.metrics = {
            'functions': 0,
            'classes': 0,
            'interfaces': 0,
            'api_endpoints': 0,
            'public_methods': 0,
            'private_methods': 0,
            'complexity': 0.0,
            'functions_details': [],
            'classes_details': [],
            'interfaces_details': [],
            'api_endpoints_details': []
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze code metrics.
        
        Returns:
            Dictionary containing code metrics
        """
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self._analyze_file(file_path, content)
                    except Exception as e:
                        print(f"Error analyzing {file_path}: {str(e)}")
                        
        # 计算总体复杂度
        total_complexity = sum(f.get('complexity', 0) for f in self.metrics['functions_details'])
        if self.metrics['functions'] > 0:
            self.metrics['complexity'] = total_complexity / self.metrics['functions']
            
        return self.metrics
        
    def _analyze_file(self, file_path: str, content: str):
        """Analyze a single Python file.
        
        Args:
            file_path: Path to the file
            content: File content
        """
        try:
            tree = ast.parse(content)
            analyzer = FileAnalyzer(file_path, content)
            analyzer.visit(tree)
            
            # 更新指标
            self.metrics['functions'] += analyzer.function_count
            self.metrics['classes'] += analyzer.class_count
            self.metrics['interfaces'] += analyzer.interface_count
            self.metrics['api_endpoints'] += analyzer.api_endpoint_count
            self.metrics['public_methods'] += analyzer.public_method_count
            self.metrics['private_methods'] += analyzer.private_method_count
            
            # 更新详细信息
            self.metrics['functions_details'].extend(analyzer.functions_details)
            self.metrics['classes_details'].extend(analyzer.classes_details)
            self.metrics['interfaces_details'].extend(analyzer.interfaces_details)
            self.metrics['api_endpoints_details'].extend(analyzer.api_endpoints_details)
            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")

class FileAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python files."""
    
    def __init__(self, file_path: str, content: str):
        """Initialize file analyzer.
        
        Args:
            file_path: Path to the file being analyzed
            content: File content
        """
        self.file_path = file_path
        self.content = content
        self.function_count = 0
        self.class_count = 0
        self.interface_count = 0
        self.api_endpoint_count = 0
        self.public_method_count = 0
        self.private_method_count = 0
        
        self.functions_details = []
        self.classes_details = []
        self.interfaces_details = []
        self.api_endpoints_details = []
        
        # 用于跟踪当前类的上下文
        self.current_class = None
        self.current_class_bases = []
        
        # 用于识别FastAPI装饰器
        self.api_decorators = {
            # FastAPI路由装饰器
            'get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace',
            'APIRouter', 'router', 'app',
            # FastAPI特殊装饰器
            'api_route', 'websocket', 'websocket_route',
            # 通用HTTP方法
            'route', 'endpoint',
            # Flask装饰器
            'route', 'get', 'post', 'put', 'delete', 'patch',
            # Django装饰器
            'api_view', 'permission_classes', 'authentication_classes'
        }
        
        # 用于识别FastAPI对象
        self.api_objects = {
            'FastAPI', 'APIRouter', 'app', 'router'
        }
        
        # 用于识别接口类
        self.interface_bases = {
            'Protocol', 'ABC', 'metaclass=ABCMeta', 'Interface', 'AbstractBase'
        }
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit a class definition.
        
        Args:
            node: AST node for class definition
        """
        self.class_count += 1
        
        # 保存当前类的上下文
        prev_class = self.current_class
        prev_bases = self.current_class_bases
        
        self.current_class = node.name
        self.current_class_bases = [self._get_base_name(base) for base in node.bases]
        
        # 检查是否是接口
        is_interface = any(
            base in self.interface_bases for base in self.current_class_bases
        ) or any(
            isinstance(dec, ast.Name) and dec.id in self.interface_bases 
            for dec in node.decorator_list
        )
        
        if is_interface:
            self.interface_count += 1
            self.interfaces_details.append({
                'name': node.name,
                'file': self.file_path,
                'line_number': node.lineno,
                'bases': self.current_class_bases,
                'methods': [],
                'docstring': ast.get_docstring(node) or ''
            })
            
        # 分析类的属性和方法
        class_info = {
            'name': node.name,
            'file': self.file_path,
            'line_number': node.lineno,
            'is_interface': is_interface,
            'methods': [],
            'attributes': [],
            'bases': self.current_class_bases,
            'docstring': ast.get_docstring(node) or ''
        }
        
        # 访问类的内容
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # 添加类属性
                class_info['attributes'].append({
                    'name': item.target.id,
                    'type': self._get_type_annotation(item.annotation)
                })
                
        self.classes_details.append(class_info)
        
        # 递归访问类的内容
        self.generic_visit(node)
        
        # 恢复之前的类上下文
        self.current_class = prev_class
        self.current_class_bases = prev_bases
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit a function definition.
        
        Args:
            node: AST node for function definition
        """
        self._analyze_function(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit an async function definition.
        
        Args:
            node: AST node for async function definition
        """
        self._analyze_function(node)
        
    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """Analyze a function node.
        
        Args:
            node: AST node for function
        """
        self.function_count += 1
        
        # 检查是否是私有方法
        is_private = node.name.startswith('_')
        if is_private:
            self.private_method_count += 1
        else:
            self.public_method_count += 1
            
        # 检查是否是API端点
        is_api = False
        http_methods = []
        paths = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # 处理装饰器调用，如 @app.get("/path")
                if isinstance(decorator.func, ast.Attribute):
                    # 检查对象是否是API对象
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id in self.api_objects:
                            is_api = True
                            http_methods.append(decorator.func.attr)
                            if decorator.args:
                                paths.append(self._get_decorator_arg(decorator.args[0]))
                    # 检查方法是否是API方法
                    if decorator.func.attr in self.api_decorators:
                        is_api = True
                        http_methods.append(decorator.func.attr)
                        if decorator.args:
                            paths.append(self._get_decorator_arg(decorator.args[0]))
                elif isinstance(decorator.func, ast.Name):
                    # 处理直接装饰器调用，如 @api_view(["GET"])
                    if decorator.func.id in self.api_decorators:
                        is_api = True
                        # 尝试从参数中提取HTTP方法
                        for arg in decorator.args:
                            if isinstance(arg, ast.List):
                                for elt in arg.elts:
                                    if isinstance(elt, ast.Constant):
                                        http_methods.append(elt.value.lower())
            elif isinstance(decorator, ast.Name):
                # 处理简单装饰器，如 @require_auth
                if decorator.id in self.api_decorators:
                    is_api = True
                    http_methods.append(decorator.id)
                    
        if is_api:
            self.api_endpoint_count += 1
            
            # 如果没有明确的HTTP方法，默认为GET
            if not http_methods:
                http_methods = ['get']
                
            # 如果没有明确的路径，使用函数名作为路径
            if not paths:
                paths = [f"/{node.name}"]
                
            self.api_endpoints_details.append({
                'name': node.name,
                'file': self.file_path,
                'line_number': node.lineno,
                'http_methods': list(set(http_methods)),  # 去重
                'paths': list(set(paths)),  # 去重
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'parameters': self._get_function_parameters(node),
                'returns': self._get_return_type(node),
                'docstring': ast.get_docstring(node) or '',
                'decorators': [self._get_decorator_str(d) for d in node.decorator_list]
            })
            
        # 计算函数复杂度
        complexity = self._calculate_complexity(node)
        
        # 添加函数详细信息
        function_info = {
            'name': node.name,
            'file': self.file_path,
            'line_number': node.lineno,
            'is_private': is_private,
            'is_api': is_api,
            'parameters': self._get_function_parameters(node),
            'returns': self._get_return_type(node),
            'docstring': ast.get_docstring(node) or '',
            'complexity': complexity
        }
        
        if self.current_class:
            # 如果是类方法，添加到对应的类信息中
            for class_info in self.classes_details:
                if class_info['name'] == self.current_class:
                    class_info['methods'].append(function_info)
                    break
                    
            # 如果是接口方法，添加到对应的接口信息中
            for interface_info in self.interfaces_details:
                if interface_info['name'] == self.current_class:
                    interface_info['methods'].append(function_info)
                    break
                    
        self.functions_details.append(function_info)
        
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function.
        
        Args:
            node: AST node
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            # 条件语句
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            # 异常处理
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # 布尔运算符
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _get_function_parameters(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Dict[str, str]]:
        """Get function parameters with type annotations.
        
        Args:
            node: Function node
            
        Returns:
            List of parameter information
        """
        params = []
        for arg in node.args.args:
            params.append({
                'name': arg.arg,
                'type': self._get_type_annotation(arg.annotation)
            })
        return params
        
    def _get_return_type(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Get function return type annotation.
        
        Args:
            node: Function node
            
        Returns:
            Return type as string
        """
        if node.returns:
            return self._get_type_annotation(node.returns)
        return 'Any'
        
    def _get_type_annotation(self, node: ast.AST | None) -> str:
        """Convert type annotation AST node to string.
        
        Args:
            node: Type annotation node
            
        Returns:
            Type annotation as string
        """
        if node is None:
            return 'Any'
            
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self._get_type_annotation(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_type_annotation(node.value)}[{self._get_type_annotation(node.slice)}]"
        elif isinstance(node, ast.BinOp):
            return f"{self._get_type_annotation(node.left)} | {self._get_type_annotation(node.right)}"
        
        return 'Any'
        
    def _get_base_name(self, node: ast.AST) -> str:
        """Get base class name from AST node.
        
        Args:
            node: AST node
            
        Returns:
            Base class name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return str(node)
        
    def _get_decorator_arg(self, node: ast.AST) -> str:
        """Get decorator argument value.
        
        Args:
            node: AST node
            
        Returns:
            Decorator argument as string
        """
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_arg(node.value)}.{node.attr}"
        return ''
        
    def _get_decorator_str(self, node: ast.AST) -> str:
        """Get string representation of a decorator.
        
        Args:
            node: AST node
            
        Returns:
            Decorator as string
        """
        if isinstance(node, ast.Name):
            return f"@{node.id}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        args.append(repr(arg.value))
                    elif isinstance(arg, ast.List):
                        items = []
                        for item in arg.elts:
                            if isinstance(item, ast.Constant):
                                items.append(repr(item.value))
                        args.append(f"[{', '.join(items)}]")
                return f"@{node.func.id}({', '.join(args)})"
            elif isinstance(node.func, ast.Attribute):
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        args.append(repr(arg.value))
                return f"@{self._get_decorator_arg(node.func.value)}.{node.func.attr}({', '.join(args)})"
        return str(node)
        
    def get_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """Get metrics for a specific file.
        
        Args:
            file_path: Path to the file relative to repo root
            
        Returns:
            Dictionary containing file metrics
        """
        for file_info in self.metrics['functions_details']:
            if file_info['file'] == file_path:
                return file_info
        return {}
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results.
        
        Returns:
            Dictionary containing summary metrics
        """
        return {
            'total_files': len(self.metrics['functions_details']),
            'total_functions': self.metrics['functions'],
            'total_classes': self.metrics['classes'],
            'total_interfaces': self.metrics['interfaces'],
            'total_api_endpoints': self.metrics['api_endpoints'],
            'public_private_ratio': round(
                self.metrics['public_methods'] / max(self.metrics['private_methods'], 1), 2
            ),
            'complexity': self.metrics['complexity']
        } 