"""Main module for code analyzer."""

import json
from pathlib import Path
from typing import Dict, Any, List

from .analyzers.route_analyzer import RouteAnalyzer
from .analyzers.code_metrics import CodeMetricsAnalyzer
from .utils.code_explainer import CodeExplainer
from .config import Config

class CodeAnalyzer:
    """Main code analyzer that coordinates all analysis tasks."""
    
    def __init__(self, repo_path: str, config: Config = None):
        """Initialize code analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            config: Configuration object for the analyzer
        """
        self.repo_path = repo_path
        self.config = config or Config()
        self.results = {
            'routes': {},
            'metrics': {},
            'explanations': {}
        }
        
        # 初始化分析器
        self.route_analyzer = RouteAnalyzer(repo_path, self.config.route_analysis)
        self.metrics_analyzer = CodeMetricsAnalyzer(repo_path, self.config.metrics)
        self.code_explainer = CodeExplainer(self.config.llm)
        
    def analyze(self) -> Dict[str, Any]:
        """Run all analyzers and generate reports.
        
        Returns:
            Dictionary containing all analysis results
        """
        # 分析路由
        print("\n分析路由...")
        self.results['routes'] = self.route_analyzer.analyze()
        
        # 分析代码指标
        print("分析代码指标...")
        self.results['metrics'] = self.metrics_analyzer.analyze()
        
        # 分析代码说明
        print("生成代码说明...")
        self.results['explanations'] = self._analyze_code_explanations()
        
        # 保存分析结果
        self._save_results()
        
        # 打印分析结果
        self._print_results()
        
        return self.results
        
    def _analyze_code_explanations(self) -> Dict[str, str]:
        """分析代码文件并生成说明"""
        explanations = {}
        repo_path = Path(self.repo_path)
        
        # 遍历所有代码文件
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and self._is_code_file(file_path):
                relative_path = str(file_path.relative_to(repo_path))
                print(f"分析文件: {relative_path}")
                result = self.code_explainer.analyze_file(str(file_path))
                if result["status"] == "success":
                    explanations[relative_path] = result["explanation"]
                    print(f"分析结果: {result}")
                else:
                    explanations[relative_path] = f"分析失败: {result.get('error', '未知错误')}"
        
        return explanations
        
    def _is_code_file(self, file_path: Path) -> bool:
        """判断文件是否为代码文件"""
        # 检查文件大小
        if file_path.stat().st_size > self.config.analyzer.max_file_size:
            return False
            
        # 检查是否在排除目录中
        for excluded_dir in self.config.analyzer.excluded_dirs:
            if excluded_dir in str(file_path):
                return False
                
        # 检查文件扩展名
        suffix = file_path.suffix.lower()
        for extensions in self.config.analyzer.code_extensions.values():
            if suffix in extensions:
                return True
                
        return False
        
    def _save_results(self):
        """Save analysis results to JSON file."""
        output_dir = Path(self.config.analyzer.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 根据配置的格式保存结果
        for format in self.config.reporting.output_formats:
            if format == 'json':
                output_file = output_dir / 'analysis_report.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=4, ensure_ascii=False)
                print(f"\nJSON 分析结果已保存到: {output_file}")
            elif format == 'markdown':
                output_file = output_dir / 'analysis_report.md'
                self._save_markdown_report(output_file)
                print(f"\nMarkdown 分析结果已保存到: {output_file}")
            elif format == 'html':
                output_file = output_dir / 'analysis_report.html'
                self._save_html_report(output_file)
                print(f"\nHTML 分析结果已保存到: {output_file}")
        
    def _save_markdown_report(self, output_file: Path):
        """保存 Markdown 格式的报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 代码分析报告\n\n")
            
            if self.config.reporting.include_timestamps:
                from datetime import datetime
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 路由分析结果
            f.write("## 路由分析\n\n")
            f.write("### 前端路由\n\n")
            for route in self.results['routes'].get('frontend', []):
                f.write(f"- **路径**: {route['path']}\n")
                if route.get('component'):
                    f.write(f"  - 组件: {route['component']}\n")
                if route.get('framework'):
                    f.write(f"  - 框架: {route['framework']}\n")
                if route.get('file'):
                    f.write(f"  - 文件: {route['file']}\n")
                if route.get('guards'):
                    f.write(f"  - 路由守卫: {', '.join(route['guards'])}\n")
                f.write("\n")
            
            f.write("### 后端路由\n\n")
            for route in self.results['routes'].get('backend', []):
                f.write(f"- **路径**: {route['path']}\n")
                if route.get('methods'):
                    f.write(f"  - 方法: {', '.join(route['methods'])}\n")
                if route.get('handler'):
                    f.write(f"  - 处理函数: {route['handler']}\n")
                if route.get('file'):
                    f.write(f"  - 文件: {route['file']}\n")
                if route.get('functionality'):
                    f.write(f"  - 功能: {route['functionality']}\n")
                if route.get('auth_required'):
                    f.write("  - 需要认证: 是\n")
                f.write("\n")
            
            # 代码指标
            f.write("## 代码指标\n\n")
            metrics = self.results['metrics']
            f.write("| 指标 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| 函数总数 | {metrics.get('functions', 0)} |\n")
            f.write(f"| 类总数 | {metrics.get('classes', 0)} |\n")
            f.write(f"| 接口总数 | {metrics.get('interfaces', 0)} |\n")
            f.write(f"| API端点总数 | {metrics.get('api_endpoints', 0)} |\n")
            f.write(f"| 公共方法数 | {metrics.get('public_methods', 0)} |\n")
            f.write(f"| 私有方法数 | {metrics.get('private_methods', 0)} |\n")
            f.write(f"| 代码复杂度 | {metrics.get('complexity', 0)} |\n")
            
            # 代码说明
            f.write("\n## 代码说明\n\n")
            for file_path, explanation in self.results['explanations'].items():
                f.write(f"### {file_path}\n\n")
                # 只保留简要逻辑和作用说明
                lines = explanation.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('```'):
                        f.write(f"{line}\n")
                f.write("\n")
                
    def _save_html_report(self, output_file: Path):
        """保存 HTML 格式的报告"""
        # 这里可以实现 HTML 报告的生成
        # 可以使用模板引擎如 Jinja2 来生成更漂亮的报告
        pass
        
    def _print_results(self):
        """Print analysis results to console."""
        # 打印路由分析结果
        print("\n=== 路由分析结果 ===")
        
        print("\n前端路由:")
        for route in self.results['routes'].get('frontend', []):
            print(f"\n路径: {route['path']}")
            print(f"组件: {route['component']}")
            print(f"框架: {route['framework']}")
            print(f"文件: {route['file']}")
            if route['guards']:
                print(f"路由守卫: {', '.join(route['guards'])}")
                
        print("\n后端路由:")
        for route in self.results['routes'].get('backend', []):
            print(f"\n路径: {route['path']}")
            print(f"方法: {', '.join(route['methods'])}")
            print(f"处理函数: {route['handler']}")
            print(f"文件: {route['file']}")
            print(f"功能: {route['functionality']}")
            if route['auth_required']:
                print("需要认证: 是")
                
        # 打印代码指标
        print("\n=== 代码指标 ===")
        metrics = self.results['metrics']
        print(f"\n函数总数: {metrics.get('functions', 0)}")
        print(f"类总数: {metrics.get('classes', 0)}")
        print(f"接口总数: {metrics.get('interfaces', 0)}")
        print(f"API端点总数: {metrics.get('api_endpoints', 0)}")
        print(f"公共方法数: {metrics.get('public_methods', 0)}")
        print(f"私有方法数: {metrics.get('private_methods', 0)}")
        print(f"代码复杂度: {metrics.get('complexity', 0)}")
        
        # 打印代码说明
        print("\n=== 代码说明 ===")
        for file_path, explanation in self.results['explanations'].items():
            print(f"\n文件: {file_path}")
            print("说明:")
            print(explanation)

def main():
    """Command line entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m code_analyzer <project_path> [config_file]")
        sys.exit(1)
        
    project_path = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else None
    config = Config(config_file)
    
    analyzer = CodeAnalyzer(project_path, config)
    analyzer.analyze()
    
if __name__ == '__main__':
    main() 