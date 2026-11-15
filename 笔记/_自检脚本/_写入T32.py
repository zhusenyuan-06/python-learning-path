# -*- coding: utf-8 -*-
"""写入工具链坑 T32（2026-11-15 15:10，清 LeetCode 欠账时踩的）

T32: 实跑 ≠ 验证 —— 用例集本身必须能【反证】解法。
     我实跑了 6 个用例全绿就写进交付物，但那 6 个用例没有一条能揭穿
     「只判首尾相同」的错误解法，等于给错误解法发了通行证。
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

if any(x["id"] == "T32" for x in db["items"]):
    print("⚠️ T32 已存在，跳过")
else:
    db["items"].append({
        "id": "T32",
        "title": "实跑 ≠ 验证 —— 用例集本身必须能反证解法，否则只是给错误解法发了通行证",
        "symptom": "2026-11-14 晚写 LeetCode 125 练习的「一条正则判回文」加分项：\n"
                   "  ① 第一版 r\"^(.+)(?=\\1$)\" 实跑返回 None → 发现不工作\n"
                   "  ② 改成 r\"^(.)(?=.*\\1$)|^.$\"，实跑 6 个用例（aba/abcd/a/aa/abba/ab）全对\n"
                   "  ③ 当成「已实跑验证」写进交付物文件\n"
                   "  ④ 2026-11-15 跑完整 10 用例集，被 'race a car' 逮住：\n"
                   "     清洗后 = 'raceacar'，首尾都是 'r' → 这条正则返回 True\n"
                   "     但 'raceacar' 不是回文（反着读是 'racacer'）→ 判定错误\n"
                   "  ⑤ 这条正则的本质只是判【首字符 == 尾字符】，之前那 6 个用例的首尾关系\n"
                   "     恰好都和答案一致，纯属【蒙对】。",
        "cause": "把「我跑过了」当成了「我验证过了」。\n"
                 "  实跑只证明【代码按我写的逻辑执行】；\n"
                 "  验证要证明【这份用例集有能力揭穿错误解法】。\n"
                 "那 6 个用例：aba/abba/abcba 都是真回文，abcd 首尾不同，a/aa 是单字符特判 ——\n"
                 "  唯独缺一条【首尾相同但中间不对称】的样本（比如 raceacar），\n"
                 "  而那正是唯一能区分「真回文判定」和「首尾检查」的样本。\n"
                 "→ **用例集有盲区时，跑绿 = 蒙对**。",
        "solutions": [
            "【铁律】写完解法问一句：*「我的用例里，哪一条能证明这个解法【不是】那个错误解法？*」"
            "答不上来 → 用例集不合格",
            "【反例模板】凡是「简化/忽略某些东西」的解法（首尾检查、只查前 3 个、只测偶数长度），"
            "必须专门造一条【能揭穿它】的用例",
            "【已修】练习文件里把这条正则降级成「反面教材」小节，"
            "并补上 4 条对照输出（raceacar ❌ / abba ✅ / abcd ✅ / abcba ✅），"
            "让错误解法留在文件里当教材，而不是删掉",
            "【理论依据】回文语言【不是正则语言】（需要递归才能表达），"
            "标准库 re 不支持递归 → 单正则判完整回文在标准库里【做不到】",
            "【心法】实跑是【必要条件】不是【充分条件】。"
            "绿了就写进交付物之前，先问「有没有反例能揭穿它」",
            "【配套】T26（写进交付物的输出必须实跑）—— T26 管「跑没跑」，T32 管「跑得对不对」",
        ],
        "tags": ["测试用例", "反例", "验证", "交付物", "蒙对", "T26", "正则", "LeetCode", "假绿"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T32")

gzk.save(db)
print("✅ 已保存并 render")
