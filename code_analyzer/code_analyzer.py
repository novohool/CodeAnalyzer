import os
import json
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
        
        # 保存JSON文件
        json_path = os.path.join(self.output_dir, 'full_documentation.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(full_docs, f, indent=2, ensure_ascii=False)
            
        # 复制HTML模板到输出目录
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'analysis_report.html')
        output_html = os.path.join(self.output_dir, 'analysis_report.html')
        
        import shutil
        shutil.copy2(template_path, output_html)
        
        print(f"Documentation saved to {self.output_dir}/")
        print(f"- JSON data: {json_path}")
        print(f"- HTML report: {output_html}")
        print("\nOpen analysis_report.html in a web browser to view the interactive report.") 