a = [1,2,3,4,4,4,7,8,8,8,8,8,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5,5]
b = [1,1,1,1,1,2,2,2,23,3,3,3,3,44,4,4,4,4,5,5,5,6,6,6,7,7,7]
print(set(a))

A = set(a)
print(A)

B = set(b)

print(sorted(A|B))
print(sorted(A-B))
print(sorted(A&B))
print(sorted(A^B))


一班 = ["小明", "小红", "小刚", "小美"]
二班 = ["小红", "小刚", "小李", "小王"]

aaa = sorted(set(一班)|set(二班))
bbb = sorted(set(一班)&set(二班))
ccc = sorted(set(一班)-set(二班))
ddd = sorted(set(一班)^set(二班))
print(aaa)
print(bbb)
print(ccc)
print(ddd)
print(len(aaa))



xueshengchengji = {
    '威龙':{'人头像' : 1,'怀表' : 3,'刀片' : 2,'坦克':2},
    '麦小雯':{'人头像':2,'怀表':4,'刀片':5,'步战车':2},
    '红狼':{'人头像':1,'怀表':3,'刀片':1,'世界名画':2}
}


aa = xueshengchengji['威龙'].keys()
bb = xueshengchengji['麦小雯'].keys()
cc = xueshengchengji['红狼'].keys()

AA = set(aa)
BB = set(bb)
CC = set(cc)
print(AA&BB&CC)

# 第 1 步：写一个"求某个学生平均分"的函数
def pinjun(name):
    fenshubiao = xueshengchengji[name]
    zongfen = 0
    for fenshu in fenshubiao.values():
        zongfen += fenshu                  # ← 这行你会写（sum_list 练过）
    return zongfen / len(fenshubiao)               # ← 科目数怎么来？

# 第 2 步：按平均分排（这行我直接给）
paiming = sorted(xueshengchengji, key=pinjun, reverse=True)
print(paiming)


# ===================================================================
# 【Python 第 4 周笔记 · 容器】2026-10-20
#   ↑ 上面是练习代码，下面是笔记。随便改，别把代码删了。
# ===================================================================

# ---------- 1. 四种容器对照 ----------
#   容器     括号写法     有序      可重复    可修改    典型用途
#   list      [  ]        ✅         ✅        ✅      一串东西：名单/成绩单/待办            列表
#   tuple     (  )        ✅         ✅        ❌      固定不变的一组值                     元组
#   set       {  }        ❌         ❌        ✅      唯一集合：去重/交集/标签
#   dict    { k: v }      ✅(3.7+)   key唯一   ✅      一张表：按名字查（通讯录/成绩）         字典
#
#   ⚠️ 大括号两种含义：{} 空的是 dict，空 set 必须写 set()
#   ⚠️ set(字典) / list(字典) 直接取 key，.keys() 可以省

# ---------- 2. 三大容器方法清单 ----------
# list:
#   append(x) 末尾加一个 | insert(i,x) 指定位置插入 | extend(其他) 接一整个容器
#   remove(x) 删指定值(没有会报错) | pop(i) 按位置弹出并返回 | pop() 弹最后一个
#   sort() 原地排序(返回 None) | reverse() 原地反转 | index(x) 找位置
#   count(x) 数有几个 | clear() 清空 | copy() 复制
#   for i, v in enumerate(lst) 同时拿下标和值 ⭐
#
# dict:
#   d[k]=v 增/改(已有 key 会静默覆盖) | update(其他) 批量更新
#   d.get(k,默认) 安全查 | d.pop(k,默认) 删并返回 | d.popitem() 删最后一组
#   del d[k] 硬删(没有会报错) | d.keys()/values()/items() 三种遍历(items 最常用)
#   k in d 判断 key 在不在 | d.setdefault(k,默认) 没有就建并返回 | clear()
#
# set:
#   add(x) 加一个(不是 append!) | update(其他) 加多个
#   remove(x) 删(没有会报错) | discard(x) 删(没有不报错) | pop() 弹一个
#   union 并集 | intersection 交集 | difference 差集 | symmetric_difference 对称差
#   运算符版本：|  &  -  ^   ← 只对 set 有效，list 不行
#   issubset / issuperset / isdisjoint 判断包含关系

# ---------- 3. 选型三问（写代码时的第一反应）----------
#   ① 要按名字/键查东西吗？          → 是 → dict
#   ② 要去重、或求交集并集吗？        → 是 → set
#   ③ 要保持顺序、允许重复吗？        → 是 → list
#   都不需要 → 默认 list（错了再换，改动成本低）
#
#   补充判断：重复是"脏数据"→ set；重复是"有效信息"→ list

# ---------- 4. 我踩过的坑（这份笔记最值钱的部分）----------
#   4.1 unhashable：list 不能当 dict 的 key
#        students.get(['小刚'], {}) → TypeError: unhashable type: 'list'
#        .get() 的参数是 key 本身，不带方括号（方括号是 d[k] 下标语法）
#   4.2 {} 不是空 set，是空 dict；空 set 要写 set()
#   4.3 list 不能用 | & - ^，必须先 set()
#        c = sorted(set(a)) → c 是 list！再用 | 就崩
#        正确：A = set(a)；B = set(b)；sorted(A | B)
#   4.4 sorted() 返回新 list；sort() 原地排序且返回 None（不能写 x = lst.sort()）
#   4.5 key=函数 不带括号！key=pinjun() → TypeError: missing 1 required argument
#   4.6 会变的东西别写死：zongfen / 4 → zongfen / len(fenshubiao)
#   4.7 中文 sorted 按 Unicode 编码排，不是拼音（输出看着乱是正常的）
#   4.8 定义了变量却忘用：for wu, count in ... 忘了把 wu 放进 print
#   4.9 三角色别搞混：入参(别人给的) / 累加器(自己新建) / 循环变量(每轮临时)
#        函数不该伸手拿全局变量，要用参数传进去
#
#   ---------- 以下 4.10~4.17 是 10-21 那天的坑（10-22 补记）----------
#
#   4.10 [重点] 静默错误三件套（现在最大的坎）：代码能跑，结果是错的        **************
#        缺 .strip()      -> "python." 和 "python" 被当成两个词
#        缺 reverse=True  -> 排出来的"前 N 名"其实是最后 N 名
#        if 缺 else/return -> 提示了"未覆盖"，照样覆盖了
#        这三个 Python 一声不吭，只能靠自己按 review 清单抓
#
#   4.11 if 缺 else / return：提示了却照样执行
#        if 姓名 in contacts: print("已存在，未覆盖")
#        contacts[姓名] = {...}      <- 照样覆盖了！
#        正确：有 return 就停在那，不往下走
#
#   4.12 循环变量把字典覆盖成整数
#        for w, counts in t:   -> int object has no attribute items
#        counts 是字典，c 是次数。拿到变量名先问：这位置它该是什么类型？
#
#   4.13 字符串方法返回新值，不改原变量
#        w.lower()      -> 白干，w 没变
#        w = w.lower()  -> 才对
#
#   4.14 两层就要两层都配默认值
#        d.get("不存在")             -> None，再链式 .get() 就 AttributeError
#        d.get("不存在", {})         -> 两层各配默认值
#
#   4.15 .get() 只读不建，setdefault() 没有就新建 —— 长得像，用途相反           **********
#        d.get(k, 默认)         有->返回它，无->返回默认值，字典不变
#        d.setdefault(k, 默认)  无->真的新建这个 key
#
#   4.16 continue 只能写在 for / while 里面，写在最外层直接 SyntaxError
#
#   4.17 遍历中 remove() 会漏删
#        [a,a,b] 里遍历 remove，只会删掉一个 a
#        统计时用 continue 跳过；要清理就用推导式重建一个新列表

#
#   ---------- 以下 4.18~4.19 是 10-22 补的 key= 专题（第一次自己抓到静默错误）----------
#
#   4.18 key= 是什么：一把"量大小"的尺子
#        lambda x: x[1]  等价于  def f(x): return x[1]   （lambda 就是没名字的 def）
#        x 是【当前这一个元素】，不是整个列表
#        items() 给的 x 是元组 -> x[0]是词，x[1]是次数
#        不给 key -> Python 直接比元组本身（先比词，词一样再比次数）-> 排成字母序
#        给了 key -> 挨个量一遍拿返回值比大小，但搬走的还是原来那个完整元组
#        尺子相同怎么办 -> 稳定排序，保持原来的先后（needs 2 和 learning 2 谁在前看原顺序）
#        key= 后面【永远不带括号】：key=pinjun 对，key=pinjun() 报 TypeError
#
#   4.19 [静默错误·亲身体验] x[1] 换到别的元素上，含义就变了
#        sorted(counts.keys(), key=lambda x: x[1])   -> 不报错！
#        因为 keys() 给的是字符串，'python'[1] 是第二个字母 'y'
#        结果按 a/e/o/y 排：['data','learn','code','python']  和次数毫无关系
#        正确想按次数排要么用 items()，要么 key=lambda x: counts[x]
#        教训：x[1] 到底取到什么，取决于 x 是什么类型 —— 跑一下看，别靠记忆
#
#   ---------- 以下 4.20~4.22 是 10-22 晚上复习补记 ----------
#
#   4.20 set 的对称差 ^ ：两边不同才算
#        A = {1,2,3}   B = {3,4,5}
#        A | B  -> {1,2,3,4,5}   并集：两边全要
#        A & B  -> {3}           交集：两边都要
#        A - B  -> {1,2}         差集：只在 A 不在 B
#        A ^ B  -> {1,2,4,5}     对称差：在A或B，但不能同时在两边
#        记法：^ 就是"异或"，两边不同才算。3 两边都有所以排除
#        另一个记法：A ^ B == (A - B) | (B - A)
#
#   4.21 推导式的结果类型，看括号就知道
#        {w for ...}        -> set    大括号且【没有冒号】= 集合
#        {w: c for ...}      -> dict   大括号且【有冒号】 = 字典
#        [w for ...]         -> list   方括号 = 列表
#        (w for ...)          -> generator 生成器（惰性，不急着全算）
#        记忆：跟第 1 章的括号口诀是同一条 —— 方=list 圆=tuple 大括号看有没有冒号
#
#   4.22 可变 vs 不可变：赋值是"贴标签"，不是复制
#        不可变：str  tuple          可变：list  dict  set
#        s = "hello"; s2 = s; s2 = s + "!"
#          -> 造了【新对象】贴到 s2 上，s 纹丝不动
#        lst = [1,2,3]; lst2 = lst; lst2.append(4)
#          -> 原地改，lst 和 lst2 指向【同一块内存】，lst 也变了
#        实测 id()：字符串 id(s) != id(s2)；列表 id(lst) == id(lst2)
#        这就是字符串方法必须赋值回去的原因（不可变，只能造新的换标签）
#        也这是 E17 浅拷贝的根源：dict(a) 只复制外层，内层还是共享的
#
# ---------- 5. 本周 4 个练习各自用到了什么 ----------
#   词频统计 word_count → 字符串.split() + dict 累加 counts[w] = counts.get(w,0)+1
#   学生成绩(嵌套)      → dict of dict，双层 items() 遍历
#   去重 / 班级名单     → set + | & - ^ 四种运算
#   班级成绩系统        → dict 存 + set 求交集 + sorted(key=函数, reverse=True)

# ---------- 6. 已经整明白的（10-22 复查确认）----------
#   [OK] 嵌套 dict "一层层剥皮"：students.values() 给的是内层 dict，要分数还得再剥一层
#        list(students['小明'].values())   <- 一行搞定，不用先存中间变量
#   [OK] sorted(字典, key=函数)：key 传的是函数本身，不是函数结果
#        sorted(counts.items(), key=lambda x: x[1], reverse=True)   <- items() 给出 (词, 次数)
#   [OK] set 运算结果想保序：先做 set 运算，最后再 sorted
#        sorted(A | B)   <- 运算在 set 上，排序放最后
#
# ---------- 7. 接下来要盯的 ----------
#   * 高频错题清单：D:\pythonProject\笔记\错题追踪.md
#     每周四 19:00 自动出卷重考，连对 2 次才退场，再犯会加门槛
#   * 下一个坎是静默错误：能跑 != 对。改完先跑一遍，看输出对不对
#   * 10-23（周五）上午：通讯录 CLI + 写 README + requirements.txt
#   * 10-24（周六）上午：README 改造成作品集主页 + 放项目截图
#
# ---------- 8. 10-22 晚复习结果（自己记一下，别管别人怎么说）----------
#   复习卷 6 大题 + 附加题 + 概念快查，做了 51 分钟，8 题全对
#   已记 streak 1/2 的 8 题：E01 E02 E03 E04 E05 E13 E15 E16
#     -> 这些题 10-29（周四）还会再考，连对 2 次才毕业
#   三个之前不会的，这晚学会了：4.20 对称差 / 4.21 推导式类型 / 4.22 可变不可变
#   最值钱的一课（10-22 第 3 题踩出来的）：
#     "加 else" != "停在这" —— else 只是给 if 加另一条路，程序照样往下走
#     只有 return 才是"到此为止"
#     还有一条：函数名 = 意图契约。叫 add 就别静默覆盖，叫 update 才直接覆盖



























