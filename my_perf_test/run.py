#!/usr/bin/env python
import argparse
import yaml
import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PerformanceTestRunner:
    def __init__(self, config_file: str = "config.yaml"):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.output_dir = Path("results")
        self.output_dir.mkdir(exist_ok=True)

    def run_batch_test(self):
        """批量测试模式 - 功能验证"""
        logger.info("🧪 启动批量测试模式...")

        # 加载测试用例
        from core.test_loader import test_loader
        from core.batch_runner import BatchTestRunner

        # 定义要测试的接口
        endpoints = [
            "/api/correction",
            # "/api/translation",
            # "/api/summary"
        ]

        # 加载所有测试用例
        test_cases = {}
        for endpoint in endpoints:
            cases = test_loader.load_cases(endpoint)
            if cases:
                test_cases[endpoint] = cases
                logger.info(f"✅ {endpoint}: 加载 {len(cases)} 个用例")
            else:
                logger.warning(f"⚠️ {endpoint}: 没有测试用例")

        if not test_cases:
            logger.error("❌ 没有找到任何测试用例，请先运行: python scripts/generate_test_cases.py")
            return False

        # 运行批量测试
        runner = BatchTestRunner(self.config.get('host', 'http://localhost:8000'))
        results = runner.run_batch_test(test_cases)

        # 打印报告
        runner.print_report(results)

        # 返回是否全部通过
        return results['failed'] == 0 and results['errors'] == 0

    def run_headless(self):
        """压测模式 - 命令行模式"""
        cmd = [
            sys.executable, "-m", "locust",
            "-f", "locustfiles/api_user.py",
            "--host", self.config.get('host', 'http://localhost:8000'),
            "--headless",
            "-u", str(self.config.get('users', 50)),
            "-r", str(self.config.get('spawn_rate', 5)),
            "-t", self.config.get('run_time', '3m'),
            "--csv", str(self.output_dir / "result"),
            "--html", str(self.output_dir / "report.html"),
            "--loglevel", "INFO"
        ]
        logger.info(f"🚀 启动压测: {' '.join(cmd)}")
        return subprocess.run(cmd)

    def run_web(self):
        """压测模式 - Web界面模式"""
        cmd = [
            sys.executable, "-m", "locust",
            "-f", "locustfiles/api_user.py",
            "--host", self.config.get('host', 'http://localhost:8000'),
            "--web-port", "8089"
        ]
        logger.info(f"🌐 启动Web界面: http://localhost:8089")
        return subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="性能测试工具")
    parser.add_argument("-m", "--mode",
                        choices=["batch", "headless", "web"],
                        default="batch",
                        help="运行模式: batch(批量测试), headless(压测), web(Web界面)")
    parser.add_argument("-u", "--users", type=int, help="模拟用户数")
    parser.add_argument("-t", "--time", help="运行时间 (如: 3m, 1h)")

    args = parser.parse_args()

    runner = PerformanceTestRunner()

    if args.users:
        runner.config['users'] = args.users
    if args.time:
        runner.config['run_time'] = args.time

    if args.mode == "batch":
        # 批量测试模式
        success = runner.run_batch_test()
        sys.exit(0 if success else 1)
    elif args.mode == "headless":
        # 压测模式
        runner.run_headless()
    elif args.mode == "web":
        # Web界面模式
        runner.run_web()


if __name__ == "__main__":
    main()
