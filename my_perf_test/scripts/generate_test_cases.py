#!/usr/bin/env python
"""生成各种接口的测试集Excel文件"""
import pandas as pd
from pathlib import Path
import openpyxl


def generate_correction_test_cases():
    """生成纠错接口测试集"""
    data = {
        "错词": [
            "今天天气真不错",
            "我吃完饭了",
            "他明天来北京",
            "这个苹果很好吃",
        ],
        "标准词": [
            "今天天气真好",
            "我已经吃过饭了",
            "他将于明天抵达北京",
            "这个苹果味道很好",
        ]
    }
    return pd.DataFrame(data)


def generate_translation_test_cases():
    """生成翻译接口测试集"""
    data = {
        "源语言": ["zh", "zh", "en", "zh"],
        "目标语言": ["en", "en", "zh", "ja"],
        "源文本": [
            "你好世界",
            "今天天气好",
            "Hello",
            "我喜欢编程"
        ],
        "目标文本": [
            "Hello World",
            "Today is sunny",
            "你好",
            "I like programming"
        ]
    }
    return pd.DataFrame(data)


def generate_summary_test_cases():
    """生成摘要接口测试集"""
    data = {
        "原文": [
            "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
            "深度学习是机器学习的分支，是一种以人工神经网络为架构，对数据进行表征学习的算法。"
        ],
        "摘要": [
            "人工智能是计算机科学分支，旨在制造智能机器。",
            "深度学习是机器学习分支，使用神经网络进行特征学习。"
        ]
    }
    return pd.DataFrame(data)


def main():
    """生成所有测试集"""
    # 创建目录
    Path("test_cases").mkdir(exist_ok=True)

    # 先删除旧文件
    for f in Path("test_cases").glob("*.xlsx"):
        f.unlink()
        print(f"🗑️  删除旧文件: {f}")

    try:
        # 1. 生成纠错测试集
        df = generate_correction_test_cases()
        output_file = "test_cases/correction.xlsx"
        # ★★★ 使用openpyxl的Writer ★★★
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"✅ 纠错测试集: {output_file} ({len(df)} 条)")

        # 2. 生成翻译测试集
        df = generate_translation_test_cases()
        output_file = "test_cases/translation.xlsx"
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"✅ 翻译测试集: {output_file} ({len(df)} 条)")

        # 3. 生成摘要测试集
        df = generate_summary_test_cases()
        output_file = "test_cases/summary.xlsx"
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"✅ 摘要测试集: {output_file} ({len(df)} 条)")

        print("\n✅ 所有测试集生成完成！")
        print("📌 请检查 test_cases/ 目录下的Excel文件")

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print("请确保已安装: pip install openpyxl")


if __name__ == "__main__":
    main()