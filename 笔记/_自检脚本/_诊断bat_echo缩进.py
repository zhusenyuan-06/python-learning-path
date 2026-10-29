"""诊断：bat 里用 `>> file echo <python代码>` 拼出来的 Python 文件到底长什么样。

为什么不猜：
  报错说临时文件第 25 行 `nm = parts[1].lower()` 缩进不对，
  但按 bat 的行号推算它应该在第 26 行 —— 差了一行，说明提取过程
  悄悄改动了内容。到底改成什么样，必须让 cmd.exe 真跑一遍才知道。

做法：
  1) 造一个 diag bat，把原 bat 的 echo 序列原样复制过来，
     但【只生成 py，不执行、不碰 hosts】
  2) 真跑一遍 cmd.exe
  3) 读出生成的 py，逐行打印行号 + repr（repr 能看清到底有几个空格）

为什么用 Python 生成 bat：
  bat 必须是 CRLF 换行，Write 工具默认写 LF —— LF 的 bat 会静默失败。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

# 原 bat 里 echo 序列的原样复制（bat 第 66~111 行）
ECHO_LINES = [
    "import sys, io",
    "hosts = sys.argv[1]",
    "webip = sys.argv[2]",
    "apiip = sys.argv[3]",
    "WEB = ['github.com','codeload.github.com','objects.githubusercontent.com','github.githubassets.com']",
    "API = ['api.github.com']",
    "try:",
    "    with io.open(hosts, 'r', encoding='utf-8', errors='replace') as f:",
    "        lines = f.read().splitlines()",
    "except Exception:",
    "    with io.open(hosts, 'r', encoding='mbcs', errors='replace') as f:",
    "        lines = f.read().splitlines()",
    "kept = []",
    "for line in lines:",
    "    s = line.strip()",
    "    if not s:",
    "        kept.append(line); continue",
    "    if s.startswith('#'):",
    "        if 'GitHub fix start' in s or 'GitHub fix end' in s:",
    "            continue",
    "        if 'Main site' in s or 'Static asset CDN' in s or 'API endpoint' in s:",
    "            continue",
    "        kept.append(line); continue",
    "    parts = s.split()",
    "    if len(parts) >= 2:",
    "        nm = parts[1].lower()",
    "        if nm in WEB or nm in API:",
    "            continue",
    "    kept.append(line)",
]


def build_bat(tmp_dir):
    """生成 diag bat（CRLF）。"""
    bat = tmp_dir / "diag_echo.bat"
    lines = ["@echo off", "chcp 65001 >nul", 'set "TMPS=%TEMP%\\gh_diag.py"', 'del "%TMPS%" >nul 2>&1']
    for i, code in enumerate(ECHO_LINES):
        op = ">" if i == 0 else ">>"
        # 关键：这里复刻原 bat 的写法 —— echo 后面紧跟 python 代码
        lines.append(f'{op} "%TMPS%" echo {code}')
    lines.append('echo GENERATED: %TMPS%')
    lines.append("exit /b 0")
    # 关键：CRLF。bat 用 LF 会静默失败（一闪而过，什么都不执行）
    bat.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return bat


def main():
    tmp_dir = Path(tempfile.mkdtemp())
    bat = build_bat(tmp_dir)
    print(f"bat 已生成：{bat}")

    # 真跑 cmd.exe
    r = subprocess.run(["cmd.exe", "/c", str(bat)], capture_output=True, text=True)
    print(f"cmd 退出码：{r.returncode}")
    if r.stdout.strip():
        print("stdout:", r.stdout.strip())

    gen = Path(tempfile.gettempdir()) / "gh_diag.py"
    if not gen.exists():
        print("❌ 临时 py 没生成")
        return 1

    content = gen.read_bytes()
    print(f"\n生成文件大小：{len(content)} 字节")
    print("CRLF 行数：", content.count(b"\r\n"), " 裸 LF 数：", content.count(b"\n") - content.count(b"\r\n"))

    print("\n=== 逐行对比（期望缩进 vs 实际缩进）===")
    actual = content.decode("utf-8", "replace").splitlines()
    bad = 0
    for i, (exp, act) in enumerate(zip(ECHO_LINES, actual), 1):
        exp_ind = len(exp) - len(exp.lstrip(" "))
        act_ind = len(act) - len(act.lstrip(" "))
        flag = ""
        if exp != act:
            flag = f"  <<<< 不一致！期望{exp_ind}格 实际{act_ind}格"
            bad += 1
        print(f"{i:3d} | 期望{exp_ind:2d} | 实际{act_ind:2d} | {act}{flag}")

    if len(actual) != len(ECHO_LINES):
        print(f"\n❌ 行数不对：期望 {len(ECHO_LINES)} 行，实际 {len(actual)} 行")

    print(f"\n不一致的行数：{bad}")
    if bad:
        print(">>> 根因确认：cmd 的 echo 对【带空格开头的参数】做了处理")

    # 顺便看 Python 报什么错
    print("\n=== 让 Python 试着读它 ===")
    r2 = subprocess.run([r"D:\AAAA\python.exe", "-c",
                         f"import ast,io;src=io.open(r'{gen}',encoding='utf-8').read();"
                         f"print(repr(src.splitlines()[24]));ast.parse(src)"],
                        capture_output=True, text=True)
    print("stdout:", r2.stdout.strip())
    if r2.stderr.strip():
        print("stderr:", r2.stderr.strip())


if __name__ == "__main__":
    sys.exit(main())
