# 完整使用示例
from pathlib import Path
from code_analyzer.main import CodeAnalyzer
from code_analyzer.config import Config  

def analyze_project():
    """
    分析指定项目的代码并生成报告。
    """
    # 配置项目路径和输出目录
    repo_path = "./K8S-multi-cluster-resource-panel"  # 项目路径
    output_dir = "./analysis_results"  # 分析结果输出目录
    config_file = "config.json"  # 配置文件路径（可选）

    try:
        # 初始化配置对象
        print("加载配置...")
        config = Config(config_file) if config_file else Config()

        # 初始化分析器
        print("初始化代码分析器...")
        analyzer = CodeAnalyzer(
            repo_path=repo_path,
            config=config
        )

        # 设置输出目录（如果需要）
        config.analyzer.output_dir = output_dir

        # 打印项目信息
        print(f"\n正在分析项目: {Path(repo_path).resolve()}")
        print(f"输出目录: {Path(output_dir).resolve()}")

        # 运行分析
        print("\n开始分析项目...")
        results = analyzer.analyze()

        # 打印分析完成信息
        print("\n=== 分析完成！ ===")
        print(f"分析结果已保存到: {Path(output_dir).resolve()}")
        print("请查看以下文件获取详细报告：")
        for format in config.reporting.output_formats:
            if format == 'json':
                print(f"- JSON 报告: analysis_report.json")
            elif format == 'markdown':
                print(f"- Markdown 报告: analysis_report.md")
            elif format == 'html':
                print(f"- HTML 报告: analysis_report.html")

    except FileNotFoundError as fnf_error:
        # 捕获文件未找到错误
        print(f"\n错误: 文件或目录未找到 - {fnf_error}")
    except PermissionError as perm_error:
        # 捕获权限错误
        print(f"\n错误: 权限不足 - {perm_error}")
    except Exception as e:
        # 捕获其他异常
        print(f"\n分析过程中出现错误: {str(e)}")

if __name__ == "__main__":
    analyze_project()