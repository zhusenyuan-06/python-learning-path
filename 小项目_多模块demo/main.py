# main.py —— 入口文件
# 职责：只做「组装」，不写具体逻辑
#
# 你可以把这个文件当成整个项目的「总指挥」：
#   它 import 各个模块，调用它们的函数，把结果串起来。

import config
import business
from utils import helpers


def main():
    print("=" * 62)
    print(f"配送单生成器 · {config.园所名称} · {config.配送日期}")
    print("=" * 62)

    # 1. 调业务模块，拿到结果
    配送单 = business.生成配送单()

    if 配送单 is None:
        print("❌ 没有读到菜单数据")
        return

    # 2. 打印结果
    print(f"园所: {配送单['园所']}")
    print(f"日期: {配送单['日期']}")
    print(f"菜单: {配送单['菜单字符串']}")
    print()
    print(f"总价:   {helpers.格式化金额(配送单['总价'])} 元")
    print(f"均价:   {helpers.格式化金额(配送单['均价'])} 元")
    print(f"最高:   {helpers.格式化金额(配送单['最高'])} 元")
    print(f"最低:   {helpers.格式化金额(配送单['最低'])} 元")
    print(f"种类数: {配送单['种类数']}")
    print()

    # 3. 调业务模块的校验
    问题列表 = business.校验(配送单)
    if 问题列表:
        print("⚠️ 需要注意：")
        for 问题 in 问题列表:
            print(f"   - {问题}")
    else:
        print("✅ 校验通过")

    # 4. 用工具模块打个表
    print()
    helpers.表格("原始菜单数据", business.读取菜单())


if __name__ == "__main__":
    main()
