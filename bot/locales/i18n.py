"""
国际化支持
"""

import json
from pathlib import Path
from typing import Optional

# 加载语言文件
LOCALE_DIR = Path(__file__).parent


def load_locale(locale: str = "zh") -> dict:
    """加载语言包"""
    locale_file = LOCALE_DIR / f"{locale}.json"
    if not locale_file.exists():
        locale_file = LOCALE_DIR / "zh.json"

    with open(locale_file, "r", encoding="utf-8") as f:
        return json.load(f)


# 默认语言包
DEFAULT_LOCALE = load_locale("zh")


def get_text(key: str, locale: str = "zh", **kwargs) -> str:
    """获取翻译文本"""
    locale_data = load_locale(locale)

    # 支持嵌套键，如 "start.welcome"
    keys = key.split(".")
    value = locale_data

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # 回退到默认语言
            value = DEFAULT_LOCALE
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return key  # 返回键名作为默认值

    # 格式化文本
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value

    return value if isinstance(value, str) else key


def get_all_locales() -> list:
    """获取所有可用语言"""
    return [f.stem for f in LOCALE_DIR.glob("*.json")]
