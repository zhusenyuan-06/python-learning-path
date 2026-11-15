# -*- coding: utf-8 -*-
"""写入工具链坑 T34 / T35（2026-11-15 16:00，批改 E02/E35 重练时踩的）

T34: 同一文件里【同名函数定义多次】→ 后面的会【静默覆盖】前面的。
     用户写好的代码被空壳函数吃掉，自动检查跑的是空壳 —— 显示 None，看不出真相。

T35: f-string 里直接写【字典/列表字面量】→ 花括号被当表达式解析 → 报错或静默错。
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
        "id": "T34",
        "title": "同一文件里同名函数定义多次 → 后面的静默覆盖前面的，用户写的代码被空壳吃掉",
        "symptom": "2026-11-15 15:50 批改 E02/E35 重练文件：\n"
                   "文件里同时存在三处 `def 统计词频` / `def 找最大` / `def 是不是全零`：\n"
                   "  ① 题干区（故意写错的版本）\n"
                   "  ② 用户作答区（用户 15:49 亲手写的正确尝试）\n"
                   "  ③ 「代码作答区」的空壳 `return None`（当初给用户留的骨架）\n"
                   "Python 里同名定义【后者覆盖前者】→ 自动检查调用的是第 ③ 处。\n"
                   "结果：用户明明写了代码，检查却显示 `你的答案 = None`。\n"
                   "→ 差点误判成「用户一题没写 / 没保存」。",
        "cause": "重构文件时【新增了一段】，但没检查旧段里是否已有同名定义。\n"
                 "Python 的 def 是【执行即生效、后来居上】，不报错、不警告。\n"
                 "→ 凡是文件里 def 同名函数，必须先 grep 一遍全名再决定叫什么",
        "solutions": [
            "【铁律】同一个 .py 文件里，同一个函数名【只能定义一次】。"
            "要留「题干版 / 用户版 / 参考版」就必须改函数名加后缀："
            "`统计词频_题目版本` / `统计词频_第一版` / `统计词频`（重做区）",
            "【检查手法】重构后必跑："
            "`grep -n '^def ' 文件.py | awk '{print $2}' | sort | uniq -d`"
            "→ 有输出 = 有重名 = 必查",
            "【检查手法 2】批改用户的练习时，**把用户写的函数单独抽出来跑一遍** —— "
            "不要相信文件里的自动检查结果，它可能跑的根本不是你写的那个函数",
            "【已修】本题文件已重构成四段，函数名全部加后缀区分；"
            "用户的原答案另存为 `11.15练习_E02_E35重练.py.bak-20261115_你的作答版`",
            "【通用】任何「题干 + 作答 + 参考答案」共处一文件的练习都适用",
        ],
        "tags": ["Python", "函数覆盖", "同名def", "练习文件", "交付物", "T33", "教学"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
    {
        "id": "T35",
        "title": "f-string 里写【字典/列表字面量】→ 花括号被当表达式解析",
        "symptom": "2026-11-15 16:00 自动检查里写：\n"
                   "    print(f\"... 重做 3（反例 {'a':0,'b':3}）...\")\n"
                   "实跑直接崩：\n"
                   "    ValueError: Invalid format specifier '0,'b':3' for object of type 'str'\n"
                   "（f-string 看到第一个 { 就去求值 'a':0,'b':3 → 当成格式说明符）",
        "cause": "f-string 的 {} 是【表达式占位符】，不是字面量的花括号。\n"
                 "想在 f-string 里显示字典/集合字面量，必须写成 {{ 和 }}（双写转义）。",
        "solutions": [
            "【正解】f-string 里要显示字面量花括号 → 双写：`{{'a':0,'b':3}}`",
            "【更省事】字面量先存变量再插：`反例 = {'a':0,'b':3}` 然后 f\"...{反例}...\"",
            "【最省事】干脆不用 f-string：`print(\"...\", 反例)`",
            "【排查法】报 Invalid format specifier → 十有八九是 f-string 里塞了字面量花括号",
        ],
        "tags": ["Python", "f-string", "格式化", "花括号", "ValueError", "教学"],
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
