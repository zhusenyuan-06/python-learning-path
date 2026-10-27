# 标准库1_json_作业答案.py
# 每题都有解析，看代码也要看"为什么"

import json

订单2 = {"菜名": "排骨", "重量": 15.0, "送到": "阳光城"}

print("=" * 56)
print("① 用 dumps 把它变成字符串，存到 变量s")
print("=" * 56)
s = json.dumps(订单2, ensure_ascii=False)
print(s)

print()
print("=" * 56)
print("② 打印 s 的类型")
print("=" * 56)
print(type(s))
print()
print("解析：dumps 的意思是「dump（倒出来）」→ 倒出来的东西一定是字符串。")
print("     所以 dumps 之后从 dict 变成了 str。")
print("     记住这个方向：dumps 是【出】，loads 是【进】。")

print()
print("=" * 56)
print("③ 把 s 变回字典")
print("=" * 56)
字典 = json.loads(s)
print(字典)
print()
print("解析：loads 的意思是「load（装进来）」→ 装进来的是 Python 对象。")
print("     对照记忆：dumps 出、loads 进。")

print()
print("=" * 56)
print('④ 打印 "排骨" 这个值（字典取值用 ["键名"]）')
print("=" * 56)
print(字典["菜名"])
print()
print("解析：字典取值就是 字典[\"键名\"]。")
print("     你今天已经用过很多次了 —— 你的 配送工具.py 里：")
print('         print(键 + \":\", 值)      ← 值就是 附加[\"供应商\"] 这种')
print("     再举一个你熟悉的：汇总配送单(园所名, ...) 里的 园所名 就是普通参数，不用取。")

print()
print("=" * 56)
print("⑤ 如果 订单2 里多一个键 '备注': '不要葱'，dumps 出来会多出什么？")
print("=" * 56)
订单3 = {"菜名": "排骨", "重量": 15.0, "送到": "阳光城", "备注": "不要葱"}
print(json.dumps(订单3, ensure_ascii=False, indent=2))
print()
print("解析：会多出 \"备注\": \"不要葱\" 这一对。")
print("     ⭐ 重点：JSON 转出来之后，【所有的键都是字符串】，用双引号。")
print("     哪怕你的 Python 字典写的是 备注: '不要葱'（单引号），")
print("     转成 JSON 一定变成 \"备注\": \"不要葱\"（双引号）。")
print()
print("     ⭐⭐ 还有一个关键点：【顺序会保留】。")
print("     JSON 对象用的是「有序数组」结构（不是 JS 的无序对象），")
print("     所以你字典里键的顺序，转出来还是一样的。")
print("     这就是你 附加.items() 打印出来的顺序 = 你写参数时的顺序的原因。")

print()
print("=" * 56)
print("⭐ 给你 3 个「以后一定会用到」的 json 场景")
print("=" * 56)
print()
print("场景 1：调 LLM API —— 你要把 prompt 发出去")
请求体 = {
    "model": "MiniMax-M2.5",
    "messages": [{"role": "user", "content": "帮我写配送单"}],
}
print("发给服务器的必须是字符串：")
print(json.dumps(请求体, ensure_ascii=False)[:80], "...")
print()
print("场景 2：模型返回答案是 JSON 字符串，你要拆开")
回复文本 = '{\"菜名\": \"青菜\", \"重量\": 12.5}'
print("收到的是文本：", 回复文本)
print("loads 之后：", json.loads(回复文本))
print("     → 然后你才能用 [\"菜名\"] 取值")
print()
print("场景 3：存配置文件")
print('写文件: open("配置.json","w").write(json.dumps(配置))')
print("读文件: 配置 = json.loads(open(\"配置.json\").read())")
