from typing import Dict, Any, List


class ResponseComparator:
    """响应比较器"""

    # 需要忽略的动态字段
    IGNORE_KEYS = ['id', 'timestamp', 'created_at', 'updated_at', 'token']

    def compare(self, actual: Dict, expected: Dict) -> tuple:
        """
        比较实际响应和期望响应
        返回: (是否匹配, 差异描述)
        """
        if not expected:
            return True, ""

        # 过滤动态字段
        actual_filtered = self._filter_ignore_keys(actual)
        expected_filtered = self._filter_ignore_keys(expected)

        # 比较
        if actual_filtered == expected_filtered:
            return True, ""

        # 找出差异
        diff = self._find_diff(actual_filtered, expected_filtered)
        return False, diff

    def _filter_ignore_keys(self, obj: Any) -> Any:
        """递归过滤需要忽略的字段"""
        if isinstance(obj, dict):
            return {
                k: self._filter_ignore_keys(v)
                for k, v in obj.items()
                if k not in self.IGNORE_KEYS
            }
        elif isinstance(obj, list):
            return [self._filter_ignore_keys(item) for item in obj]
        else:
            return obj

    def _find_diff(self, actual: Dict, expected: Dict, path: str = "") -> str:
        """递归查找差异"""
        diffs = []

        for key in expected.keys():
            new_path = f"{path}.{key}" if path else key

            if key not in actual:
                diffs.append(f"缺少字段: {new_path}")
                continue

            if isinstance(expected[key], dict) and isinstance(actual[key], dict):
                sub_diff = self._find_diff(actual[key], expected[key], new_path)
                if sub_diff:
                    diffs.append(sub_diff)
            elif expected[key] != actual[key]:
                diffs.append(
                    f"字段 {new_path} 不匹配: "
                    f"期望 '{expected[key]}', 实际 '{actual[key]}'"
                )

        return "; ".join(diffs) if diffs else ""


comparator = ResponseComparator()