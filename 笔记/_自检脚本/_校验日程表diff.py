# -*- coding: utf-8 -*-
"""日程表逐格 diff 校验器 —— 每次改表前后都跑一遍。

用法：
    python _校验日程表diff.py <改前备份xlsx> <改后xlsx> [预期变化的行号,逗号分隔]

例：
    python _校验日程表diff.py "备份_20261027_1820.xlsx" "当前表.xlsx" 51,52,53,54

输出：
  - 每个 sheet 的差异格清单（标明是否在预期列表内）
  - 关键词完整性复检（周四复习 / LeetCode / 看 JD / 投递 / 📌）
  - 总时长

为什么要有这个：
  openpyxl 改多轮表最容易出的事是「手滑改到别的地方」，
  而且 openpyxl 不报错、不提示，肉眼很难发现。
  逐格 diff 是唯一可靠的验证手段。
"""
import sys
import openpyxl


def diff_sheets(old_path, new_path):
    wo = openpyxl.load_workbook(old_path)
    wn = openpyxl.load_workbook(new_path)
    if wo.sheetnames != wn.sheetnames:
        raise SystemExit("sheet 不一致:\n  旧=%s\n  新=%s" % (wo.sheetnames, wn.sheetnames))

    all_diffs = []
    print("sheet: %s" % " | ".join(wn.sheetnames))
    for name in wn.sheetnames:
        so, sn = wo[name], wn[name]
        mr = max(so.max_row, sn.max_row)
        mc = max(so.max_column, sn.max_column)
        diffs = []
        for r in range(1, mr + 1):
            for c in range(1, mc + 1):
                a, b = so.cell(r, c).value, sn.cell(r, c).value
                if a != b:
                    diffs.append((r, c, a, b))
        all_diffs += [(name, d) for d in diffs]
        print("\n[sheet] %s  %dx%d -> %dx%d  差异 %d 处"
              % (name, so.max_row, so.max_column, sn.max_row, sn.max_column, len(diffs)))
        for r, c, a, b in diffs:
            print("  r%dc%d" % (r, c))
            print("      旧: %s" % str(a)[:95])
            print("      新: %s" % str(b)[:95])
    return wn, all_diffs


def keyword_check(ws):
    blob = "\n".join(str(v) for row in ws.iter_rows(values_only=True)
                      for v in row if v is not None)
    print("\n--- 关键词复检 ---")
    for kw in ["周四", "LeetCode", "看 JD", "投递", "投简历", "📌", "SQL", "Linux"]:
        print("  %-10s : %d 处" % (kw, blob.count(kw)))
    tot = 0
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, 8).value
        if isinstance(v, (int, float)):
            tot += v
    print("  总时长     : %s h" % tot)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    old_path, new_path = sys.argv[1], sys.argv[2]
    expected = set()
    if len(sys.argv) >= 4:
        for part in sys.argv[3].split(","):
            part = part.strip()
            if part:
                expected.add(int(part))

    wn, all_diffs = diff_sheets(old_path, new_path)

    print("\n=== 总结 ===")
    print("总差异格数 :", len(all_diffs))
    if expected:
        # 预期行号针对「每日计划」sheet；若其他 sheet 也有差异则一律判为意外
        got_rows = {d[0] for _, d in all_diffs}
        other = {name for name, _ in all_diffs if name != "每日计划"}
        print("预期行数   :", sorted(expected))
        print("实际行数   :", sorted(got_rows))
        if other:
            print("结论       : !!! 其他 sheet 也有改动 -> %s" % sorted(other))
        elif got_rows == expected:
            print("结论       : ✅ 只改了预期行")
        else:
            print("结论       : !!! 有非预期改动 -> %s" % sorted(got_rows - expected))
            print("           缺失的行 -> %s" % sorted(expected - got_rows))

    keyword_check(wn["每日计划"])


if __name__ == "__main__":
    main()
