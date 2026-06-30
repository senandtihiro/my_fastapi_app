from locust import FastHttpUser, task, between
import json
import random
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from core.test_loader import test_loader
from core.response_comparator import comparator

logger = logging.getLogger(__name__)


class APIUser(FastHttpUser):
    """API压测用户"""

    wait_time = between(0.5, 2)
    host = "http://localhost:8000"

    def __init__(self, environment):
        super().__init__(environment)
        self.session_data = {}

        # ★★★ 定义要测试的接口及其权重 ★★★
        self.endpoint_config = {
            "/api/correction": {
                "weight": 3,
                "name": "纠错接口"
            },
            # "/api/translation": {
            #     "weight": 2,
            #     "name": "翻译接口"
            # },
            # "/api/summary": {
            #     "weight": 1,
            #     "name": "摘要接口"
            # }
        }

        # ★★★ 加载所有接口的测试用例 ★★★
        self.test_cases = {}
        self.available_endpoints = []

        for endpoint in self.endpoint_config.keys():
            cases = test_loader.load_cases(endpoint)
            if cases:
                self.test_cases[endpoint] = cases
                weight = self.endpoint_config[endpoint]["weight"]
                self.available_endpoints.extend([endpoint] * weight)
                logger.info(f"✅ {endpoint}: 加载 {len(cases)} 个用例")
            else:
                logger.warning(f"⚠️ {endpoint}: 没有找到测试用例")

        logger.info(f"📋 可用接口: {set(self.available_endpoints)}")

    @task
    def test_apis(self):
        """执行API测试"""
        if not self.available_endpoints:
            return

        # 1. 根据权重随机选择接口
        endpoint = random.choice(self.available_endpoints)
        config = self.endpoint_config[endpoint]

        # 2. 从该接口的测试用例中随机选择一个
        cases = self.test_cases[endpoint]
        case = random.choice(cases)

        # 3. 获取数据
        request_body = case.get("request_body", {})
        expected_status = case.get("expected_status", 200)
        expected_response = case.get("expected_response", {})
        headers = case.get("headers", {"Content-Type": "application/json"})
        case_name = case.get("name", "unknown")

        # 4. 参数化处理（支持动态数据）
        request_body = self._parametrize_data(request_body)

        # 5. 发送请求
        with self.client.post(
                endpoint,
                json=request_body,
                headers=headers,
                catch_response=True,
                timeout=30,
                name=f"{config['name']}_{case_name}"
        ) as response:

            # 6. ★★★ 验证状态码 ★★★
            if response.status_code != expected_status:
                response.failure(
                    f"[{config['name']}] 状态码错误\n"
                    f"  期望: {expected_status}\n"
                    f"  实际: {response.status_code}\n"
                    f"  请求体: {json.dumps(request_body, ensure_ascii=False)[:200]}"
                )
                return

            # 7. ★★★ 验证响应内容 ★★★
            try:
                actual_response = response.json()

                if expected_response:
                    match, diff = comparator.compare(actual_response, expected_response)

                    if not match:
                        response.failure(
                            f"[{config['name']}] 响应内容不匹配\n"
                            f"  差异: {diff[:300]}\n"
                            f"  期望: {json.dumps(expected_response, ensure_ascii=False)[:200]}\n"
                            f"  实际: {json.dumps(actual_response, ensure_ascii=False)[:200]}"
                        )
                        return

                # 8. 提取数据供后续使用
                self._extract_data(endpoint, actual_response)

            except json.JSONDecodeError:
                response.failure(
                    f"[{config['name']}] 响应不是有效的JSON\n"
                    f"  响应内容: {response.text[:200]}"
                )

    def _parametrize_data(self, data):
        """参数化替换"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.startswith('$'):
                    if value == '$random_int':
                        data[key] = random.randint(1, 10000)
                    elif value.startswith('$session_'):
                        session_key = value[9:]
                        if session_key in self.session_data:
                            data[key] = self.session_data[session_key]
                elif isinstance(value, dict):
                    data[key] = self._parametrize_data(value)
                elif isinstance(value, list):
                    data[key] = [
                        self._parametrize_data(item) if isinstance(item, dict) else item
                        for item in value
                    ]
        return data

    def _extract_data(self, endpoint: str, response: dict):
        """提取响应数据"""
        if 'data' in response and isinstance(response['data'], dict):
            data = response['data']
            if 'id' in data:
                self.session_data['last_id'] = data['id']