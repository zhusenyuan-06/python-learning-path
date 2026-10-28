# -*- coding: utf-8 -*-
"""
import_mapping.py —— 把外面整理好的归类表导入成 config/mapping.xlsx。

用法：
    python src/import_mapping.py "C:/某路径/mapping.xlsx"

导入时顺手清洗四件事：
  1. 删掉被误当菜品的表内分类标题行（蔬菜类 / 豆制品 / 水果、糕点、坚果类 …）
  2. 把写歪的类别名统一成标准类别（水果坚果糕点、水果 -> 水果坚果）
  3. 合并编号前导零不一致造成的重复行（00011 和 11 是同一个菜）
  4. 按 categories.yaml 的 migrations 节做一次迁移（比如新增豆制品后挪豆腐）

原文件不会被修改，只写 config/mapping.xlsx。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classifier import apply_migrations, load_config  # noqa: E402
from paths import get_root                            # noqa: E402

ROOT = get_root()
CONFIG_PATH = ROOT / "config" / "categories.yaml"
MAPPING_PATH = ROOT / "config" / "mapping.xlsx"

# 原表里那些"分类标题行"的常见写法（只有编号为空的才算，避免误伤真菜品）
CATEGORY_TITLES = {
    "米、粉、面", "食用油", "干货、调料", "肉禽类", "蛋类", "蔬菜类",
    "豆制品", "奶制品", "水果、糕点、坚果类",
    "米面类", "粮油类", "调味类", "水产类", "肉类", "水果类", "坚果类",
}

# 写歪的类别名 -> 标准类别
CANON = {
    "水果坚果糕点": "水果坚果",
    "水果糕点坚果": "水果坚果",
    "水果": "水果坚果",
    "糕点": "水果坚果",
    "豆类": "豆制品",
    "豆制": "豆制品",
    "肉类": "水产和肉类",
    "水产": "水产和肉类",
    "调味": "干货调味",
    "调料": "干货调味",
    "米面粮油": "米面",
}


def _norm_code(code) -> str:
    """编号规范化：纯数字去掉前导零（00011 和 11 视作同一个）。"""
    s = str(code).strip()
    if s.lower() in ("", "nan", "none"):
        return ""
    if s.isdigit():
        return str(int(s))
    return s


def clean(df: pd.DataFrame, config: dict) -> tuple:
    """返回 (清洗后的表, 操作日志列表)。"""
    log = []
    df = df.copy()
    n0 = len(df)

    # 1. 删分类标题行：编号为空 且 品名正好是某个分类标题
    df["_code"] = df["编号"].apply(_norm_code)
    df["_name"] = df["品名"].astype(str).str.strip()
    mask = (df["_code"] == "") & (df["_name"].isin(CATEGORY_TITLES))
    if mask.any():
        log.append(f"删掉 {int(mask.sum())} 行表内分类标题（误当菜品的）："
                   f"{'、'.join(sorted(set(df.loc[mask, '_name'])))}")
        df = df[~mask]

    # 2. 统一类别名
    changed = 0
    cats = df["类别"].astype(str).str.strip()
    for wrong, right in CANON.items():
        hit = cats == wrong
        if hit.any():
            changed += int(hit.sum())
            cats = cats.mask(hit, right)
    if changed:
        log.append(f"统一了 {changed} 行写歪的类别名（如 水果/水果坚果糕点 -> 水果坚果）")
    df["类别"] = cats

    # 3. 合并重复（同一 编号+品名 只留一行，优先留确认过的）
    df["_conf"] = df["确认"].astype(str).str.strip().str.lower().isin(
        ["y", "yes", "1", "是", "√", "v"]).astype(int)
    before = len(df)
    df = df.sort_values("_conf", ascending=False).drop_duplicates(
        subset=["_code", "_name"], keep="first")
    if len(df) < before:
        log.append(f"合并了 {before - len(df)} 行重复（编号前导零不同造成的）")

    # 4. 迁移（新增类别后把老菜挪过去）
    n_mig = apply_migrations(df, config)
    if n_mig:
        log.append(f"按 migrations 迁移了 {n_mig} 行归类")

    df = df.drop(columns=["_code", "_name", "_conf"], errors="ignore")
    df = df.sort_values(["类别", "品名"]).reset_index(drop=True)
    log.append(f"最终 {len(df)} 行（原表 {n0} 行）")
    return df, log


def main():
    if len(sys.argv) < 2:
        print("用法：python src/import_mapping.py <归类表.xlsx>")
        return 1
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"找不到文件：{src}")
        return 1

    config = load_config(CONFIG_PATH)
    df = pd.read_excel(src, dtype={"编号": str})
    for col in ("编号", "品名", "单位", "类别", "判定依据", "确认"):
        if col not in df.columns:
            df[col] = ""
    df["编号"] = df["编号"].astype(str).str.strip()

    cleaned, log = clean(df, config)
    MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_excel(MAPPING_PATH, index=False, sheet_name="品名归类")

    print("─" * 60)
    print(f"已从 {src.name} 导入归类表")
    print("─" * 60)
    for line in log:
        print(f"  · {line}")
    print("─" * 60)
    print("各类别条数：")
    for cat, n in cleaned["类别"].value_counts().items():
        print(f"  {cat:<12} {n:>4}")
    pending = cleaned[cleaned["类别"].astype(str).str.strip() == "待定"]
    if len(pending):
        print(f"\n还有 {len(pending)} 个待定：")
        for _, r in pending.head(20).iterrows():
            print(f"  - {r['品名']}")
    print(f"\n已写入：{MAPPING_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
