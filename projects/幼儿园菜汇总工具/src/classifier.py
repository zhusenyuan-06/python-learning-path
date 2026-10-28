# -*- coding: utf-8 -*-
"""
classifier.py —— 把品名归入八类。

归类优先级：
  1. mapping.xlsx 里你手工确认过的（最高，永远听你的）
  2. categories.yaml 里的老板裁决 overrides
  3. categories.yaml 里的关键词规则
  4. 都匹配不上 -> 待定（会单独列出来提醒你补）
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

MAPPING_COLUMNS = ["编号", "品名", "单位", "类别", "判定依据", "确认"]


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def classify(name: str, code: str, config: dict, manual: dict | None = None):
    """返回 (类别, 判定依据)。

    判定依据可能是：手工确认 / 老板裁决 / 关键词:XX / 未匹配
    """
    name = str(name).strip()
    code = str(code).strip()

    # 1. 手工确认过的（品名优先，其次编号 —— 因为有的供应商压根没有商品编号）
    if manual:
        if name in manual.get("__by_name__", {}):
            return manual["__by_name__"][name]["类别"], "手工确认"
        if code and code in manual:
            return manual[code]["类别"], "手工确认"

    # 2. 老板裁决
    for rule in config.get("overrides", []) or []:
        if str(rule.get("match", "")) in name:
            return rule["category"], "老板裁决"

    # 3. 关键词规则，按顺序命中即停
    for rule in config.get("keyword_rules", []) or []:
        for kw in rule.get("keywords", []) or []:
            if str(kw) in name:
                return rule["category"], f"关键词:{kw}"

    # 4. 兜底
    return config.get("fallback_category", "待定"), "未匹配"


def load_manual_mapping(path: str | Path) -> dict:
    """读 mapping.xlsx 里已确认的行。返回 {编号: {类别:..}} 和 {品名: {...}}。"""
    manual: dict = {"__by_name__": {}}
    p = Path(path)
    if not p.exists():
        return manual
    try:
        df = pd.read_excel(p, dtype={"编号": str})
    except Exception:
        return manual
    if "确认" not in df.columns or "类别" not in df.columns:
        return manual
    for _, row in df.iterrows():
        if str(row.get("确认", "")).strip().lower() in ("y", "yes", "1", "是", "√", "v"):
            cat = str(row.get("类别", "")).strip()
            if not cat:
                continue
            code = str(row.get("编号", "")).strip()
            name = str(row.get("品名", "")).strip()
            if code and code != "nan":
                manual[code] = {"类别": cat}
            if name and name != "nan":
                manual["__by_name__"][name] = {"类别": cat}
    return manual


def build_mapping(sheets, config: dict, manual: dict | None = None) -> pd.DataFrame:
    """把所有出现过的品名汇总成一张待确认清单。"""
    frames = []
    for sheet in sheets:
        df = sheet.df
        if not len(df):
            continue
        tmp = df.copy()
        tmp["_sheet"] = sheet.name
        frames.append(tmp)

    if not frames:
        return pd.DataFrame(columns=MAPPING_COLUMNS)

    all_rows = pd.concat(frames, ignore_index=True)

    grouped = all_rows.groupby(["编号", "品名"], as_index=False).agg(
        送货次数=("日期", "nunique"),
        总数量=("实收数量", "sum"),
        总金额=("重算金额", "sum"),
        单位=("单位", lambda s: "/".join(sorted({str(x) for x in s if str(x).strip()}))),
        出现在=("_sheet", lambda s: "、".join(sorted(set(s)))),
    )

    grouped["总数量"] = grouped["总数量"].round(2)
    grouped["总金额"] = grouped["总金额"].round(2)

    categories, reasons = [], []
    for _, row in grouped.iterrows():
        cat, reason = classify(row["品名"], row["编号"], config, manual)
        categories.append(cat)
        reasons.append(reason)

    grouped["类别"] = categories
    grouped["判定依据"] = reasons
    grouped["确认"] = ""

    grouped = grouped.sort_values(["类别", "总金额"], ascending=[True, False])
    return grouped[["编号", "品名", "单位", "类别", "判定依据", "确认",
                    "总数量", "送货次数", "总金额", "出现在"]].reset_index(drop=True)


def apply_migrations(df: pd.DataFrame, config: dict) -> int:
    """按 categories.yaml 的 migrations 节，把归类表里**已经确认过**的行挪到新类。

    比如新增「豆制品」之后，豆腐原先在蔬菜里且打过 y，光靠关键词改不动它，
    就靠这里一次性迁移。返回改动的行数。
    """
    rules = config.get("migrations", []) or []
    if df is None or not len(df) or not rules:
        return 0

    changed = 0
    for rule in rules:
        to = str(rule.get("to", "")).strip()
        words = rule.get("match", []) or []
        if not to:
            continue
        for word in words:
            word = str(word).strip()
            if not word:
                continue
            mask = df["品名"].astype(str).str.contains(word, na=False)
            mask &= df["类别"].astype(str).str.strip() != to
            n = int(mask.sum())
            if n:
                df.loc[mask, "类别"] = to
                df.loc[mask, "判定依据"] = f"迁移:{word}"
                changed += n
    return changed
