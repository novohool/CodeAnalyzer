# 完整使用示例
from code_analyzer.main import CodeAnalyzer

def analyze_project():
    # 初始化分析器
    analyzer = CodeAnalyzer(
        repo_path="./K8S-multi-cluster-resource-panel",
        output_dir="./analysis_results"
    )
    
    try:
        # 运行分析
        print("开始分析项目...")
        results = analyzer.analyze()
        
        print("分析完成！")
        print("请查看 analysis_results/analysis_report.json 获取详细报告。")
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")

if __name__ == "__main__":
    analyze_project()