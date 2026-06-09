"""
配置加载器
支持插件默认配置 + 项目级自定义配置 + CLI 指定配置目录
查找优先级：CLI 指定 > 项目 .singularity/config/ > 插件默认
"""

import re
from pathlib import Path
from typing import Dict, List

_DEFAULT_CONFIG_DIR = Path(__file__).parent
_OVERRIDE_CONFIG_DIR = None  # CLI 可覆盖


def set_config_dir(path: str):
    """设置覆盖配置目录（由 CLI 调用）"""
    global _OVERRIDE_CONFIG_DIR
    _OVERRIDE_CONFIG_DIR = Path(path) if path else None


def _find_user_config_dir() -> Path:
    """从当前目录向上查找 .singularity/config/，类似 git 查找 .git"""
    current = Path.cwd().resolve()
    for path in [current] + list(current.parents):
        candidate = path / ".singularity" / "config"
        if candidate.exists():
            return candidate
    return current / ".singularity" / "config"  # 默认位置


def _get_config_dirs() -> List[Path]:
    """返回配置目录查找顺序（优先级从高到低）"""
    dirs = []
    if _OVERRIDE_CONFIG_DIR:
        dirs.append(_OVERRIDE_CONFIG_DIR)
    user_dir = _find_user_config_dir()
    if user_dir.exists():
        dirs.append(user_dir)
    dirs.append(_DEFAULT_CONFIG_DIR)
    return dirs


def _deep_merge(base: dict, override: dict) -> dict:
    """深度合并两个字典，override 优先级更高"""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(config_name: str) -> dict:
    """按优先级查找并加载 YAML 配置，合并所有配置源"""
    merged = {}
    for config_dir in reversed(_get_config_dirs()):
        yaml_path = config_dir / config_name
        if yaml_path.exists():
            try:
                import yaml
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                # 合并：高优先级配置覆盖低优先级
                merged = _deep_merge(merged, data)
            except ImportError:
                continue
    return merged


def load_artifact_types() -> Dict:
    """加载产物类型定义（合并所有配置源）"""
    data = _load_yaml("artifact_types.yaml")
    types = data.get("types", {})
    if not types:
        return {
            "types": {
                "generic": {"label": "通用文档", "required_sections": [], "id_prefixes": []}
            }
        }
    return {"types": types}


def load_id_patterns() -> Dict[str, re.Pattern]:
    """加载编号格式定义，返回编译后的正则"""
    data = _load_yaml("id_patterns.yaml")
    patterns = {}
    for prefix, pattern_str in data.get("patterns", {}).items():
        try:
            patterns[prefix] = re.compile(f'^({pattern_str})$')
        except re.error:
            continue
    return patterns


def get_required_sections(doc_type: str) -> List[str]:
    """获取指定产物类型的必填章节"""
    config = load_artifact_types()
    types = config.get("types", {})
    return types.get(doc_type, types.get("generic", {})).get("required_sections", [])


def get_id_prefixes(doc_type: str) -> List[str]:
    """获取指定产物类型允许的编号前缀"""
    config = load_artifact_types()
    types = config.get("types", {})
    return types.get(doc_type, types.get("generic", {})).get("id_prefixes", [])


def load_checklist(doc_type: str) -> str:
    """
    加载指定产物类型的语义检查清单

    查找顺序：
    1. CLI --config-dir 指定目录下的 checklists/{type}-checklist.md
    2. 项目 .singularity/config/checklists/{type}-checklist.md
    3. 插件默认 checklists/{type}-checklist.md
    4. 回退到通用检查清单 generic-checklist.md

    Args:
        doc_type: 产物类型（prd/tech/test/generic 等）

    Returns:
        检查清单文件内容字符串，找不到则返回空字符串
    """
    checklist_dirs = []

    # CLI 覆盖
    if _OVERRIDE_CONFIG_DIR:
        checklist_dirs.append(_OVERRIDE_CONFIG_DIR.parent / "checklists")
        checklist_dirs.append(_OVERRIDE_CONFIG_DIR / "checklists")

    # 用户配置
    user_dir = _find_user_config_dir()
    if user_dir.exists():
        checklist_dirs.append(user_dir.parent / "checklists")
        checklist_dirs.append(user_dir / "checklists")

    # 插件默认
    plugin_checklist_dir = _DEFAULT_CONFIG_DIR.parent / "checklists"
    checklist_dirs.append(plugin_checklist_dir)

    # 按优先级查找
    for checklist_dir in checklist_dirs:
        if not checklist_dir.exists():
            continue
        # 先找类型专属
        specific = checklist_dir / f"{doc_type}-checklist.md"
        if specific.exists():
            return specific.read_text(encoding='utf-8')

    # 回退到通用清单
    for checklist_dir in checklist_dirs:
        if not checklist_dir.exists():
            continue
        generic = checklist_dir / "generic-checklist.md"
        if generic.exists():
            return generic.read_text(encoding='utf-8')

    return ""
