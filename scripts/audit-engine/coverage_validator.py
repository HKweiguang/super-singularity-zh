"""
覆盖率校验器
后置校验 AI 审计输出是否完整回应了所有预期检查项
"""

import re
from typing import Set, Dict, List


def extract_responded_ids(ai_output: str, id_pattern: str = r"[A-Z]-[A-Z]-\d{2}") -> Set[str]:
    """
    从 AI 输出中提取已回应的检查项编号。

    默认匹配形如 G-U-01、G-S-03 的编号。
    可根据实际清单编号格式调整 id_pattern。
    """
    return set(re.findall(id_pattern, ai_output))


def validate_coverage(ai_output: str, expected_ids: Set[str],
                      id_pattern: str = r"[A-Z]-[A-Z]-\d{2}") -> Dict:
    """
    校验 AI 输出是否覆盖了所有预期检查项。

    Args:
        ai_output: AI 审计输出的原始文本
        expected_ids: 预期必须回应的检查项编号集合
        id_pattern: 检查项编号的正则模式

    Returns:
        {
            "expected_count": int,
            "responded_count": int,
            "missing_ids": List[str],
            "coverage_rate": float,
            "passed": bool,
            "coverage_statement_found": bool
        }
    """
    responded_ids = extract_responded_ids(ai_output, id_pattern)
    missing_ids = sorted(expected_ids - responded_ids)

    expected_count = len(expected_ids)
    responded_count = len(responded_ids & expected_ids)
    coverage_rate = round(responded_count / expected_count * 100, 1) if expected_count > 0 else 0.0

    # 检测是否包含覆盖声明
    coverage_statement_found = bool(
        re.search(r"应检查\s*\d+\s*项", ai_output) and
        re.search(r"已回应\s*\d+\s*项", ai_output)
    )

    return {
        "expected_count": expected_count,
        "responded_count": responded_count,
        "missing_ids": missing_ids,
        "coverage_rate": coverage_rate,
        "passed": len(missing_ids) == 0 and coverage_statement_found,
        "coverage_statement_found": coverage_statement_found,
    }


def format_coverage_report(result: Dict) -> str:
    """将覆盖率校验结果格式化为人类可读的文本。"""
    lines = [
        "=" * 50,
        "AI 审计覆盖率校验报告",
        "=" * 50,
        f"预期检查项：{result['expected_count']} 项",
        f"已回应检查项：{result['responded_count']} 项",
        f"覆盖率：{result['coverage_rate']}%",
        f"覆盖声明：{'✅ 已提供' if result['coverage_statement_found'] else '❌ 未提供'}",
    ]

    if result["missing_ids"]:
        lines.append(f"❌ 遗漏检查项：{', '.join(result['missing_ids'])}")
    else:
        lines.append("✅ 无遗漏检查项")

    lines.append(
        "✅ 校验通过" if result["passed"] else "❌ 校验未通过"
    )

    return "\n".join(lines)
