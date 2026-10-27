# -*- coding: utf-8 -*-
"""按证据更新《AI应用工程师技能清单.xlsx》状态列。

原则
----
1. 只填有硬证据支撑的状态，没证据的一律保持「未开始」——这张表是用来求职的，虚标会在面试被戳穿。
2. 每一格都在 E 列（说明/对照）追加「📌 状态依据」，标明凭什么这么填，方便逐条核对和推翻。
3. 不动表格结构：5 列不变，auto_filter(A1:E37) 不变，D 列数据验证 D2:D37 不变。

用法： python _更新技能清单状态.py
"""
import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师技能清单.xlsx"

# 行号 -> (新状态, 依据)
# 状态只允许三个值（和 D 列下拉一致）：未开始 / 进行中 / 已完成
UPDATES = {
    # —— 一、地基硬技能 ——
    2:  ("进行中", "6 周 / 38 个 .py / 2798 行；函数·字典·列表·推导式·文件读写·JSON 已过；"
                  "pandas 在 11-16 才学，算法题未开刷 → 熟练还差一截"),
    3:  ("进行中", "天天在用：Claude Code 陪练 + code review + CLAUDE.md；"
                  "但 subagent / 评测闭环 还没系统练过 → 不能写「精通」"),
    4:  ("未开始", "无 Java/Go 任何痕迹，如实留空"),
    5:  ("进行中", "10.20练习.py 末尾 258 行笔记含容器对照/推导式/选型三问/9 条踩坑；"
                  "但 23 次 LeetCode 槽位还没开始刷 → 笔试项仍需补"),

    # —— 二、AI 应用核心技术 ——
    6:  ("进行中", "日常写提示词已在做；但 system prompt / few-shot / CoT / 输出约束 没系统学 → 进行中"),
    7:  ("进行中", "RAG 技术方案已完成 13 章（chunking/Embedding/向量检索/rerank/幻觉处理 都有设计）；"
                  "代码未实现 → 「会设计」不是「会做」"),
    8:  ("未开始", "无多步骤编排/工具调用代码，如实留空"),
    9:  ("未开始", "未系统写过 Function Calling / MCP server，如实留空"),
    10: ("未开始", "无长文本/多轮对话管理实践，如实留空"),

    # —— 三、工程化与部署 ——
    11: ("未开始", "Milvus/pgvector/Qdrant/FAISS 均未接触"),
    12: ("未开始", "LangChain / LlamaIndex 未开始"),
    13: ("未开始", "FastAPI 未开始（11 月第 2 周才排 requests）"),
    14: ("进行中", "Ollama 0.34.4 本地已装 + deepseek-r1:8b 已跑通（本地部署这一半有了）；"
                  "Docker / K8s / vLLM 空白 → 只能算进行中"),
    15: ("未开始", "并发/延迟/token 成本/缓存/降级 无实践；硅基流动中转遇到限流但未系统处理过"),
    16: ("未开始", "Dify / Coze 未接触"),

    # —— 四、模型与选型判断 ——
    17: ("进行中", "RAG 技术方案里已写了选型理由（为什么不上 SFT）；"
                  "但 4 种范式横向对比还没背熟 → 面试必问项，仍需补"),
    18: ("进行中", "3 份技术方案 docx 都在讲「为什么这么选」；"
                  "幼儿园菜项目做过真实取舍（yaml 配置驱动 vs 硬编码、多供应商格式容错）→ 能讲出理由，但缺系统化"),
    19: ("进行中", "实际调用过 MiniMax-M2.5 / Kimi-K2.6 / DeepSeek-V3.2 / deepseek-r1:8b；"
                  "SiliconFlow 云端 + Ollama 本地双通道在跑 → 有手感，但没系统对比过特点"),
    20: ("进行中", "自建了 2 个评测/追踪闭环：错题追踪器（occurrences + streak 退场机制）"
                  "+ 工具链坑追踪器（hits 排序）；MLP 实验做了混淆矩阵/优化器对比/正则化对比 → 有意识，缺系统"),

    # —— 五、数据与周边 ——
    21: ("未开始", "SQL 排在 11-16~11-19，尚未开始（教材已就位）"),
    22: ("进行中", "pandas 已实际用于 CSV/Excel 处理（幼儿园菜项目主力就是 pandas）；"
                  "PyPDF2/pdfplumber 排在 11-17 → 文档解析这半还没做"),
    23: ("未开始", "Linux 排在 11-24~11-25，尚未开始（WSL 也没装）"),

    # —— 六、软技能 ——
    24: ("已完成", "已有"),
    25: ("已完成", "已有，差异化加分项"),
    26: ("进行中", "3 份技术方案 docx + 幼儿园菜架构决策，都是「讲清楚为什么这么选」的实例；"
                  "但没练过口述表达"),
    27: ("进行中", "方案文档已写 3 份（RAG 13 章 + 麻醉 2 份）；技术博客一篇未发 → JD 要的「博客」还空着"),
    28: ("未开始", "无跨团队协作证据，如实留空"),

    # —— 七、求职信号 ——
    29: ("进行中", "仓库已上线 github.com/zhusenyuan-06/python-learning-path：59 文件 / 12 commit / 真名作者 / "
                  "README 含目录·作品表·踩坑精选；但 MLP 实验和幼儿园菜还没推上去，⭐ 高星/突出贡献尚不成立"),
    30: ("未开始", "技术博客一篇未发"),
    31: ("进行中", "已有 3 个可讲的项目：① 幼儿园菜汇总（已交付园方）② MLP_MNIST 实验（6 图+报告）"
                  "③ RAG 机器人（仅方案）。⚠️ 但都是「传统 Python」或「仅方案」，"
                  "严格意义的 AI 应用成品还没有 → 这是当前最大缺口"),
    32: ("未开始", "无竞赛 / 开源 PR / Hackathon 记录，如实留空"),
    33: ("未开始", "尚未进入面试准备阶段"),

    # —— 八、不用深钻 ——
    34: ("未开始", "明确不深钻（符合预期，不是缺陷）"),
    35: ("未开始", "明确不深钻（符合预期，不是缺陷）"),
    36: ("未开始", "明确不深钻（符合预期，不是缺陷）"),
    37: ("已完成", "目标明确：AI 应用工程师，明确排除基层开发岗；"
                  "且已有真实交付项目证明走的是应用路线"),
}

MARK = "📌 状态依据（2026-10-27 按证据更新）："


def main():
    wb = openpyxl.load_workbook(PATH)
    ws = wb["技能清单"]

    allowed = {"未开始", "进行中", "已完成"}
    changed = []
    for r, (status, reason) in sorted(UPDATES.items()):
        cell = ws.cell(r, 4)
        old_status = cell.value
        if old_status not in allowed:
            raise SystemExit("r%d 状态值非法: %r" % (r, old_status))
        if status not in allowed:
            raise SystemExit("r%d 新状态非法: %r" % (r, status))

        cell.value = status
        e = ws.cell(r, 5)
        old_note = e.value or ""
        if MARK not in old_note:
            e.value = ("%s\n%s%s" % (old_note, MARK, reason)).strip()
        changed.append((r, old_status, status))

    # 在「使用说明」sheet 顶部加一行来源说明
    ws2 = wb["使用说明"]
    tip = ("6. 状态列已于 2026-10-27 按「实际证据」批量更新一次（依据写在 E 列，标 📌 开头）；"
           "✅ 标记的软技能 2 项是你原本就填好的。后续自己维护时，"
           "「进行中」必须能说出证据，「已完成」必须能拿出东西。")
    if not any(isinstance(c.value, str) and c.value.startswith("6.") for c in ws2["A"]):
        ws2.insert_rows(7)
        ws2.cell(7, 1).value = tip

    wb.save(PATH)

    print("已更新 %d 行状态" % len(changed))
    for r, o, n in changed:
        flag = "  " if o == n else "->"
        print("  r%-3d %s %s" % (r, flag, n))

    # ---- 回读校验 ----
    wb2 = openpyxl.load_workbook(PATH)
    ws3 = wb2["技能清单"]
    print("\n--- 回读校验 ---")
    bad = 0
    for r, o, n in changed:
        v = ws3.cell(r, 4).value
        if v != n:
            print("  !!! r%d 状态不符: %r" % (r, v))
            bad += 1
    print("状态不一致格数:", bad)

    from collections import Counter
    cnt = Counter(ws3.cell(r, 4).value for r in range(2, ws3.max_row + 1))
    print("\n状态分布:", dict(cnt))
    print("auto_filter:", ws3.auto_filter.ref)
    for dv in ws3.data_validations.dataValidation:
        print("数据验证:", dv.formula1, dv.sqref)
    print("freeze:", ws3.freeze_panes)
    print("dims:", ws3.max_row, "x", ws3.max_column)


if __name__ == "__main__":
    main()
