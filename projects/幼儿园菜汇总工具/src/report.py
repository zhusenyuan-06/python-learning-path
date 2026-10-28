# -*- coding: utf-8 -*-
"""
report.py —— 生成汇总表（五个工作表）。

输出结构：
  1. {人群}汇总    按类别分组的菜品明细，每类带小计
  2. {人群}日期    送货日 × 八类金额，带自然周小计
  3. 类别总览      八类在两表中的金额对比
  4. 待补充        没归上类的品名（有才出现）
  5. 图表          各类占比饼图 + 各月趋势 + 本月每日趋势

月度趋势的数据来自 data/月度台账.csv，每次出表自动累积（同月重跑会覆盖）。
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import get_root                                        # noqa: E402

ROOT = get_root()
HISTORY_PATH = ROOT / "data" / "月度台账.csv"

# 八个类别的固定配色，保证三张饼图、堆叠图颜色一致
CAT_COLORS = {
    "蔬菜": "#6AA84F",
    "水产和肉类": "#CC0000",
    "米面": "#E69138",
    "水果坚果": "#FFD966",
    "蛋": "#C27BA0",
    "奶制品": "#A2C4C9",
    "干货调味": "#8E7CC3",
    "油": "#666666",
    "待定": "#BFBFBF",
}


def attach_category(df: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """给明细加上『类别』列。

    先按 (编号, 品名) 精确查，查不到再按品名查
    —— 因为有的供应商（绿禾）压根没有商品编号，只能认品名。
    """
    def norm_code(raw) -> str:
        """编号去前导零（00011 和 11 视作同一个），空值统一成 ''。"""
        s = "" if raw is None else str(raw).strip()
        if s.lower() in ("nan", "none"):
            return ""
        return str(int(s)) if s.isdigit() else s

    by_pair, by_name = {}, {}
    for _, row in mapping.iterrows():
        cat = str(row["类别"]).strip() or "待定"
        name = str(row["品名"]).strip()
        key = (norm_code(row["编号"]), name)
        by_pair.setdefault(key, cat)
        if name and name != "nan":
            by_name.setdefault(name, cat)

    df = df.copy()
    result = []
    for code, name in zip(df["编号"], df["品名"]):
        name = str(name).strip()
        result.append(
            by_pair.get((norm_code(code), name)) or by_name.get(name) or "待定"
        )
    df["类别"] = result
    return df


def aggregate_items(df: pd.DataFrame, categories: list) -> pd.DataFrame:
    """菜品级汇总：类别 / 编号 / 品名 / 单位 / 送货次数 / 总数量 / 均价 / 总金额。"""
    g = df.groupby(["类别", "编号", "品名", "单位"], as_index=False).agg(
        送货次数=("日期", "nunique"),
        总数量=("实收数量", "sum"),
        总金额=("重算金额", "sum"),
    )
    g["总数量"] = g["总数量"].round(2)
    g["总金额"] = g["总金额"].round(2)
    g["加权均价"] = np.where(g["总数量"] > 0, (g["总金额"] / g["总数量"]).round(2), 0.0)

    order = {c: i for i, c in enumerate(categories)}
    g["_ord"] = g["类别"].map(lambda c: order.get(c, 99))
    g = g.sort_values(["_ord", "总金额"], ascending=[True, False]).drop(columns="_ord")
    return g


def build_date_pivot(df: pd.DataFrame, categories: list) -> pd.DataFrame:
    """日期 × 类别 的金额透视，带星期和自然周。"""
    df = df.copy()
    df["类别"] = df["类别"].fillna("待定")
    pivot = df.pivot_table(
        index="日期", columns="类别", values="重算金额", aggfunc="sum", fill_value=0.0
    )
    for cat in categories:
        if cat not in pivot.columns:
            pivot[cat] = 0.0
    extra = [c for c in pivot.columns if c not in categories]
    pivot = pivot[categories + extra]
    pivot["当日合计"] = pivot.sum(axis=1)
    pivot = pivot.reset_index().sort_values("日期")

    pivot["星期"] = pivot["日期"].dt.dayofweek.map(
        {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    )
    # 自然周：以周一为一周起点
    pivot["周"] = pivot["日期"].dt.to_period("W-SUN").dt.start_time
    return pivot


def month_of(sheets) -> str:
    """从明细里取月份（YYYY-MM），取不到就用今天。"""
    for s in sheets:
        df = getattr(s, "df", None)
        if df is not None and len(df) and df["日期"].notna().any():
            return df["日期"].max().strftime("%Y-%m")
    return dt.datetime.now().strftime("%Y-%m")


def update_history(month: str, per_sheet: dict, path: Path = HISTORY_PATH) -> pd.DataFrame:
    """把本月的各类金额写进月度台账；同一个月重跑会覆盖旧记录。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = []
    for name, series in per_sheet.items():
        for cat, amt in series.items():
            rows.append({
                "月份": month, "人群": str(name), "类别": str(cat),
                "金额": round(float(amt), 2), "更新时间": stamp,
            })
    new = pd.DataFrame(rows)

    if path.exists():
        try:
            old = pd.read_csv(path, encoding="utf-8-sig")
            old = old[old["月份"].astype(str) != month]
            merged = pd.concat([old, new], ignore_index=True)
        except Exception:
            merged = new
    else:
        merged = new

    merged = merged.sort_values(["月份", "人群", "类别"])
    merged.to_csv(path, index=False, encoding="utf-8-sig")
    return merged


def read_history(path: Path = HISTORY_PATH, max_months: int = 12) -> pd.DataFrame:
    """读台账并整理成 行=月份、列=类别（+合计）的表。"""
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame()
    if not len(df) or "月份" not in df.columns:
        return pd.DataFrame()
    p = df.pivot_table(index="月份", columns="类别", values="金额",
                       aggfunc="sum", fill_value=0.0)
    p = p.sort_index().tail(max_months)
    p["合计"] = p.sum(axis=1)
    return p


def combine_daily(pivots: dict, categories: list) -> pd.DataFrame:
    """把各人群的日期透视按日期相加，得到全园每日金额。"""
    cols = [c for c in list(categories) + ["待定"]]
    frames = []
    for p in pivots.values():
        if not len(p):
            continue
        use = [c for c in cols if c in p.columns] + ["当日合计"]
        frames.append(p.set_index("日期")[use])
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames).groupby(level=0).sum().reset_index().sort_values("日期")
    return out


class Writer:
    """把汇总结果写进 xlsx，顺手把格式弄好看。"""

    def __init__(self, path: Path, source_name: str, colors: dict | None = None):
        self.path = Path(path)
        self.source_name = source_name
        # 类别配色：以配置文件的为准，配置里没写的用默认色
        self.colors = {**CAT_COLORS, **(colors or {})}
        self.writer = pd.ExcelWriter(path, engine="xlsxwriter", datetime_format="yyyy-mm-dd")
        self.book = self.writer.book

        self.f_note = self.book.add_format({"font_size": 9, "font_color": "#888780"})
        self.f_head = self.book.add_format({
            "bold": True, "bg_color": "#E6F1FB", "border": 1, "border_color": "#B5D4F4",
            "align": "center", "valign": "vcenter", "text_wrap": True,
        })
        self.f_text = self.book.add_format({"border": 1, "border_color": "#E6E6E0"})
        self.f_num = self.book.add_format({"border": 1, "border_color": "#E6E6E0", "num_format": "#,##0.00"})
        self.f_date = self.book.add_format({"border": 1, "border_color": "#E6E6E0", "num_format": "yyyy-mm-dd"})
        self.f_int = self.book.add_format({"border": 1, "border_color": "#E6E6E0", "num_format": "0"})
        self.f_pct = self.book.add_format({"border": 1, "border_color": "#E6E6E0", "num_format": "0.0%"})
        self.f_sub = self.book.add_format({
            "bold": True, "bg_color": "#F1EFE8", "border": 1, "border_color": "#D3D1C7",
            "num_format": "#,##0.00",
        })
        self.f_subtext = self.book.add_format({
            "bold": True, "bg_color": "#F1EFE8", "border": 1, "border_color": "#D3D1C7",
        })
        self.f_total = self.book.add_format({
            "bold": True, "bg_color": "#B5D4F4", "border": 1, "border_color": "#85B7EB",
            "num_format": "#,##0.00",
        })
        self.f_totaltext = self.book.add_format({
            "bold": True, "bg_color": "#B5D4F4", "border": 1, "border_color": "#85B7EB",
        })

    def _note(self, ws, text: str, width: int):
        ws.write(0, 0, text, self.f_note)
        ws.set_row(0, 18)

    def write_items(self, sheet_name: str, agg: pd.DataFrame, categories: list, total: float):
        ws = self.book.add_worksheet(sheet_name)
        self.writer.sheets[sheet_name] = ws
        self._note(ws, f"数据来源：{self.source_name}   生成时间：{dt.datetime.now():%Y-%m-%d %H:%M}", 10)

        headers = ["类别", "编号", "品名", "单位", "送货次数", "总数量", "加权均价", "总金额", "占比"]
        widths = [12, 10, 26, 8, 10, 12, 12, 14, 10]
        for c, (h, w) in enumerate(zip(headers, widths)):
            ws.write(1, c, h, self.f_head)
            ws.set_column(c, c, w)
        ws.freeze_panes(2, 0)

        row = 2
        for cat in [c for c in categories if c in set(agg["类别"])] + (
                ["待定"] if "待定" in set(agg["类别"]) else []):
            block = agg[agg["类别"] == cat]
            for _, r in block.iterrows():
                ws.write(row, 0, r["类别"], self.f_text)
                ws.write(row, 1, str(r["编号"]), self.f_text)
                ws.write(row, 2, r["品名"], self.f_text)
                ws.write(row, 3, r["单位"], self.f_text)
                ws.write_number(row, 4, int(r["送货次数"]), self.f_int)
                ws.write_number(row, 5, float(r["总数量"]), self.f_num)
                ws.write_number(row, 6, float(r["加权均价"]), self.f_num)
                ws.write_number(row, 7, float(r["总金额"]), self.f_num)
                ws.write_number(row, 8, float(r["总金额"]) / total if total else 0, self.f_pct)
                row += 1
            sub = float(block["总金额"].sum())
            ws.write(row, 0, f"{cat} 小计", self.f_subtext)
            for c in range(1, 5):
                ws.write_blank(row, c, None, self.f_subtext)
            ws.write_blank(row, 5, None, self.f_subtext)
            ws.write_blank(row, 6, None, self.f_subtext)
            ws.write_number(row, 7, sub, self.f_sub)
            ws.write_number(row, 8, sub / total if total else 0, self.f_sub)
            row += 1

        ws.write(row, 0, "总计", self.f_totaltext)
        for c in range(1, 8):
            ws.write_blank(row, c, None, self.f_totaltext)
        ws.write_number(row, 7, total, self.f_total)
        ws.write_number(row, 8, 1.0, self.f_total)
        return ws

    def write_dates(self, sheet_name: str, pivot: pd.DataFrame, categories: list):
        ws = self.book.add_worksheet(sheet_name)
        self.writer.sheets[sheet_name] = ws
        self._note(ws, f"数据来源：{self.source_name}   按送货日统计，灰色行为自然周小计", 10)

        cols = list(categories) + (["待定"] if "待定" in pivot.columns else [])
        headers = ["日期", "星期"] + cols + ["当日合计"]
        for c, h in enumerate(headers):
            ws.write(1, c, h, self.f_head)
        ws.set_column(0, 0, 12)
        ws.set_column(1, 1, 6)
        ws.set_column(2, len(headers) - 1, 12)
        ws.freeze_panes(2, 0)

        row = 2
        for week_start, block in pivot.groupby("周", sort=True):
            for _, r in block.iterrows():
                ws.write_datetime(row, 0, r["日期"].to_pydatetime(), self.f_date)
                ws.write(row, 1, r["星期"], self.f_text)
                c = 2
                for cat in cols:
                    ws.write_number(row, c, float(r.get(cat, 0)), self.f_num)
                    c += 1
                ws.write_number(row, c, float(r["当日合计"]), self.f_num)
                row += 1
            ws.write(row, 0, f"{week_start:%m/%d} 当周小计", self.f_subtext)
            ws.write_blank(row, 1, None, self.f_subtext)
            c = 2
            for cat in cols:
                ws.write_number(row, c, float(block[cat].sum()), self.f_sub)
                c += 1
            ws.write_number(row, c, float(block["当日合计"].sum()), self.f_sub)
            row += 1
        return ws

    def write_overview(self, per_sheet: dict, categories: list):
        ws = self.book.add_worksheet("类别总览")
        self.writer.sheets["类别总览"] = ws
        self._note(ws, f"数据来源：{self.source_name}   两表对照", 10)

        names = list(per_sheet.keys())
        headers = ["类别"] + [f"{n}金额" for n in names] + ["合计", "占比"]
        for c, h in enumerate(headers):
            ws.write(1, c, h, self.f_head)
        ws.set_column(0, 0, 14)
        ws.set_column(1, len(headers) - 1, 14)
        ws.freeze_panes(2, 0)

        used = [c for c in categories + ["待定"]
                if any(c in set(v.index) for v in per_sheet.values())]
        grand = sum(float(v.sum()) for v in per_sheet.values())

        row = 2
        for cat in used:
            ws.write(row, 0, cat, self.f_text)
            vals = [float(per_sheet[n].get(cat, 0.0)) for n in names]
            for i, v in enumerate(vals):
                ws.write_number(row, 1 + i, v, self.f_num)
            ws.write_number(row, 1 + len(names), sum(vals), self.f_num)
            ws.write_number(row, 2 + len(names), sum(vals) / grand if grand else 0, self.f_pct)
            row += 1

        ws.write(row, 0, "总计", self.f_totaltext)
        for i, n in enumerate(names):
            ws.write_number(row, 1 + i, float(per_sheet[n].sum()), self.f_total)
        ws.write_number(row, 1 + len(names), grand, self.f_total)
        ws.write_number(row, 2 + len(names), 1.0, self.f_total)
        return ws

    def write_pending(self, pending: pd.DataFrame):
        ws = self.book.add_worksheet("待补充")
        self.writer.sheets["待补充"] = ws
        self._note(ws, "这些品名没归上类，请在 config/mapping.xlsx 里补类别后重跑", 10)
        headers = ["编号", "品名", "单位", "总金额", "送货次数"]
        for c, h in enumerate(headers):
            ws.write(1, c, h, self.f_head)
        ws.set_column(0, 0, 10)
        ws.set_column(1, 1, 28)
        ws.set_column(2, 2, 8)
        ws.set_column(3, 4, 12)
        ws.freeze_panes(2, 0)
        for i, (_, r) in enumerate(pending.iterrows(), start=2):
            ws.write(i, 0, str(r["编号"]), self.f_text)
            ws.write(i, 1, r["品名"], self.f_text)
            ws.write(i, 2, r["单位"], self.f_text)
            ws.write_number(i, 3, float(r["总金额"]), self.f_num)
            ws.write_number(i, 4, int(r["送货次数"]), self.f_int)
        return ws

    # 图表区占据第 3~50 行，数据块统一藏在 56 行以下
    CHART_DATA_ROW = 56

    def write_charts(self, per_sheet: dict, categories: list,
                     daily: pd.DataFrame, history: pd.DataFrame):
        """生成『图表』工作表：饼图（占比）+ 柱图（按月趋势）+ 折线（每日趋势）。"""
        ws = self.book.add_worksheet("图表")
        self.writer.sheets["图表"] = ws
        self._note(ws, f"数据来源：{self.source_name}    月度趋势来自 data/月度台账.csv"
                       f"（每次出表自动累积，同月重跑会覆盖）", 12)
        for c in range(0, 20):
            ws.set_column(c, c, 11)

        names = list(per_sheet.keys())
        cat_order = [str(c) for c in categories] + ["待定"]

        # ---------- 1. 饼图：每个一张 + 全园合计一张 ----------
        blocks = [(n, {str(k): float(v) for k, v in per_sheet[n].items()}) for n in names]
        if len(names) > 1:
            grand: dict = {}
            for series in blocks:
                for c, v in series[1].items():
                    grand[c] = grand.get(c, 0.0) + v
            blocks.append(("全园合计", grand))

        pie_blocks = []
        base = self.CHART_DATA_ROW
        for i, (title, series) in enumerate(blocks[:3]):
            cc = i * 3
            ws.write(base, cc, "类别", self.f_head)
            ws.write(base, cc + 1, "金额", self.f_head)
            items = [(c, float(series.get(c, 0.0))) for c in cat_order
                     if float(series.get(c, 0.0)) > 0]
            items += [(c, float(v)) for c, v in series.items()
                      if c not in cat_order and float(v) > 0]
            r = base + 1
            for c, v in items:
                ws.write(r, cc, c, self.f_text)
                ws.write_number(r, cc + 1, v, self.f_num)
                r += 1
            if r > base + 1:
                pie_blocks.append((title, base + 1, r - 1, cc, [c for c, _ in items]))

        pie_pos = [(3, 1), (3, 10), (19, 1)]
        for idx, (title, r0, r1, cc, cats) in enumerate(pie_blocks[:3]):
            ch = self.book.add_chart({"type": "pie"})
            ch.add_series({
                "name": title,
                "categories": ["图表", r0, cc, r1, cc],
                "values": ["图表", r0, cc + 1, r1, cc + 1],
                "data_labels": {"category": True, "percentage": True, "font": {"size": 9}},
                "points": [{"fill": {"color": self.colors.get(c, "#BFBFBF")}} for c in cats],
            })
            ch.set_title({"name": f"{title} · 各类金额占比"})
            ch.set_legend({"none": True})
            ch.set_size({"width": 460, "height": 280})
            ws.insert_chart(pie_pos[idx][0], pie_pos[idx][1], ch)

        # ---------- 2. 月度台账（柱图 + 堆叠柱图）----------
        hist_cats: list = []
        n_hist = 0
        if len(history):
            hist_cats = [c for c in cat_order if c in history.columns] + \
                        [c for c in history.columns if c not in cat_order and c != "合计"]
            hr = base + 12
            ws.write(hr, 0, "月份", self.f_head)
            for j, c in enumerate(hist_cats):
                ws.write(hr, 1 + j, c, self.f_head)
            ws.write(hr, 1 + len(hist_cats), "合计", self.f_head)
            for i, (m, row) in enumerate(history.iterrows()):
                ws.write(hr + 1 + i, 0, str(m), self.f_text)
                for j, c in enumerate(hist_cats):
                    ws.write_number(hr + 1 + i, 1 + j, float(row.get(c, 0.0)), self.f_num)
                ws.write_number(hr + 1 + i, 1 + len(hist_cats),
                                float(row.get("合计", 0.0)), self.f_num)
            n_hist = len(history)
            h0, h1 = hr + 1, hr + n_hist
            tcol = 1 + len(hist_cats)

            ch = self.book.add_chart({"type": "column"})
            ch.add_series({
                "name": "当月金额",
                "categories": ["图表", h0, 0, h1, 0],
                "values": ["图表", h0, tcol, h1, tcol],
                "data_labels": {"value": True, "num_format": "#,##0"},
                "fill": {"color": "#4A86C8"},
            })
            ch.set_title({"name": "各月采购总额趋势"})
            ch.set_legend({"none": True})
            ch.set_y_axis({"num_format": "#,##0"})
            ch.set_size({"width": 460, "height": 280})
            ws.insert_chart(35, 1, ch)

            ch2 = self.book.add_chart({"type": "column", "subtype": "stacked"})
            for j, c in enumerate(hist_cats):
                ch2.add_series({
                    "name": c,
                    "categories": ["图表", h0, 0, h1, 0],
                    "values": ["图表", h0, 1 + j, h1, 1 + j],
                    "fill": {"color": self.colors.get(c, "#BFBFBF")},
                })
            ch2.set_title({"name": "各月类别结构（堆叠）"})
            ch2.set_y_axis({"num_format": "#,##0"})
            ch2.set_size({"width": 620, "height": 280})
            ws.insert_chart(35, 10, ch2)

        # ---------- 3. 本月每日趋势（折线）----------
        if len(daily) >= 2:
            dr = base + 12 + n_hist + 3
            day_cats = [c for c in daily.columns if c != "日期"]
            ws.write(dr, 0, "日期", self.f_head)
            for j, c in enumerate(day_cats):
                ws.write(dr, 1 + j, c, self.f_head)
            for i, (_, r) in enumerate(daily.iterrows()):
                try:
                    ws.write_datetime(dr + 1 + i, 0,
                                      pd.Timestamp(r["日期"]).to_pydatetime(), self.f_date)
                except Exception:
                    ws.write(dr + 1 + i, 0, str(r["日期"]), self.f_text)
                for j, c in enumerate(day_cats):
                    ws.write_number(dr + 1 + i, 1 + j, float(r[c]), self.f_num)

            n_day = len(daily)
            tcol = 1 + day_cats.index("当日合计") if "当日合计" in day_cats else 1
            ch3 = self.book.add_chart({"type": "line"})
            ch3.add_series({
                "name": "每日采购额",
                "categories": ["图表", dr + 1, 0, dr + n_day, 0],
                "values": ["图表", dr + 1, tcol, dr + n_day, tcol],
                "marker": {"type": "circle", "size": 5},
                "line": {"color": "#CC0000", "width": 2.0},
            })
            ch3.set_title({"name": "本月每日采购额趋势（全园合计）"})
            ch3.set_legend({"none": True})
            ch3.set_y_axis({"num_format": "#,##0"})
            ch3.set_size({"width": 460, "height": 280})
            # 饼图少于两张时，折线挪到右上，别留空位
            ws.insert_chart(3 if len(pie_blocks) <= 1 else 19, 10, ch3)

        if not pie_blocks and not n_hist and len(daily) < 2:
            ws.write(3, 1, "没有足够的数据生成图表。", self.f_text)
        return ws

    def close(self):
        self.writer.close()


def build_report(sheets, mapping: pd.DataFrame, config: dict, source_name: str,
                 out_path: Path, keep_history: bool = True):
    categories = list(config["categories"])
    writer = Writer(out_path, source_name, config.get("colors"))

    per_sheet_totals = {}
    pivots = {}
    all_pending = []

    for sheet in sheets:
        df = attach_category(sheet.df, mapping)
        agg = aggregate_items(df, categories)
        agg["类别"] = agg["类别"].fillna("待定")
        total = float(agg["总金额"].sum())

        writer.write_items(f"{sheet.name}汇总", agg, categories, total)

        pivot = build_date_pivot(df, categories)
        pivots[sheet.name] = pivot
        writer.write_dates(f"{sheet.name}日期", pivot, categories)

        per_sheet_totals[sheet.name] = agg.groupby("类别")["总金额"].sum()

        pending = agg[(agg["类别"] == "待定") | (agg["类别"].isna())]
        if len(pending):
            all_pending.append(pending)

    # 全园合并总表：跨供应商按品名合并（编号各家不通用，合并时留空）
    if len(sheets) > 1:
        frames = []
        for s in sheets:
            d = attach_category(s.df, mapping)
            d["编号"] = ""
            frames.append(d)
        all_df = pd.concat(frames, ignore_index=True)

        agg_all = aggregate_items(all_df, categories)
        agg_all["类别"] = agg_all["类别"].fillna("待定")
        writer.write_items("全园汇总", agg_all, categories, float(agg_all["总金额"].sum()))
        writer.write_dates("全园日期", build_date_pivot(all_df, categories), categories)

    overview = {name: series for name, series in per_sheet_totals.items()}
    writer.write_overview(overview, categories)

    # 月度台账：先写本月，再读回来画图（同月重跑自动覆盖）
    history = pd.DataFrame()
    if keep_history:
        try:
            month = month_of(sheets)
            update_history(month, per_sheet_totals)
            history = read_history()
        except Exception as exc:
            print(f"（月度台账更新失败，跳过趋势图：{type(exc).__name__}: {exc}）")

    daily = combine_daily(pivots, categories)
    writer.write_charts(per_sheet_totals, categories, daily, history)

    if all_pending:
        writer.write_pending(pd.concat(all_pending, ignore_index=True))

    writer.close()
    return out_path
