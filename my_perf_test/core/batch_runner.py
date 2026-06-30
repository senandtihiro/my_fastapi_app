import json
import time
import requests
from typing import Dict, List, Any
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)


class BatchTestRunner:
    """批量测试运行器 - 用于功能验证"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()

    def run_batch_test(self, test_cases: Dict[str, List[Dict]], max_workers: int = 5) -> Dict:
        """
        批量运行所有测试用例
        test_cases: {endpoint: [case1, case2, ...]}
        """
        logger.info(f"🚀 开始批量测试，共 {len(test_cases)} 个接口")

        logger.info(f"test cases are:{test_cases}")

        total_cases = sum(len(cases) for cases in test_cases.values())
        logger.info(f"📊 总测试用例数: {total_cases}")

        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }

        # 逐个接口测试
        for endpoint, cases in test_cases.items():
            logger.info(f"📤 测试接口: {endpoint} ({len(cases)} 个用例)")

            for case in cases:
                result = self._run_single_test(endpoint, case)
                results["details"].append(result)
                results["total"] += 1

                if result["status"] == "pass":
                    results["passed"] += 1
                elif result["status"] == "fail":
                    results["failed"] += 1
                else:
                    results["errors"] += 1

                # 打印进度
                if results["total"] % 10 == 0:
                    logger.info(f"  进度: {results['total']}/{total_cases}")

        return results

    def _run_single_test(self, endpoint: str, case: Dict) -> Dict:
        """运行单个测试用例"""
        request_body = case.get("request_body", {})
        expected_status = case.get("expected_status", 200)
        expected_response = case.get("expected_response", {})
        case_name = case.get("name", "unknown")

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            # 发送请求
            response = self.session.post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000

            # 验证状态码
            if response.status_code != expected_status:
                return {
                    "endpoint": endpoint,
                    "case": case_name,
                    "status": "fail",
                    "reason": f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}",
                    "request_body": request_body,
                    "response": response.text[:200],
                    "response_time": response_time
                }

            # 验证响应内容
            if expected_response:
                try:
                    actual_response = response.json()
                    # 简单比较
                    match = self._compare_response(actual_response, expected_response)
                    if not match:
                        return {
                            "endpoint": endpoint,
                            "case": case_name,
                            "status": "fail",
                            "reason": f"响应内容不匹配",
                            "request_body": request_body,
                            "expected_response": expected_response,
                            "actual_response": actual_response,
                            "response_time": response_time
                        }
                except json.JSONDecodeError:
                    return {
                        "endpoint": endpoint,
                        "case": case_name,
                        "status": "error",
                        "reason": "响应不是有效的JSON",
                        "response": response.text[:200],
                        "response_time": response_time
                    }

            # 测试通过
            return {
                "endpoint": endpoint,
                "case": case_name,
                "status": "pass",
                "response_time": response_time,
                "request_body": request_body
            }

        except requests.exceptions.RequestException as e:
            return {
                "endpoint": endpoint,
                "case": case_name,
                "status": "error",
                "reason": f"请求异常: {str(e)}",
                "request_body": request_body
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "case": case_name,
                "status": "error",
                "reason": f"未知异常: {str(e)}",
                "request_body": request_body
            }

    def _compare_response(self, actual: Dict, expected: Dict) -> bool:
        """简单比较响应（忽略动态字段）"""
        ignore_keys = ['id', 'timestamp', 'created_at', 'updated_at', 'token']

        # 过滤动态字段
        actual_filtered = {k: v for k, v in actual.items() if k not in ignore_keys}
        expected_filtered = {k: v for k, v in expected.items() if k not in ignore_keys}

        return actual_filtered == expected_filtered

    def print_report(self, results: Dict):
        """打印测试报告"""
        print("\n" + "=" * 70)
        print("📊 批量测试报告")
        print("=" * 70)
        print(f"总用例数: {results['total']}")
        print(f"✅ 通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
        print(f"❌ 失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
        print(f"⚠️  错误: {results['errors']} ({results['errors']/results['total']*100:.1f}%)")

        # 响应时间统计
        response_times = [d.get('response_time', 0) for d in results['details'] if d.get('response_time')]
        if response_times:
            print("\n⏱️  响应时间统计:")
            print(f"  平均: {sum(response_times)/len(response_times):.2f}ms")
            print(f"  最大: {max(response_times):.2f}ms")
            print(f"  最小: {min(response_times):.2f}ms")

        # 失败详情
        failures = [d for d in results['details'] if d['status'] in ['fail', 'error']]
        if failures:
            print("\n❌ 失败/错误详情:")
            print("-" * 70)
            for i, fail in enumerate(failures[:10], 1):
                print(f"{i}. [{fail['endpoint']}] {fail['case']}")
                print(f"   原因: {fail.get('reason', '未知')}")
                if 'request_body' in fail:
                    print(f"   请求体: {json.dumps(fail['request_body'], ensure_ascii=False)[:100]}")
                if 'response' in fail:
                    print(f"   响应: {fail['response'][:100]}")
                print()

            if len(failures) > 10:
                print(f"... 还有 {len(failures) - 10} 个失败用例")

        print("=" * 70)

        # 保存详细结果到文件
        self._save_results(results)

    def _save_results(self, results: Dict):
        """保存结果到文件"""
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)

        filename = output_dir / f"batch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 详细结果已保存: {filename}")