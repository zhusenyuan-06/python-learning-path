# ensure_ascii 对比.py
# 演示 json.dumps 的 ensure_ascii 参数

import json

订单 = {"菜名": "排骨", "重量": 15.0, "送到": "阳光城"}

print("=" * 58)
print("❌ 不写 ensure_ascii（默认值 True）")
print("=" * 58)
默认 = json.dumps(订单)
print(默认)
print()
print("看出来了：中文全变成了 \\u 开头的编码")
print()

print("=" * 58)
print("✅ 写 ensure_ascii=False")
print("=" * 58)
正常 = json.dumps(订单, ensure_ascii=False)
print(正常)
print()

print("=" * 58)
print("⭐ 关键：这两者的信息量【完全一样】")
print("=" * 58)
print("转回来对比：")
print("  默认版本 loads 回来 =", json.loads(默认))
print("  正常版本 loads 回来 =", json.loads(正常))
print("  两者相等吗？", json.loads(默认) == json.loads(正常))
print()
print("→ 只是【长得不一样】，数据一模一样")
print("→ 所以 dumps 出来的东西 loads 回去，永远能还原")
print()

print("=" * 58)
print("⚠️ 为什么默认要转义？")
print("=" * 58)
print("JSON 标准诞生时，有些老语言/老系统【看不懂中文】")
print("转成 \\uXXXX 后，任何语言都能读")
print("→ 兼容性换可读性")
print()
print("但对我们来说：")
print("  1. 你要看 JSON 内容 → 一定要 ensure_ascii=False")
print("  2. 你要发给 LLM API → 也要 ensure_ascii=False")
print("     （不然中文变成 \\uXXXX，模型要多绕一层，回复质量会掉）")
print()
print("=" * 58)
print("💡 记忆：只要跟中文打交道，dumps 就写死 ensure_ascii=False")
print("=" * 58)
