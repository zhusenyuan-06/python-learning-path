"""清理今天产生的多余文件。

删除方式说明（为什么不是 rm）：
  桌面属于个人目录，永久删除不可逆。
  本沙箱里「送回收站」的 COM 接口被安全策略拦截（见 MEMORY.md），
  所以采用【同盘移动】到临时回收目录 —— C 盘 → C 盘 是重命名，秒级且可逆。
  万一我判断错了，用户去 %TEMP%\\_workbuddy_trash_20261029_1936\\ 就能捞回来。

删的：
  ① 坏的旧版 bat（v1 / v2）—— 留着只会误导，双击还会报错
  ② 5 个内容完全相同的 hosts 备份（md5 全是 88ef1d862764）—— 留 1 个当保险
  ③ 我今天在 %TEMP% 建的测试残留（diag py / 副本临时目录）

留的：
  - gh_hosts_fix.py + 修复GitHub访问_v3.bat  ← 待会儿要用
  - 1 个最新的 hosts 备份（保险，万一 v3 写坏 hosts 能还原）
  - 仓库里的 _诊断bat_echo缩进.py（诊断证据，是教学材料不是垃圾）
"""
import os
import shutil
import time
from pathlib import Path

DESKTOP = Path(r"C:\Users\15816\Desktop")
TEMP = Path(os.environ["TEMP"])
TRASH = TEMP / "_workbuddy_trash_20261029_1936"

# ---- 要移走的文件（桌面）----
TO_MOVE = [
    # 坏掉的旧版 bat
    "修复GitHub访问.bat",          # v1：4 个域名绑同一 IP，违反 T17
    "修复GitHub访问_v2.bat",       # v2：bat 里拼 Python，> 吃掉代码行，今晚报错
    # 5 个重复备份（保留 hosts_backup_20261029_193435.bak 这个最新的）
    "hosts_backup_140.82.113.3.bak",
    "hosts_backup_20261029_1845.bak",
    "hosts_backup_20261029_5729.bak",
    "hosts_backup_20261029_192528.bak",
    "hosts_backup_20261029_193145.bak",
]

# ---- 要移走的测试残留（%TEMP%）----
TEMP_JUNK = [
    "gh_diag.py",          # 诊断 bat 生成的临时 py
    "gh_fix2.py",          # v2 bat 留下的残骸
    "tmp2pgsg43v",        # 我建的 hosts 副本测试目录
    "tmpiitmctmg",        # diag bat 的临时目录
    "tmpu86ofga8",        # 第二次副本测试目录
]


def move_to_trash(path, label):
    """把文件/目录移到回收目录。返回 (成功, 说明)。"""
    try:
        TRASH.mkdir(parents=True, exist_ok=True)
        dest = TRASH / path.name
        # 同名冲突时加时间戳
        if dest.exists():
            dest = TRASH / ("%s_%d" % (path.name, int(time.time())))
        shutil.move(str(path), str(dest))
        return True, "已移到回收目录：%s" % dest
    except Exception as e:
        return False, "失败：%s" % e


def main():
    print("回收目录：%s\n" % TRASH)
    print("=== 移动桌面文件 ===")
    for name in TO_MOVE:
        p = DESKTOP / name
        if not p.exists():
            print("  [跳过] 不存在：%s" % name)
            continue
        ok, msg = move_to_trash(p, name)
        print("  [%s] %-38s %s" % ("OK" if ok else "[X]", name, msg))

    print("\n=== 移动临时目录残留 ===")
    for name in TEMP_JUNK:
        p = TEMP / name
        if not p.exists():
            print("  [跳过] 不存在：%s" % name)
            continue
        ok, msg = move_to_trash(p, name)
        print("  [%s] %-38s %s" % ("OK" if ok else "[X]", name, msg))

    print("\n=== 桌面现状（应只剩 3 个）===")
    for f in sorted(DESKTOP.iterdir()):
        n = f.name
        if "hosts" in n or "github" in n.lower() or n.startswith("gh_") or "修复" in n:
            print("    %-42s %8d bytes" % (n, f.stat().st_size))


if __name__ == "__main__":
    main()
