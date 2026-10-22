def add_task(tasks, text):
    """把一条任务（dict）加到 tasks 列表，返回新列表"""
    tasks.append({"text": text, "done": False})
    return tasks


def list_tasks(tasks):
    """打印所有任务；空列表提示'暂无任务'"""
    if not tasks:
        print("暂无任务")
        return
    for i, t in enumerate(tasks, 1):
        status = "已完成" if t["done"] else "未完成"
        print(f"{i}. {t['text']} [{status}]")



# 新增：第 3 个函数（在 add_task 下面加）
def mark_done(tasks, n):
    """把第 n 条任务标记为已完成（n 从 1 开始计）"""
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"

    tasks[n - 1]["done"] = True
    # ← 核心一行：把第 n 条标成已完成
    return tasks


# 修改：run_cli 里的 elif 链，加一条
def run_cli():
    tasks = []
    print("=== 极简待办工具 ===")
    print("命令：add <任务> / list / done <编号> / quit")

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue

        if cmd == "quit":
            print("再见！")
            break
        elif cmd == "list":
            list_tasks(tasks)
        elif cmd.startswith("add "):
            text = cmd[4:]
            add_task(tasks, text)
            print(f"已添加：{text}")
        elif cmd.startswith("done "):
            n = int(cmd[5:])  # 解析 "done 1" 拿 "1" 再转 int
            mark_done(tasks, n)
            # ← 解析 "done 1" 拿 n，调 mark_done
            print(f"已完成第 {n} 条")
        else:
            print("未知命令，输入 add / list / done / quit")


# 启动
run_cli()
