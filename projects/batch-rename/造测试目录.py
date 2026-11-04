"""
测试目录生成器 —— 给 batch_rename.py 准备一个安全的练手环境
=============================================================

为什么要单独一个脚本？
    批量改名是【不可逆操作】。拿真文件练手，改错了没法回退。
    所以先在测试目录里造一批假文件，练熟了再碰真的。

⚠️ 测试目录放在【D 盘项目内】，不是系统临时目录（C 盘）。
   原因：
     - C 盘是系统盘，临时目录会被系统清理策略盯上，可能突然消失
     - 用户的真实文件都在 D 盘，测试也在 D 盘，行为一致
     - 放在项目里方便随时查看、随时清

用法：
    python 造测试目录.py          → 造一个测试目录并打印路径
    python 造测试目录.py 清理     → 把测试目录删掉

造出来的文件（故意包含各种边界情况）：
    报告_v1.txt        ← 正常该改的
    报告_final_v1.txt  ← 正常该改的（含旧片段但不在结尾）
    照片.jpg           ← 扩展名不匹配，--ext .txt 时不该被改
    笔记.txt           ← 文件名里没有 _v1，不该被改
    数据_v1.csv        ← 另一个扩展名
    子目录/            ← 目录本身不该被改，里面的文件也不该被改
    子目录/里面的_v1.txt ← 测「不递归」

    _冲突测试/          ← 单独隔开的冲突场景（不影响上面那批正常文件）
        冲突_v1.txt    ← 改名后会撞上 冲突_v2.txt
        冲突_v2.txt
"""

import shutil
from pathlib import Path

# ⚠️ 测试目录的根 = 本脚本所在目录下的 _测试目录
#    Path(__file__).parent = 本脚本所在的文件夹（D 盘项目内）
#    这样不管你从哪个目录运行脚本，测试目录都在同一个地方
测试根 = Path(__file__).parent / "_测试目录"


def 造测试目录():
    """造一个测试目录，返回它的路径。"""
    # 每次都先删掉旧的，保证干净（不然上次残留的文件会干扰测试）
    if 测试根.exists():
        shutil.rmtree(测试根)
    测试根.mkdir(parents=True)

    # ---- 平铺的文件 ----
    # ⚠️ 故意【不】放「报告_v2.txt」—— 放了的话「报告_v1.txt → 报告_v2.txt」
    #    就会撞车，正常的批量改名场景就跑不通了。
    #    冲突场景单独放在下面的 _冲突测试 里。
    for 名 in [
        "报告_v1.txt",        # 该改
        "报告_final_v1.txt",  # 该改（含旧片段但不在结尾）
        "照片.jpg",           # 扩展名不匹配
        "笔记.txt",           # 没有 _v1，不该改
        "数据_v1.csv",        # 另一个扩展名
    ]:
        (测试根 / 名).write_text(f"这是 {名} 的内容\n", encoding="utf-8")

    # ---- 一个子目录，测试「不递归」 ----
    子 = 测试根 / "子目录"
    子.mkdir()
    (子 / "里面的_v1.txt").write_text("子目录里的文件，不该被改\n", encoding="utf-8")

    # ---- 单独的冲突场景：改名后会撞上已存在的文件 ----
    冲突目录 = 测试根 / "_冲突测试"
    冲突目录.mkdir()
    (冲突目录 / "冲突_v1.txt").write_text("改名后会撞上 冲突_v2.txt\n", encoding="utf-8")
    (冲突目录 / "冲突_v2.txt").write_text("目标已存在，改名应该被跳过\n", encoding="utf-8")

    return 测试根


def 清理():
    """删掉测试目录。"""
    if 测试根.exists():
        shutil.rmtree(测试根)
        print(f"✅ 已清理 {测试根}")
    else:
        print(f"测试目录本来就不存在：{测试根}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "清理":
        清理()
    else:
        目录 = 造测试目录()
        print(f"✅ 测试目录已造好：{目录}")
        print()
        print("目录里的内容：")
        for p in sorted(目录.rglob("*")):
            类型 = "目录" if p.is_dir() else "文件"
            print(f"  [{类型}] {p.relative_to(目录)}")
        print()
        print("接下来可以这样试：")
        print(f'  python batch_rename.py "{目录}" _v1 _v2 --ext .txt')
        print(f'  python batch_rename.py "{目录}" _v1 _v2 --ext .txt --apply')
