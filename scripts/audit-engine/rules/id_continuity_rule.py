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

        # 按前缀分组（只统计定义位置的编号）
        prefix_groups: Dict[str, List[int]] = defaultdict(list)
        definition_occurrences: Dict[str, List[int]] = defaultdict(list)
        reference_occurrences: Dict[str, List[int]] = defaultdict(list)

        for id_info in document.ids:
            id_str = id_info['id']
            line_num = id_info['line_number']

            # 向后兼容：没有 is_definition 字段时默认视为定义位置
            is_def = id_info.get('is_definition', True)
            if is_def:
                definition_occurrences[id_str].append(line_num)

                if '-' in id_str:
                    prefix, num_str = id_str.split('-', 1)
                    try:
                        num = int(num_str)
                        prefix_groups[prefix].append(num)
                    except ValueError:
                        pass
            else:
                reference_occurrences[id_str].append(line_num)

        # 检查重复（只检查定义位置）
        duplicates = {k: v for k, v in definition_occurrences.items() if len(v) > 1}
        if duplicates:
            for dup_id, lines in duplicates.items():
                result.add(self._make_checkpoint(
                    id="C-DUP",
                    item=f"编号 '{dup_id}' 无重复",
                    status=ResultStatus.FAIL,
                    line_number=lines[1],
                    note=f"编号 '{dup_id}' 在第 {lines} 行被重复定义"
                ))
        else:
            result.add(self._make_checkpoint(
                id="C-DUP",
                item="文档中编号无重复",
                status=ResultStatus.PASS
            ))

        # 记录引用统计（信息级，不报错）
        if reference_occurrences:
            total_refs = sum(len(v) for v in reference_occurrences.values())
            result.add(self._make_checkpoint(
                id="C-REF",
                item="文档中编号引用统计",
                status=ResultStatus.PASS,
                note=f"发现 {len(reference_occurrences)} 个编号被引用，共 {total_refs} 次引用"
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
