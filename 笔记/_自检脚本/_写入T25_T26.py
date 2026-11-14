# -*- coding: utf-8 -*-
"""写入工具链坑 T25 / T26（2026-11-14 晚）

T25: PyCharm 正则检查器对中文命名组报红 —— 假警报
T26: 写进交付物的输出和「小技巧」必须实跑验证 —— 一天连错 4 处
"""
import datetime
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "工具链")))
import importlib.util

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

if any(x["id"] == "T25" for x in db["items"]):
    print("⚠️ T25 已存在，跳过")
else:
    db["items"].append({
        "id": "T25",
        "title": "PyCharm 正则检查器对【中文命名组】报红 —— 假警报，Python 本身完全支持",
        "symptom": "在 PyCharm 里写 r\"(?P<年>\\d{4})-(?P<月>\\d{2})-(?P<日>\\d{2})\"，\n"
                   "「年」「月」「日」三个组名正下方出现红色波浪线，鼠标悬停提示组名不合法。\n"
                   "但代码在 PyCharm 里 Run 一遍完全正常，输出 2026 / 11 / 14，没有报错。",
        "cause": "PyCharm 编辑器会对 r\"...\" 字符串做【实时正则检查】（Inspection），\n"
                 "但它内部用的是自己的正则检查器（Java 语法取向），\n"
                 "要求命名组名只能是 ASCII 字母数字，不认中文组名。\n"
                 "而 Python 3 自 PEP 3131 起允许 Unicode 标识符，re 模块完全支持中文组名。\n"
                 "→ 检查器与 CPython 的 re 不一致 = 误报（false positive）。",
        "solutions": [
            "【判定方法】别猜，跑一遍就知道：re.search(r\"(?P<年>\\d{4})\", \"2026\").group(\"年\") → 输出 2026，说明 Python 侧完全正常",
            "【方案A】不想看红线就改用数字编号组 (\\d{4})-(\\d{2})-(\\d{2}) + .group(1)（功能完全等价）",
            "【方案B】组名改 ASCII（如 (?P<year>...)）一般就不再标红",
            "【方案C】根治：Settings → Editor → Inspections → 搜 \"Regular expression\" → Severity 改成 \"Do not show\"，以后写任何正则都不再被假警报带偏注意力",
            "【心法】假警报比没有检查更伤 —— 它消耗注意力，还让人怀疑本来正确的代码；看到红线先实跑验证，再决定改不改",
            "【反向提醒】Python 认 (?P<name>...) 但【不认】Java 的 (?<name>...)：后者会报 unknown extension ?<y at position 1，别照着 Java 写法抄",
        ],
        "tags": ["PyCharm", "正则", "误报", "假警报", "命名组", "IDE检查", "检查器"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T25")

if any(x["id"] == "T26" for x in db["items"]):
    print("⚠️ T26 已存在，跳过")
else:
    db["items"].append({
        "id": "T26",
        "title": "写进讲义/练习/注释里的「输出」和「小技巧」必须实跑验证 —— 一天连错 4 处",
        "symptom": "2026-11-14 晚写 re 正则讲义 + 练习答案 + LeetCode 练习，\n"
                   "交付物里连着 4 处是「凭印象写」的，实跑后发现全错：\n"
                   "① 讲义里 finditer 的 span 手抄成 (38 - 38, 38)，实际是 (35, 38)\n"
                   "② 讲义里「compile 后 sub」的输出手抄时漏了「日期是…哦」那半句\n"
                   "③ 练习答案里写「bbb → 3 个空串」，实际是 4 个（空匹配数 = 字符串长度 + 1）\n"
                   "④ LeetCode 练习的加分项正则 r\"^(.+)(?=\\1$)\" 实测直接返回 None，根本不工作\n"
                   "   （贪婪的 (.+) 把整串吃光后没内容留给 \\1；正确写法是 ^(.)(?=.*\\1$)|^.$）",
        "cause": "三个来源叠加：① 手抄输出时凭记忆转写 ② 「听起来对」的技巧没跑 ③ 讲义类交付物写完没有逐段比对实跑结果。\n"
                 "第 ④ 条尤其典型 —— 模式看着专业、逻辑看着通顺，但从来没跑过。",
        "solutions": [
            "【铁律】凡是写进交付物的「输出」「实跑结果」，一律先跑一遍再粘，不许凭记忆转写",
            "【技巧也要验】给用户的「小技巧 / 加分项 / 进阶写法」同样必须实跑 —— 听起来对 ≠ 能跑（今天这条直接给了用户一个跑不通的正则）",
            "【流程】写 → 跑 → 粘 → 再跑一遍交付物（把交付物当程序跑一次，不是只跑代码）",
            "这跟错题 E14「注释里的锚点值要和真实输出对得上」是同一条；今天一天重现 3 次，说明它必须变成固定流程而不是靠自觉",
            "【教学法】讲义里主动写「我今天自己也写错了 N 处，附实跑对照」反而更有教学价值 —— 把自己的坑变成教材，而不是藏起来",
        ],
        "tags": ["实跑验证", "讲义", "注释", "交付物", "手抄错误", "E14", "教学", "正则"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T26")

gzk.save(db)
print("✅ 已保存并 render")
