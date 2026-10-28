# -*- coding: utf-8 -*-
"""
run.py —— 项目主入口。

用法（在项目目录下）：
    python src/run.py check      只读表 + 清洗 + 对账，验证数字对不对（不出汇总表）
    python src/run.py mapping    生成品名归类清单 config/mapping.xlsx，等你人工确认
    python src/run.py report     出正式汇总表到 output/

也可以直接指定源文件：
    python src/run.py check "C:/某路径/云湖湾2026.6月电子汇总表.xlsx"
"""

from __future__ import annotations

import datetime as dt
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")   # 不让 pandas 的升级提示混进对账结果里

sys.path.insert(0, str(Path(__file__).resolve().parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from paths import get_root                                        # noqa: E402
from loader import load_source                                    # noqa: E402
from classifier import (load_config, build_mapping, load_manual_mapping,  # noqa: E402
                        apply_migrations)
from report import build_report                                   # noqa: E402

ROOT = get_root()
CONFIG_PATH = ROOT / "config" / "categories.yaml"
MAPPING_PATH = ROOT / "config" / "mapping.xlsx"


def _norm_key(code, name) -> tuple:
    """归类表的行标识：编号去前导零（00282 和 282 是同一个菜），空编号统一成 ''。"""
    c = "" if code is None else str(code).strip()
    if c.lower() in ("nan", "none"):
        c = ""
    if c.isdigit():
        c = str(int(c))
    return (c, str(name).strip())


def pick_source(cli_path: str | None = None) -> Path | None:
    """命令行给了就用命令行的，否则扫 input 目录里最新的那张表。"""
    if cli_path:
        return Path(cli_path)
    candidates = [p for p in (ROOT / "input").glob("*.xls*")
                  if not p.name.startswith("~$")]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _line(char: str = "─", width: int = 62) -> str:
    return char * width


def cmd_check(path: Path) -> int:
    print(_line())
    print(f"源文件：{path.name}")
    print(_line())

    config = load_config(CONFIG_PATH)
    sheets, skipped = load_source(path, supplier_aliases=config.get("supplier_aliases"))
    if not sheets:
        print("没读到任何明细表。检查：表里有没有含『品名』的表头行？")
        return 1

    if skipped:
        print(f"已跳过 {len(skipped)} 个工作表：")
        for name, reason in skipped:
            print(f"  · {name}（{reason}）")

    grand_total = 0.0
    ok = True

    for sheet in sheets:
        df = sheet.df
        total = sheet.total_amount
        grand_total += total
        print(f"\n【{sheet.name}】表头在第 {sheet.header_row} 行")
        print(f"  明细行数   {len(df)}")
        print(f"  剔除空行   {sheet.empty_rows}")
        print(f"  剔除合计行 {sheet.summary_rows}")
        if len(df) and df["日期"].notna().any():
            print(f"  日期范围   {df['日期'].min():%Y-%m-%d} ~ {df['日期'].max():%Y-%m-%d}"
                  f"   送货 {df['日期'].nunique()} 天")
        print(f"  菜品数     {df['品名'].nunique()}")
        print(f"  重算合计   {total:,.2f}")

        if sheet.inner_totals:
            nums = " / ".join(f"{amt:,.2f}" for _, amt in sheet.inner_totals)
            print(f"  表内数字   {nums}")
            matched = [amt for _, amt in sheet.inner_totals if abs(amt - total) < 0.05]
            if matched:
                print(f"  对账       ✅ 与表内小计一致（{matched[0]:,.2f}）")
            else:
                print(f"  对账       ⚠️  表内没有任何数字等于重算合计，以重算为准")
                ok = False

        if sheet.warnings:
            print(f"  提醒       {len(sheet.warnings)} 条")
            for w in sheet.warnings[:5]:
                print(f"            - {w}")
            if len(sheet.warnings) > 5:
                print(f"            ... 另有 {len(sheet.warnings) - 5} 条")

    print("\n" + _line())
    print(f"全月总计   {grand_total:,.2f}")
    print(_line())
    return 0 if ok else 2


def cmd_mapping(path: Path) -> int:
    config = load_config(CONFIG_PATH)
    manual = load_manual_mapping(MAPPING_PATH)
    sheets, _ = load_source(path, supplier_aliases=config.get("supplier_aliases"))

    df = build_mapping(sheets, config, manual)
    if not len(df):
        print("没读到明细，无法生成清单。")
        return 1
    apply_migrations(df, config)

    df.to_excel(MAPPING_PATH, index=False, sheet_name="品名归类")

    pending = df[df["判定依据"] == "未匹配"]
    print(_line())
    print(f"已生成归类清单：{MAPPING_PATH}")
    print(f"共 {len(df)} 个菜品")
    print(_line())
    print("各类数量：")
    for cat, n in df["类别"].value_counts().items():
        print(f"  {cat:<12} {n:>4} 个")
    if len(pending):
        print(f"\n⚠️  有 {len(pending)} 个没匹配上规则（类别=待定），必须手工补：")
        for _, r in pending.iterrows():
            print(f"  - {r['品名']}（{r['总金额']:,.2f} 元）")
    print("\n请打开 mapping.xlsx，检查『类别』列，改完后在『确认』列填 y。")
    print("确认过的行以后会优先采用，不会被自动规则覆盖。")
    return 0


def cmd_report(path: Path) -> int:
    config = load_config(CONFIG_PATH)
    manual = load_manual_mapping(MAPPING_PATH)
    sheets, _ = load_source(path, supplier_aliases=config.get("supplier_aliases"))
    if not sheets:
        print("没读到明细表。")
        return 1

    # 归类表：以 mapping.xlsx 里你改过的为准，没改过的用自动规则
    auto = build_mapping(sheets, config, manual)
    mapping_updated = False
    if MAPPING_PATH.exists():
        try:
            edited = pd.read_excel(MAPPING_PATH, dtype={"编号": str})
            # 没有编号的供应商（绿禾）在表里是 NaN，统一成空串才能对上
            edited["编号"] = edited["编号"].fillna("").astype(str).str.strip()
            auto["编号"] = auto["编号"].fillna("").astype(str).str.strip()

            # 只有「确认」列填了 y 的行才具有最高优先级
            confirmed = edited[edited["确认"].astype(str).str.strip().str.lower()
                              .isin(["y", "yes", "1", "是", "√", "v"])]
            if len(confirmed):
                merged = auto.drop(columns=["类别", "判定依据"], errors="ignore").merge(
                    confirmed[["编号", "品名", "类别"]], on=["编号", "品名"], how="left"
                )
                final = merged["类别"].fillna(auto["类别"])
                auto["类别"] = final.values

            # 迁移：新增类别之后，把老菜从旧类挪过去（这一步能覆盖手工确认）
            n_mig = apply_migrations(auto, config)
            if n_mig:
                print(f"已按 migrations 调整 {n_mig} 行归类")

            # 把结果同步回归类表（迁移的成果要落盘）
            # 编号要去前导零再对，否则 00282 改了、282 那行还是旧的
            auto_map = {
                _norm_key(c, n): str(cat).strip()
                for c, n, cat in zip(auto["编号"], auto["品名"], auto["类别"])
            }
            edited["类别"] = [
                auto_map.get(_norm_key(c, n), cat)
                for c, n, cat in zip(edited["编号"], edited["品名"], edited["类别"])
            ]

            # 把 mapping 里没有的新品名补进去（保留你已确认的归类不被覆盖）
            known = set(zip(edited["编号"].astype(str), edited["品名"].astype(str)))
            new_rows = auto[~auto.apply(
                lambda r: (str(r["编号"]).strip(), str(r["品名"]).strip()) in known, axis=1
            )]
            if len(new_rows) or n_mig:
                combined = pd.concat([edited, new_rows], ignore_index=True)
                # 顺手去重：同一个菜（编号去零后相同）只留一行
                combined["_k"] = [_norm_key(c, n) for c, n in
                                  zip(combined["编号"], combined["品名"])]
                combined = combined.drop_duplicates("_k", keep="first").drop(columns="_k")
                combined.to_excel(MAPPING_PATH, index=False, sheet_name="品名归类")
                mapping_updated = True
                if len(new_rows):
                    print(f"已把 {len(new_rows)} 个新品名补进 mapping.xlsx（等你确认归类）")
        except Exception as exc:
            print(f"读取 mapping.xlsx 失败（{exc}），全部使用自动归类")

    # 先对账
    grand = sum(s.total_amount for s in sheets)
    for s in sheets:
        matched = [amt for _, amt in s.inner_totals if abs(amt - s.total_amount) < 0.05]
        status = "✅ 与表内小计一致" if matched else "⚠️  表内数字对不上，以重算为准"
        print(f"{s.name}：{len(s.df)} 行，合计 {s.total_amount:,.2f}  {status}")

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    month = ""
    for s in sheets:
        if len(s.df) and s.df["日期"].notna().any():
            month = s.df["日期"].max().strftime("%Y-%m")
            break

    out = ROOT / "output" / f"汇总表_{month or '未知月份'}_{stamp}.xlsx"
    seq = 2
    while out.exists():
        out = ROOT / "output" / f"汇总表_{month or '未知月份'}_{stamp}_{seq}.xlsx"
        seq += 1

    try:
        build_report(sheets, auto, config, path.name, out)
    except PermissionError:
        print(f"\n❌ 写不进去：{out.name}")
        print("   这个文件正在 Excel 里打开着。请关掉它再跑一次。")
        return 1
    except Exception as exc:
        print(f"\n❌ 生成失败：{type(exc).__name__}: {exc}")
        print("   如果是文件被占用，请先关闭 Excel 里打开的表。")
        return 1

    print(_line())
    print(f"汇总表已生成：{out}")
    print(_line())
    pending = auto[auto["类别"].astype(str).str.strip().isin(["待定", "nan", ""])]
    if len(pending):
        print(f"⚠️  还有 {len(pending)} 个品名没归类，已单列在『待补充』工作表")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    mode = argv[0] if argv else "check"
    cli_path = argv[1] if len(argv) > 1 else None

    path = pick_source(cli_path)
    if path is None or not path.exists():
        print("找不到源文件。把表放进 input/ 目录，或在命令后面写上文件路径。")
        return 1

    if mode == "check":
        return cmd_check(path)
    if mode == "mapping":
        return cmd_mapping(path)
    if mode == "report":
        return cmd_report(path)

    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
