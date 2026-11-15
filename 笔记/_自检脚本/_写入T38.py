# -*- coding: utf-8 -*-
"""写入工具链坑 T38（2026-11-15 17:35，独立批改 pandas 练习时踩的）

T38: 用「独立脚本」验用户代码时，【判据自己也会错】——
     跨工具比较时类型推断不一致（pandas 自动推断成 int，标准库 csv 一律给字符串），
     导致两边数据明明一样却不相等 → 误判成「用户写错了」。
"""
import datetime
import os
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

新增 = [
    {
        "id": "T38",
        "title": "独立验证脚本的判据自己也会错：跨工具比较时类型推断不一致 → 误判成「用户写错了」",
        "symptom": "2026-11-15 17:30 批改 pandas 练习：8 题文件里的自动检查全绿，\n"
                   "但我不放心（期望值是我自己写的，万一写错了检查也跟着错），\n"
                   "于是另写一个【独立批改脚本】：用标准库 csv 重算「真相」，跟 pandas 比。\n"
                   "结果任务3 报 ❌：\n"
                   "    你的 = 序号 1, 2, 3          ← 整数（pandas 自动推断的结果）\n"
                   "    期望 = ['1', '2', '3']      ← 字符串（标准库 csv 一律返回字符串）\n"
                   "两边打印出来【肉眼完全一样】，但 '1' == 1 → False → 判错。\n"
                   "→ 差一步就冤枉用户「任务3 写错了」，而他的代码其实完全正确。",
        "cause": "跨【两个不同工具】比较数据时，默认「两边类型一样」，从没验证过。\n"
                 "标准库 csv.reader 是【纯文本读取器】，一个数字都不帮你转；\n"
                 "pandas read_csv 默认会【自动类型推断】：'1' → int64。\n"
                 "→ 同一个 CSV，两个工具读出来的「同一列」类型就是不一样。",
        "solutions": [
            "【正解】判据里统一转型再比：\n"
            "    [str(x) for x in 你的列] == [str(x) for x in 期望列]",
            "【判据自检】独立验证脚本跑出 ❌ 时的第一反应应该是\n"
            "  「是用户错，还是我判据错？」而不是直接甩结论给用户。\n"
            "  判据错的表现特征：【两边 print 出来肉眼一样，但不相等】\n"
            "  → 几乎必然是类型 / 精度 / 空格 / 换行符 之类的差异。",
            "【打印 repr】怀疑时把两边都 `%r` 打出来（带引号和转义），\n"
            "  肉眼看不出差别时 repr 能看出来：'1' vs 1、'1\\n' vs '1'。",
            "【pandas 侧的知识点】pandas 的自动类型推断是个【双刃剑】：\n"
            "  · 好：数字列直接是 int64，能直接算\n"
            "  · 坏：'007' 会被读成 7（前导零没了）、'0001-01-01' 变字符串、TLE 号变 float\n"
            "  → 要原样保留文本：read_csv(..., dtype={'列名': str})",
            "【适用】所有「用 A 工具的结果验 B 工具的结果」的独立验证脚本：\n"
            "pandas vs csv、pandas vs openpyxl、JSON vs CSV …… 都栽在同一类差异上。",
        ],
        "tags": ["Python", "pandas", "验证", "判据", "类型推断", "误判", "教学"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
]

for 条目 in 新增:
    if any(x["id"] == 条目["id"] for x in db["items"]):
        print("⚠️ %s 已存在，跳过" % 条目["id"])
    else:
        db["items"].append(条目)
        print("✅ 已写入 %s" % 条目["id"])

gzk.save(db)
print("✅ 已保存并 render")
