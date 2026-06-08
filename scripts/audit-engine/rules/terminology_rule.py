"""
跨产物术语一致性检查规则

从全局术语表中读取"标准术语-禁止别名"映射，检查当前文档中是否使用了禁止别名。

使用场景：
- 市场策划中"受众"vs"目标客户"vs"用户群体"
- 技术方案中"接口"vs"API"vs"端点"
- 任何跨产物共享的概念需要统一命名
"""

import re
from typing import Optional, Dict, List
from pathlib import Path

from .base_rule import BaseRule, AuditResult, ResultStatus


class TerminologyRule(BaseRule):
    """
    跨产物术语一致性检查

    检查逻辑：
    1. 加载术语表配置（默认 + 用户自定义）
    2. 扫描当前文档全文
    3. 发现禁止别名时报告，提示应使用标准术语
    """

    RULE_NAME = "terminology"
    DIMENSION = "数据"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)

        terminology = self._load_terminology()
        if not terminology:
            result.add(self._make_checkpoint(
                id="TERM-CONFIG",
                item="术语表配置存在且可解析",
                status=ResultStatus.NA,
                note="术语表配置不存在，跳过术语一致性检查"
            ))
            return result

        text = getattr(document, 'raw_content', '')
        if not text:
            result.add(self._make_checkpoint(
                id="TERM-CONTENT",
                item="文档内容可读取",
                status=ResultStatus.NA,
                note="文档内容为空，跳过术语检查"
            ))
            return result

        issues_found = []
        for entry in terminology:
            standard = entry.get("standard", "")
            forbidden = entry.get("forbidden_aliases", [])
            definition = entry.get("definition", "")

            for alias in forbidden:
                if not alias:
                    continue

                # 中文无空格分词，多字别名直接精确匹配，单字需要边界
                escaped = re.escape(alias)
                if len(alias) >= 2:
                    pattern = escaped
                else:
                    pattern = r"(?<![\u4e00-\u9fa5a-zA-Z0-9])" + escaped + r"(?![\u4e00-\u9fa5a-zA-Z0-9])"

                for m in re.finditer(pattern, text):
                    start = max(0, m.start() - 30)
                    end = min(len(text), m.end() + 30)
                    ctx = text[start:end].replace("\n", " ")
                    issues_found.append({
                        "alias": alias,
                        "standard": standard,
                        "definition": definition,
                        "context": ctx,
                        "line_number": text[:m.start()].count("\n") + 1
                    })

        if issues_found:
            # 去重：同一位置的同一别名只报一次
            seen = set()
            unique_issues = []
            for issue in issues_found:
                key = (issue["alias"], issue["line_number"])
                if key not in seen:
                    seen.add(key)
                    unique_issues.append(issue)

            result.add(self._make_checkpoint(
                id="TERM-001",
                item="文档中使用标准术语，无禁止别名",
                status=ResultStatus.FAIL,
                note=f"发现 {len(unique_issues)} 处禁止别名使用: "
                     f"{', '.join(set(i['alias'] for i in unique_issues[:5]))}"
                     f"{' 等...' if len(unique_issues) > 5 else ''}"
            ))
        else:
            result.add(self._make_checkpoint(
                id="TERM-001",
                item="文档中使用标准术语，无禁止别名",
                status=ResultStatus.PASS,
                note=f"已检查 {len(terminology)} 条术语定义，未发现禁止别名"
            ))

        return result

    def _load_terminology(self) -> List[Dict]:
        """加载术语表配置（默认 + 用户自定义）"""
        merged = []
        loaded_keys = set()

        # 查找配置目录（与 artifact_types.yaml 相同的查找逻辑）
        config_dirs = self._get_config_dirs()

        for config_dir in config_dirs:
            yaml_path = config_dir / "terminology.yaml"
            if not yaml_path.exists():
                continue
            try:
                import yaml
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                for entry in data.get("terms", []):
                    std = entry.get("standard", "")
                    if std and std not in loaded_keys:
                        loaded_keys.add(std)
                        merged.append(entry)
            except Exception:
                continue

        return merged

    def _get_config_dirs(self) -> List[Path]:
        """返回配置目录查找顺序（复用 config/__init__.py 的逻辑）"""
        # 导入 config 模块的配置目录查找逻辑
        try:
            from config import _find_user_config_dir
            user_dir = _find_user_config_dir()
            dirs = []
            if user_dir.exists():
                dirs.append(user_dir)
            dirs.append(Path(__file__).parent.parent / "config")
            return dirs
        except ImportError:
            return [Path(__file__).parent.parent / "config"]
