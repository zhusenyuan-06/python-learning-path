# -*- coding: utf-8 -*-
"""更新技能清单 r31「2–3 个完整 AI 应用作品集」的依据（项目盘点后内容有变）。

同时把技能清单本身纳入 git 仓库做保险层（2026-10-27 桌面主文件曾整份消失）。
用法： python _更新技能清单作品集行.py
"""
import os
import shutil
import subprocess
import sys

DESKTOP = r"C:\Users\15816\Desktop\AI应用工程师技能清单.xlsx"
AUTHORITY = r"D:\AI应用工程师\09-求职资产\AI应用工程师技能清单.xlsx"
REPO_COPY = r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\求职资产快照\AI应用工程师技能清单.xlsx"

NEW_NOTE = (
    "已有 4 个可讲的项目："
    "① 幼儿园菜汇总（已交付园方，1843 行 / 7 模块）"
    "② MLP_MNIST 实验（手写 MLP，11 张图 + 报告）"
    "③ 课程问答 RAG 机器人（13 章方案 + 四层骨架 ingest/retrieve/generate/api）"
    "④ 麻醉会诊辅助决策（11 章方案，含依据溯源与隐私合规设计）"
    "⚠️ 但 ③④ 都还没跑起来（0 行可运行代码），严格意义的「AI 应用成品」仍然没有 "
    "→ 这是当前最大缺口。已评估：麻醉会诊做 7 步 MVP 只需 2~3 天（零件已有 70%）。"
)

import openpyxl


def patch(path):
    wb = openpyxl.load_workbook(path)
    ws = wb["技能清单"]
    old = ws.cell(31, 5).value
    if NEW_NOTE in str(old):
        print("  已是最新，跳过:", os.path.basename(path))
        return False
    ws.cell(31, 5).value = NEW_NOTE
    wb.save(path)
    print("  已更新 r31:", os.path.basename(path))
    return True


if __name__ == "__main__":
    print("=== 更新各副本 ===")
    for p in (DESKTOP, AUTHORITY, REPO_COPY):
        if os.path.exists(p):
            patch(p)
        else:
            print("  不存在，跳过:", p)

    # 从桌面同步到权威副本与仓库快照（桌面是工作副本）
    print("\n=== 同步副本 ===")
    os.makedirs(os.path.dirname(REPO_COPY), exist_ok=True)
    shutil.copy2(DESKTOP, AUTHORITY)
    shutil.copy2(DESKTOP, REPO_COPY)
    for p in (DESKTOP, AUTHORITY, REPO_COPY):
        print("  %-58s %6d 字节" % (os.path.basename(p), os.path.getsize(p)))

    # 校验三份一致
    print("\n=== 一致性校验 ===")
    sigs = set()
    for p in (DESKTOP, AUTHORITY, REPO_COPY):
        wb = openpyxl.load_workbook(p)
        ws = wb["技能清单"]
        sig = (ws.cell(31, 4).value, ws.cell(31, 5).value,
               tuple(ws.cell(r, 4).value for r in range(2, 38)))
        sigs.add(sig)
        print("  %-58s r31=%s" % (os.path.basename(p), ws.cell(31, 4).value))
    print("  三份完全一致:", "是 ✅" if len(sigs) == 1 else "否 ❌")
