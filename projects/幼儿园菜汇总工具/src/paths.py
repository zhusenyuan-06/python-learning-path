# -*- coding: utf-8 -*-
"""
paths.py —— 统一决定「项目根目录」在哪。

- 跑脚本时：根目录 = src 的上一级（<项目目录>）
- 打包成 exe 后：根目录 = exe 所在的那个文件夹

这样 config / input / output / 月度台账 都落在同事看得见的地方，
不会跑到 exe 内部的临时目录里去（否则同事改不了归类、也找不到结果）。
"""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """True 表示现在是打包后的 exe 在运行。"""
    return bool(getattr(sys, "frozen", False))


def get_root() -> Path:
    """项目根目录：exe 所在目录（打包后）或 src 的上级（跑脚本时）。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def bundle_dir() -> Path:
    """打包时被塞进 exe 里的资源目录（--add-data 带进来的）。没打包时就是项目根。"""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


def get_src() -> Path:
    """脚本目录。打包后指向 exe 内部，import 模块用得到。"""
    return Path(__file__).resolve().parent


ROOT = get_root()
