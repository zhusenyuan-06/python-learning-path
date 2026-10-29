"""生成 2026-10-29 的周四大复习卷文件。

为什么用脚本而不是命令行内联：
  Markdown 里的 ``` 和 <题号> 会被 bash 吃掉（命令替换 + 重定向），
  写进脚本文件就没有这个问题。
"""
import io
import subprocess
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
PY = r"D:\AAAA\python.exe"
TRACKER = BASE / "错题追踪器.py"

HEAD = """# 周四大复习 · 复习卷 · 2026-10-29（周四）

> 本卷共 6 题，**全部是高频题**（犯过 ≥3 次）。
> 题池现状：28 题在池（今日新登记 5 条 E24-E28），已掌握 1 题，历史累计 23 条 / 40 次。

## 作答规则

1. **先别看答案**。每题只看 ❌ 那段代码，自己说出哪里错、自己改写。
2. 改完再对照 ✅，讲清楚「为什么这样改」。
3. 答完一条记一条：

```
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> pass "你的理解"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> fail "又错在哪"
```

4. 全卷做完后收尾：

```
"D:\\AAAA\\python.exe" 错题追踪器.py render   # 重新生成错题追踪.md
"D:\\AAAA\\python.exe" 错题追踪器.py stats    # 看池子还剩几题
```

> 答错不丢人，答错不记才丢人。今天新增的 E24-E28 都是你今天亲手犯过的，
> 下一周它们会排进卷子 —— 到时候看你是真会了，还是只是这次运气好。

---

"""


def main():
    r = subprocess.run(
        [PY, str(TRACKER), "plan", "6"], capture_output=True, text=True, encoding="utf-8"
    )
    if r.returncode != 0:
        raise SystemExit("plan 失败：" + r.stderr)
    out = BASE / "周四大复习_2026-10-29_复习卷.md"
    out.write_text(HEAD + r.stdout, encoding="utf-8")
    print("已保存：" + str(out))
    print("大小：" + str(out.stat().st_size) + " 字节")


if __name__ == "__main__":
    main()
