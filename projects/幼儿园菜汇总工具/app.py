# -*- coding: utf-8 -*-
"""
app.py —— 给同事用的交互入口（打包成 exe 之后，双击跑的就是它）。

两种用法：
  双击 exe            → 显示菜单，汇总 input\\ 里最新的表
  把 xlsx 拖到 exe 上 → 直接汇总那张表
"""

from __future__ import annotations

import shutil
import sys
import warnings
from pathlib import Path

# 同事看到的窗口要干干净净的，把 pandas 那些升级提示压掉
warnings.filterwarnings("ignore")

# ---------- 中文不乱码：先把控制台切到 UTF-8 ----------
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from paths import get_root, bundle_dir, is_frozen      # noqa: E402
from run import cmd_report, cmd_check                  # noqa: E402

LINE = "─" * 62


def pause(msg: str = "\n按回车继续..."):
    """只在 exe 模式下停住，跑脚本时不打断。"""
    if not is_frozen():
        return
    try:
        input(msg)
    except (EOFError, KeyboardInterrupt):
        pass


def ensure_dirs() -> Path:
    """保证程序旁边有 config / input / output；config 没有就从内置那份复制出来。"""
    root = get_root()
    for name in ("config", "input", "output"):
        (root / name).mkdir(parents=True, exist_ok=True)

    cfg = root / "config"
    if not (cfg / "categories.yaml").exists():
        builtin = bundle_dir() / "config"
        if (builtin / "categories.yaml").exists():
            try:
                shutil.copy2(builtin / "categories.yaml", cfg / "categories.yaml")
                if (builtin / "mapping.xlsx").exists():
                    shutil.copy2(builtin / "mapping.xlsx", cfg / "mapping.xlsx")
                print(f"  已在程序旁边生成 config\\ 文件夹（可以直接改里面的归类表）")
            except Exception as exc:
                print(f"  config 释放失败：{exc}")
    return root


def list_inputs(root: Path) -> list:
    files = [p for p in (root / "input").glob("*.xls*") if not p.name.startswith("~$")]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def do_report(path: Path) -> int:
    try:
        return cmd_report(path)
    except PermissionError:
        print("\n  写不进去。output 里那个同名文件是不是正开着？关掉 Excel 再跑一次。")
        return 1
    except Exception as exc:
        print(f"\n  出错了：{type(exc).__name__}: {exc}")
        return 1


def do_check(path: Path) -> int:
    try:
        return cmd_check(path)
    except Exception as exc:
        print(f"\n  出错了：{type(exc).__name__}: {exc}")
        return 1


def menu(root: Path) -> int:
    while True:
        inputs = list_inputs(root)
        print()
        print(LINE)
        print("  幼儿园菜品配送 · 月度汇总工具")
        print(LINE)
        if inputs:
            print(f"  1   汇总 input\\ 里最新的表")
            print(f"      {inputs[0].name}")
            if len(inputs) > 1:
                print(f"      （还有 {len(inputs) - 1} 张更早的表，想跑它们就拖到本程序图标上）")
        else:
            print("  1   汇总（input\\ 里还没有表）")
        print("  2   只核对数字，不出表")
        print("  0   退出")
        print(LINE)
        try:
            choice = input("  请输入数字后回车：").strip()
        except (EOFError, KeyboardInterrupt):
            return 0

        if choice in ("0", "q", "Q"):
            return 0
        if choice == "1":
            if not inputs:
                pause("\n  input\\ 里没有表。把送货单放进去，或直接拖到本程序图标上。\n  按回车继续...")
                continue
            do_report(inputs[0])
            pause("\n  按回车返回菜单...")
        elif choice == "2":
            if not inputs:
                pause("\n  input\\ 里没有表。按回车继续...")
                continue
            do_check(inputs[0])
            pause("\n  按回车返回菜单...")
        else:
            print("  没有这个选项，再看一眼。")


def main() -> int:
    root = ensure_dirs()
    print(LINE)
    print(f"  程序位置：{root}")
    print(LINE)

    # 拖文件到 exe 上 → 直接跑
    dropped = [a for a in sys.argv[1:] if a.lower().endswith((".xlsx", ".xls"))]
    dropped = [a for a in dropped if Path(a).exists()]
    if dropped:
        rc = do_report(Path(dropped[0]))
        pause("\n  按回车关闭窗口...")
        return rc

    return menu(root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
