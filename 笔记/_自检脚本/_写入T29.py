# -*- coding: utf-8 -*-
"""写入工具链坑 T29（2026-11-14 晚，push 收尾时踩的）

T29: .gitignore 会让「你以为提交了其实根本没进版本控制」—— git status 显示干净，
     但那个文件压根没被 git 跟踪；反过来，临时脚本反而被提交进去了
"""
import datetime
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

if any(x["id"] == "T29" for x in db["items"]):
    print("⚠️ T29 已存在，跳过")
else:
    db["items"].append({
        "id": "T29",
        "title": ".gitignore 会让「你以为提交了其实根本没进版本控制」—— git status 干净 ≠ 文件被跟踪了",
        "symptom": "2026-11-14 20:00 改完 工具/push_github.sh（接入前置自检 + DNS 路回退），\n"
                   "跑 push 脚本后 commit 的输出只有 1 file changed —— push_github.sh 的改动没进去。\n"
                   "git status 显示完全干净，看不出任何异常。\n"
                   "查 git ls-files 才发现：.gitignore 第 27 行写着 push_github.sh，这个文件【从来没被跟踪过】。\n"
                   "反过来，为了应急新建的临时脚本 _push_now.sh 反而被提交进了仓库。",
        "cause": "两个方向都中招：\n"
                 "① 被 ignore 的文件：git add -A 不会捡它，commit 也不会包含它 → 改动只留在本地，\n"
                 "   而且【改坏了没法 git checkout 回滚】（没版本记录），这个风险更隐蔽\n"
                 "② 临时脚本：它不在 ignore 列表里 → 被当成正经作品提交进仓库，污染交付物",
        "solutions": [
            "【查证一条命令】git ls-files 路径 → 没输出 = 这个文件压根没被跟踪（比 git status 靠谱）",
            "【判断改动有没有进去】别只看 commit 的 file count，用 git show --stat <hash> 或 git diff <hash>~1 -- <文件> 逐个点名",
            "【临时脚本处理】应急脚本用完要么删掉、要么加进 .gitignore（别留在仓库里当作品）",
            "【风险提醒】被 ignore 的脚本改了没版本记录 —— 重要脚本要么纳入版本控制（去掉 ignore），要么在别处留备份",
            "【心法】git status 干净只说明「工作区没有未提交改动」，不代表「我改的东西都提交了，也不代表提交的东西都在版本控制里」",
        ],
        "tags": ["git", "gitignore", "提交", "版本控制", "ls-files", "临时脚本", "回滚", "隐蔽坑"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T29")

gzk.save(db)
print("✅ 已保存并 render")
