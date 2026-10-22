# -*- coding: utf-8 -*-
"""周四大复习 · 自检锚点 —— 真实跑一遍每道题的错误写法，看它到底输出什么。"""

def hr(t):
    print("\n" + "=" * 60)
    print(t)
    print("-" * 60)


# ---------------------------------------------------------------- E03 / E15
hr("E03 + E15：缺 .strip()，词频被标点污染")
text = "hello, world! hello python."
words = text.split()

bad = {}
for w in words:
    w = w.lower()
    bad[w] = bad.get(w, 0) + 1
print("❌ 不 strip ->", bad)

good = {}
for w in words:
    w = w.lower().strip(".,!?")
    if w:
        good[w] = good.get(w, 0) + 1
print("✅ strip 后 ->", good)
print("→ 差异键:", set(bad) - set(good), "| 'hello' 计数:", bad.get("hello"), "vs", good.get("hello"))


# ---------------------------------------------------------------- E04 / E15
hr("E04 + E15：sorted 漏 reverse=True")
counts = {"python": 5, "data": 2, "learn": 3, "code": 2}
asc = sorted(counts.items(), key=lambda x: x[1])
desc = sorted(counts.items(), key=lambda x: x[1], reverse=True)
print("❌ 升序 ->", asc)
print("✅ 降序 ->", desc)
print("→ 第一名:", asc[0], "vs", desc[0])


# ---------------------------------------------------------------- E01
hr("E01：if 缺 else/return —— 提示了却照样覆盖")
contacts = {"小明": {"电话": "13800138000"}}
def a_bad(name, p):
    if name in contacts:
        print("已存在，未覆盖")
    contacts[name] = {"电话": p}
    return contacts

def a_good(name, p):
    if name in contacts:
        return "已存在，未覆盖"
    contacts[name] = {"电话": p}
    return contacts

print("❌ 调用前:", contacts)
a_bad("小明", "13911112222")
print("❌ 调用后:", contacts, "→ 旧电话被覆盖了:", contacts["小明"])
contacts2 = {"小明": {"电话": "13800138000"}}
def a_good2(name, p, c):
    if name in c:
        return "已存在，未覆盖"
    c[name] = {"电话": p}
    return c
print("✅ 调用后:", a_good2("小明", "13911112222", contacts2))


# ---------------------------------------------------------------- E02
hr("E02：同一个变量名承担两种角色")
def sum_list_bad(nums):
    nums = 0
    for i in nums:
        nums += i
    return nums
try:
    print(sum_list_bad([1, 2, 3]))
except Exception as e:
    print("❌ 入参被覆盖 ->", type(e).__name__, ":", e)

def sum_list_good(nums):
    total = 0
    for i in nums:
        total += i
    return total
print("✅ 正确 ->", sum_list_good([1, 2, 3]))

t = {"python": 5, "data": 2}
try:
    for w, counts in t.items():   # counts 这里变成 int
        print(w, counts)
    counts["x"] = 1                # ❌ 现在 counts 是 int，不是字典
except Exception as e:
    print("❌ 字典 counts 被覆盖成 int ->", type(e).__name__, ":", e)
for w, c in t.items():             # ✅ 换个名字
    print("✅ 换个名字 ->", w, c)

print("❌ 循环变量泄漏:", end=" ")
pairs = [("python", 5), ("data", 2)]
for w, c in pairs:
    pass
print("w =", repr(w), "c =", repr(c), "（出了循环还在，类型已被换掉）")


# ---------------------------------------------------------------- E05
hr("E05：类型不统一")
c_bad = {"小明": {"电话": 13800138000}, "小红": {"电话": "13900139000"}}
print("❌ ", c_bad)
print("   类型:", [type(v["电话"]).__name__ for v in c_bad.values()])
try:
    print("   拼接:", "电话" + str(c_bad["小明"]["电话"]))
except Exception as e:
    print("   拼接失败:", e)
c_good = {"小明": {"电话": "13800138000"}, "小红": {"电话": "13900139000"}}
print("✅ ", c_good)
print("   类型:", [type(v["电话"]).__name__ for v in c_good.values()])
try:
    print("   数字位数:", max(len(v["电话"]) for v in c_good.values()))
except Exception as e:
    print("   len() 失败:", type(e).__name__, ":", e)


# ---------------------------------------------------------------- E13
hr("E13：字符串方法返回新值，不改原变量")
w = "  Python  "
print("原始 w =", repr(w))
r = w.lower().strip()
print("❌ 只调用不赋值 -> w 仍是:", repr(w), "| 临时结果 r =", repr(r))
w2 = "  Python  "
w2 = w2.lower().strip()
print("✅ 赋值回去 -> w2 =", repr(w2))
print("→ 实战：拿 w.lower() 直接当词统计，等于什么都没做")


# ---------------------------------------------------------------- E16 附
hr("E16：x[1] 取到什么，取决于 x 是什么类型（静默）")
counts2 = {"data": 2, "learn": 3, "code": 2, "python": 5}
try:
    r = sorted(counts2.keys(), key=lambda x: x[1])
    print("keys() + x[1] 不报错 ->", r, "→ 按第二个字母排的：", [w[1] for w in r])
except Exception as e:
    print("报错:", type(e).__name__, e)

print("\n全部锚点跑完。")
