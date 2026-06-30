import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TestCaseLoader:
    """通用测试集加载器 - 无缓存"""

    def __init__(self):
        # ★★★ 接口字段映射配置 ★★★
        self.field_mappings = {
            "/api/correction": {
                "request_mapping": {
                    "wrong_word": "错词",
                },
                "response_mapping": {
                    "corrected_word": "标准词"
                }
            },
            # "/api/translation": {
            #     "request_mapping": {
            #         "source_lang": "源语言",
            #         "target_lang": "目标语言",
            #         "text": "源文本"
            #     },
            #     "response_mapping": {
            #         "translated_text": "目标文本"
            #     }
            # },
            # "/api/summary": {
            #     "request_mapping": {
            #         "content": "原文"
            #     },
            #     "response_mapping": {
            #         "summary": "摘要"
            #     }
            # }
        }

    def load_cases(self, api_path: str) -> List[Dict[str, Any]]:
        """加载指定接口的所有测试用例"""
        excel_file = self._get_excel_path(api_path)

        if not excel_file.exists():
            logger.warning(f"测试集文件不存在: {excel_file}")
            return []

        cases = self._load_from_excel(excel_file, api_path)

        logger.info(f"加载 {api_path} 的 {len(cases)} 个测试用例")
        return cases

    def _get_excel_path(self, api_path: str) -> Path:
        """根据接口路径获取Excel文件路径"""
        filename = api_path.replace('/api/', '').replace('/', '_')
        return Path("test_cases") / f"{filename}.xlsx"

    def _load_from_excel(self, file_path: Path, api_path: str) -> List[Dict]:
        """从Excel加载测试用例 - 指定引擎"""
        try:
            # ★★★ 修复：显式指定engine为openpyxl ★★★
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            logger.error(f"读取Excel文件失败: {file_path}, 错误: {e}")
            # 尝试使用xlrd引擎（如果是旧格式）
            try:
                df = pd.read_excel(file_path, engine='xlrd')
            except:
                logger.error(f"无法读取Excel文件: {file_path}")
                return []

        # 获取该接口的字段映射配置
        mapping = self.field_mappings.get(api_path, {})
        if not mapping:
            logger.warning(f"接口 {api_path} 没有配置字段映射，使用默认映射")
            return self._load_with_default_mapping(df)

        request_mapping = mapping.get("request_mapping", {})
        response_mapping = mapping.get("response_mapping", {})

        cases = []
        for idx, row in df.iterrows():
            # ★★★ 构造请求体 ★★★
            request_body = {}
            for req_field, excel_column in request_mapping.items():
                if excel_column in row and pd.notna(row[excel_column]):
                    request_body[req_field] = row[excel_column]

            # ★★★ 构造期望响应 ★★★
            expected_response = {}
            for resp_field, excel_column in response_mapping.items():
                if excel_column in row and pd.notna(row[excel_column]):
                    expected_response[resp_field] = row[excel_column]

            case = {
                "name": f"case_{idx+1}",
                "request_body": request_body,
                "expected_status": 200,
                "expected_response": expected_response,
                "headers": {"Content-Type": "application/json"},
            }
            cases.append(case)

        return cases

    def _load_with_default_mapping(self, df: pd.DataFrame) -> List[Dict]:
        """默认映射：将所有列作为请求体"""
        cases = []
        for idx, row in df.iterrows():
            request_body = row.to_dict()
            request_body = {k: v for k, v in request_body.items() if pd.notna(v)}

            cases.append({
                "name": f"case_{idx+1}",
                "request_body": request_body,
                "expected_status": 200,
                "expected_response": {},
                "headers": {"Content-Type": "application/json"},
            })
        return cases

    def add_mapping(self, api_path: str, mapping: Dict):
        """动态添加接口映射"""
        self.field_mappings[api_path] = mapping


# 全局实例
test_loader = TestCaseLoader()