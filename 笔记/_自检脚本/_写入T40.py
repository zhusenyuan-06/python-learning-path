# -*- coding: utf-8 -*-
"""写入工具链坑 T40（2026-11-17 15:20）

T40: 放在 笔记/_自检脚本/ 下的脚本，路径少退一级 → FileNotFoundError；
     而且同一个坑在【连续两个脚本】里各踩了一次。
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
        "id": "T40",
        "title": "子目录脚本用 parent.parent 定位仓库根 → 少退一级 → FileNotFoundError；同一坑连续踩两次",
        "symptom": "2026-11-17 15:20 铺 11-16 下午档 pandas 练习，连续两个脚本报同一个错：\n"
                   "  ① 笔记/_自检脚本/_生成多天新闻数据.py\n"
                   "     FileNotFoundError: '...\\pythonProject\\笔记\\练习\\数据\\news_示例.csv'\n"
                   "     → 期望是 pythonProject\\练习\\数据\\，实际多了一层「笔记」\n"
                   "  ② 笔记/_自检脚本/_自检_pandas筛选练习.py\n"
                   "     FileNotFoundError: '...\\pythonProject\\笔记\\_自检脚本\\11.17练习_pandas筛选与增删列.py'\n"
                   "     → 期望是 pythonProject\\练习\\，实际少了一层\n"
                   "两个脚本连着栽在同一个地方：脚本在 笔记/_自检脚本/（深两级），\n"
                   "  但 parent.parent 只退到 笔记/，还差一级才到仓库根。",
        "cause": "① 用 parent.parent 硬猜层级，没先数目录深度：\n"
                 "   pythonProject/笔记/_自检脚本/脚本.py  →  脚本所在目录是第 3 层\n"
                 "     .parent        = _自检脚本\n"
                 "     .parent.parent = 笔记            ← 只退到了这里\n"
                 "     .parents[2]    = pythonProject   ← 仓库根在这\n"
                 "  ② 更根本的问题：同一个错误连犯两次，说明是「凭感觉写路径」，\n"
                 "     不是「看一眼目录结构再写」。第一次报错后没把结论固化下来，\n"
                 "     第二个脚本又照抄了同一个错法。",
        "solutions": [
            "【按深度定位，别猜】仓库根 = Path(__file__).resolve().parents[2]\n"
            "  （脚本在 笔记/_自检脚本/ 下时）；练习目录 = parents[2] / '练习'。",
            "【先打印再写】新脚本第一行先 print(Path(__file__).resolve()) 和目标路径 exists()，\n"
            "  确认无误再跑逻辑 —— 别让路径问题混进业务报错里。",
            "【同类脚本抄现成的】已经在 笔记/_自检脚本/ 里跑通过的脚本（如 _给日程表收尾_1115.py\n"
            "  用的是 PATH = r'C:\\Users\\15816\\Desktop\\...' 绝对路径），直接照抄它的路径写法，\n"
            "  不要自己另发明相对层级。",
            "【备份目录好写】D:\\AI应用工程师\\09-求职资产\\ 是固定的归档位，\n"
            "  用绝对路径拼，别从 __file__ 推。",
        ],
        "tags": ["路径", "parent.parent", "FileNotFoundError", "脚本", "层级", "连踩两次"],
        "hits": 2,
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
