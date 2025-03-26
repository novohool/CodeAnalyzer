"""Main module for code analyzer."""

import json
from pathlib import Path
from typing import Dict, Any

from .analyzers.route_analyzer import RouteAnalyzer
from .analyzers.code_metrics import CodeMetricsAnalyzer

class CodeAnalyzer:
    """Main code analyzer that coordinates all analysis tasks."""
    
    def __init__(self, repo_path: str, output_dir: str = "analysis_results"):
        """Initialize code analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            output_dir: Output directory for analysis results
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.results = {
            'routes': {},
            'metrics': {}
        }
        
        # 初始化分析器
        self.route_analyzer = RouteAnalyzer(repo_path)
        self.metrics_analyzer = CodeMetricsAnalyzer(repo_path)
        
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
        
        # 保存分析结果
        self._save_results()
        
        # 打印分析结果
        self._print_results()
        
        return self.results
        
    def _save_results(self):
        """Save analysis results to JSON file."""
        output_dir = Path(self.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / 'analysis_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4)
            
        print(f"\n分析结果已保存到: {output_file}")
        
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

def main():
    """Command line entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m code_analyzer <project_path>")
        sys.exit(1)
        
    project_path = sys.argv[1]
    analyzer = CodeAnalyzer(project_path)
    analyzer.analyze()
    
if __name__ == '__main__':
    main() 