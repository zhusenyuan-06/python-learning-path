# 模块与导入_3问答案.py
# 3 问的答案 + 解析 + 对应代码位置
# 每个答案都标了「去看哪个文件的哪一行」

print("=" * 60)
print("Q1. main.py 为什么写 if __name__ == \"__main__\": ? 不写会怎样？")
print("=" * 60)
print("""
【答案】
__name__ 是每个 Python 文件自带的内置变量：
  - 直接运行这个文件      → __name__ == "__main__"
  - 被别的文件 import 进来 → __name__ == "这个文件自己的名字"

所以 if __name__ == "__main__": 的作用是：
  「只有当我被【直接运行】的时候，才执行下面这段」

【不写会怎样】
main() 会在【两种情况下都执行】：
  1. 你直接跑 main.py       → 执行（这是你想要的）
  2. 别的文件 import main   → 也执行（这是你不想要的！）
     → 别人只想 import 你的某个函数，结果把你整个程序都跑了一遍

【真实项目里的例子】
main.py 里写了 main()，如果 main.py 被 import，
别的文件一 import 就把你整个流程触发了 —— 非常难查的 bug。

【去看代码】
小项目_多模块demo/main.py 第 50-51 行：
""")
print("""    if __name__ == "__main__":
        main()
""")

print("=" * 60)
print("Q2. 为什么 business.py 要 import config / helpers？写一个文件里不行吗？")
print("=" * 60)
print("""
【答案】
行，能跑，但项目一大就废。理由有 3 个：

1. 【职责单一】
   config.py 只放常量，business.py 只放业务逻辑，helpers.py 只放工具函数。
   一个文件里塞 500 行，你要找「最低起送金额」得 Ctrl+F 半天。
   拆开后：一眼知道在哪。

2. 【复用】
   helpers.py 里的 格式化金额 / 读csv / 统计 / 表格 跟业务无关，
   幼儿园菜项目也能直接拿去用。写在一个文件里？别的项目根本用不了。

3. 【改动隔离】
   改一个参数（今天你刚体验过）只动 config.py 一个文件，
   其余 4 个文件一行都不用改，也不会被改坏。

【去看代码】
小项目_多模块demo/business.py 第 5-6 行：
""")
print("""    import config
    from utils import helpers
""")
print("""小项目_多模块demo/main.py 第 8-10 行：
""")
print("""    import config
    import business
    from utils import helpers
""")
print("""    → main.py 自己也要 import config 和 helpers
      因为每个文件都有自己独立的命名空间（今晚第 2 站学的）
""")

print("=" * 60)
print("Q3. ⭐ helpers.py 里的函数完全不提「配送单」，为什么这么设计？")
print("=" * 60)
print("""
【答案】
因为 helpers 是【通用工具层】，不是【配送单专用层】。

【核心原因：可复用】
假设 helpers.py 里写的是业务专用函数：
    def 生成配送单标题(园所名): ...
    def 算配送单总价(菜单): ...
那它就【只能被配送单项目用】。
而写成通用的：
    def 格式化金额(数字): ...
    def 统计(数字列表): ...
    def 表格(标题, 行列表): ...
那：
  - 幼儿园菜项目（也是汇总菜谱）→ 直接 import 就能用
  - 你的 RAG 机器人项目 → 统计 token 数量也能用
  - 通讯录项目 → 打印表格也能用

【第二个原因：改起来安全】
helpers.py 只依赖 Python 自带的东西，不依赖任何业务。
所以改它不会「碰坏」别的模块。
反过来，如果 helpers 里引用了 config.园所名称，
那它就跟配送单绑死了 —— 又变回一个大文件。

【面试怎么答】
"我把代码按职责分成三层：入口层只做组装，业务层放业务规则，
 工具层只放跟业务无关的通用函数。这样工具层可以被多个项目复用，
 改动时影响范围可控。"

【去看代码】
小项目_多模块demo/utils/helpers.py —— 全文没有一个「配送」二字：
""")
print("""    def 格式化金额(数字): ...
    def 读csv(路径): ...
    def 写csv(路径, 行列表): ...
    def 统计(数字列表): ...
    def 表格(标题, 行列表): ...
""")
print("""  → 对比 小项目_多模块demo/business.py：
    def 读取菜单(): ...
    def 生成配送单(): ...
    def 校验(配送单): ...
  → 这层就全是业务，依赖 config 的常量
""")

print("=" * 60)
print("⭐ 三层结构的依赖方向")
print("=" * 60)
print("""
    main.py  （入口 · 只组装）
       ↓
    business.py  （业务规则）
       ↓ ↓
    config.py   helpers.py
    （常量）   （通用工具）

  规则：只能【向下】依赖，不能【向上】，更不能【横着】互相依赖
  （横着依赖叫「循环依赖」，import 时会直接报错）
""")
