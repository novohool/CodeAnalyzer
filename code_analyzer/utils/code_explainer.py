import os
import requests
import json
import re
from typing import Dict, Any, Generator
from ..config import LLMConfig

class CodeExplainer:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

    def _filter_llm_response(self, response: str) -> str:
        """过滤LLM回答中的<think></think>标签及其内容"""
        # 移除<think>标签及其内容
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # 移除<think>标签及其内容
        response = re.sub(r'.*?</think>', '', response, flags=re.DOTALL)
        # 移除可能遗留的<think>开始标签
        response = re.sub(r'<think>', '', response)
        # 移除独立的</think>结束标签
        response = re.sub(r'</think>', '', response)
        # 移除多余空行，但保留段落格式
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        # 移除开头的空行
        response = re.sub(r'^\s*\n', '', response)
        return response.strip()

    def generate_explanation(self, file_content: str, file_path: str, stream_output: bool = True) -> str:
        """生成代码文件的说明"""
        required_attrs = ["model", "base_url", "max_tokens", "temperature", "stream", "timeout"]
        if not all(hasattr(self.config, attr) for attr in required_attrs):
            return "LLM配置缺失必要的属性"
    
        prompt = self.config.prompt_template.format(file_path=file_path, file_content=file_content)
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": self.config.stream
        }
    
        try:
            with requests.post(
                f"{self.config.base_url}/completions",
                json=payload,
                headers=self.headers,
                stream=True,
                timeout=self.config.timeout
            ) as response:
                if response.status_code == 200:
                    accumulated_text = ""
                    for line in response.iter_lines(decode_unicode=False):
                        if line:
                            try:
                                line_data = line.decode("utf-8")
                            except UnicodeDecodeError:
                                line_data = line.decode("latin1")
    
                            if line_data.startswith("data: "):
                                data_str = line_data[6:]
                                if data_str == "[DONE]":
                                    return accumulated_text
                                try:
                                    data = json.loads(data_str)
                                    if "error" in data:
                                        return f"错误: {data['error']}"
                                    if "choices" in data and len(data["choices"]) > 0:
                                        text = data["choices"][0].get("text", "")
                                        if stream_output:
                                            print(text, end="", flush=True)
                                        accumulated_text += text
                                except json.JSONDecodeError:
                                    return f"无法解析JSON数据: {data_str}"
                    return accumulated_text
                else:
                    return f"请求失败，状态码：{response.status_code}"
        except requests.exceptions.Timeout:
            return "请求超时"
        except requests.exceptions.ConnectionError:
            return "网络连接失败"
        except Exception as e:
            return f"未知错误: {str(e)}"

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件并返回结果"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            explanation = self.generate_explanation(content, file_path)
            
            # 在获取LLM回答后添加过滤
            filtered_explanation = self._filter_llm_response(explanation)
            
            return {
                "file_path": file_path,
                "explanation": filtered_explanation,
                "status": "success"
            }
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "status": "error"
            } 