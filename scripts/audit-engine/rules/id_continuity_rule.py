"""
编号连续性检查规则
验证编号是否连续，无跳号、无重复
"""

from typing import Optional, Dict, List
from collections import defaultdict
from .base_rule import BaseRule, AuditResult, ResultStatus


class IdContinuityRule(BaseRule):
    """检查编号连续性和唯一性"""

    RULE_NAME = "id_continuity"
    DIMENSION = "数据"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)

        if not document.ids:
            result.add(self._make_checkpoint(
                id="C0",
                item="文档包含编号引用",
                status=ResultStatus.NA,
                note="本文档无编号引用，跳过连续性检查"
            ))
            return result

        # 按前缀分组
        prefix_groups: Dict[str, List[int]] = defaultdict(list)
        id_occurrences: Dict[str, List[int]] = defaultdict(list)

        for id_info in document.ids:
            id_str = id_info['id']
            id_occurrences[id_str].append(id_info['line_number'])

            if '-' in id_str:
                prefix, num_str = id_str.split('-', 1)
                try:
                    num = int(num_str)
                    prefix_groups[prefix].append(num)
                except ValueError:
                    pass

        # 检查重复
        duplicates = {k: v for k, v in id_occurrences.items() if len(v) > 1}
        if duplicates:
            for dup_id, lines in duplicates.items():
                result.add(self._make_checkpoint(
                    id="C-DUP",
                    item=f"编号 '{dup_id}' 无重复",
                    status=ResultStatus.FAIL,
                    line_number=lines[1],
                    note=f"编号 '{dup_id}' 在第 {lines} 行重复出现"
                ))
        else:
            result.add(self._make_checkpoint(
                id="C-DUP",
                item="文档中编号无重复",
                status=ResultStatus.PASS
            ))

        # 检查连续性
        for prefix, numbers in prefix_groups.items():
            if not numbers:
                continue

            sorted_nums = sorted(set(numbers))
            gaps = []
            for i in range(len(sorted_nums) - 1):
                if sorted_nums[i + 1] - sorted_nums[i] > 1:
                    for missing in range(sorted_nums[i] + 1, sorted_nums[i + 1]):
                        gaps.append(missing)

            if gaps:
                result.add(self._make_checkpoint(
                    id=f"C-{prefix}",
                    item=f"前缀 '{prefix}' 编号连续",
                    status=ResultStatus.FAIL,
                    note=f"前缀 '{prefix}' 存在跳号: 缺失 {', '.join(f'{prefix}-{g:03d}' for g in gaps)}"
                ))
            else:
                result.add(self._make_checkpoint(
                    id=f"C-{prefix}",
                    item=f"前缀 '{prefix}' 编号连续",
                    status=ResultStatus.PASS
                ))

        return result
