# business.py —— 业务逻辑模块
# 职责：只放「这个项目特有的业务规则」

import config
from utils import helpers


def 读取菜单():
    """从 config 里指的路径读菜单 csv"""
    return helpers.读csv(config.样例数据文件)


def 生成配送单():
    """生成配送单的核心逻辑：读数据 → 算账 → 拼描述"""
    菜单行 = 读取菜单()

    if not 菜单行:
        return None

    表头 = 菜单行[0]
    数据行 = 菜单行[1:]

    金额列 = 表头.index("金额")
    金额列表 = []
    菜单描述 = []
    for 行 in 数据行:
        菜名 = 行[0]
        重量 = 行[1]
        金额 = float(行[金额列])
        金额列表.append(金额)
        菜单描述.append(f"{菜名}{重量}kg")

    总和, 平均, 最高, 最低, 个数 = helpers.统计(金额列表)

    return {
        "园所": config.园所名称,
        "日期": config.配送日期,
        "菜单": 菜单描述,
        "菜单字符串": ", ".join(菜单描述),
        "总价": 总和,
        "均价": 平均,
        "最高": 最高,
        "最低": 最低,
        "种类数": 个数,
        "达到起送": 总和 >= config.最低起送金额,
    }


def 校验(配送单):
    """业务规则校验：金额太低要警告"""
    if 配送单 is None:
        return ["没有数据，无法生成配送单"]
    问题 = []
    if not 配送单["达到起送"]:
        问题.append(
            f"总价 {helpers.格式化金额(配送单['总价'])} "
            f"低于起送金额 {helpers.格式化金额(config.最低起送金额)}"
        )
    if 配送单["种类数"] < 2:
        问题.append("菜单种类太少，建议至少 2 种")
    return 问题
