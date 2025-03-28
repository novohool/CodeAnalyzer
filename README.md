# Code Analyzer with AI

一个强大的代码分析工具，用于分析、评估和改进代码质量。

## 功能特点

- 代码复杂度分析
- 依赖关系分析
- 测试覆盖率分析
- 路由分析（支持客户端和服务器端）
- 自定义报告生成
- LLM 集成分析

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/code-analyzer.git
cd code-analyzer
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

项目使用 JSON 格式的配置文件进行设置。默认配置文件位于项目根目录的 `config.json`。

### 配置项说明

#### LLM 配置
```json
{
    "llm": {
        "api_key": "your-api-key",
        "base_url": "https://api.example.com",
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": true,
        "timeout": 30,
        "prompt_template": "your-prompt-template"
    }
}
```

#### 分析器配置
```json
{
    "analyzer": {
        "output_dir": "./output",
        "code_extensions": {
            "python": [".py"],
            "javascript": [".js", ".jsx"]
        },
        "excluded_dirs": ["node_modules", "venv"],
        "max_file_size": 1000000,
        "file_patterns": {
            "test": ["*_test.py", "test_*.py"]
        }
    }
}
```

#### 路由分析配置
```json
{
    "route_analysis": {
        "client": {
            "framework": "react",
            "route_pattern": "src/routes/*"
        },
        "server": {
            "framework": "flask",
            "route_pattern": "app/routes/*"
        }
    }
}
```

#### 指标配置
```json
{
    "metrics": {
        "complexity_threshold": 10,
        "max_function_length": 50,
        "max_class_length": 500,
        "max_file_length": 1000,
        "metrics_to_collect": ["complexity", "lines", "functions"]
    }
}
```

#### 报告配置
```json
{
    "reporting": {
        "output_formats": ["html", "json", "markdown"],
        "include_timestamps": true,
        "include_file_stats": true,
        "include_complexity_analysis": true,
        "include_dependency_analysis": true,
        "include_test_coverage": true,
        "custom_templates": {
            "html": "templates/report.html",
            "markdown": "templates/report.md"
        }
    }
}
```

## 使用方法

有两种方式可以使用本工具：

1. 直接运行 analyzer.py（使用默认配置）：
```bash
python analyzer.py
```
这种方式会分析默认项目路径（./K8S-multi-cluster-resource-panel）并将结果输出到默认目录（./analysis_results）。

2. 作为模块运行（可自定义项目路径和配置）：
```bash
python -m code_analyzer <project_path> [config_file]
```

例如：
```bash
# 分析当前目录
python -m code_analyzer .

# 使用自定义配置文件分析指定目录
python -m code_analyzer /path/to/project custom_config.json
```

## 输出示例

分析完成后，工具会生成以下类型的报告：

- HTML 报告：包含交互式图表和详细分析
- JSON 报告：包含原始数据，适合进一步处理
- Markdown 报告：适合在 GitHub 等平台上展示

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：[Your Name](https://github.com/yourusername)
- 项目链接：[https://github.com/yourusername/code-analyzer](https://github.com/yourusername/code-analyzer)
