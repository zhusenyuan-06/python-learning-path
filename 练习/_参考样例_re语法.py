# -*- coding: utf-8 -*-
"""_参考样例_re语法.py —— 正则语法样例集（只演示语法，任务在 11.14练习_re正则基础.py）

跑法：python _参考样例_re语法.py
这份文件是 11-14 讲义《re 正则基础》的输出来源，讲义里贴的每段输出都来自这里。
"""
import re

print("=" * 60)
print("【1】三个必会函数：search / findall / finditer")
print("=" * 60)
文本 = "联系方式：邮箱 zhangsan@mail.com，手机 13800138000，备用邮箱 lisi@abc.cn"

m = re.search(r"\d+", 文本)
print("search  ->", m, "| .group() =", m.group(), "| .start() =", m.start())
print("findall ->", re.findall(r"\d+", 文本))
print("findall(邮箱) ->", re.findall(r"[\w.+-]+@[\w-]+\.\w+", 文本))
for mm in re.finditer(r"\d{3}", 文本):
    print("  finditer:", mm.group(), "位置", mm.span())

print()
print("=" * 60)
print("【2】元字符速查：. ^ $ \\d \\w \\s")
print("=" * 60)
s = "abc123 def456\nGHI789"
print("re.findall(r'\\d+', s)      =", re.findall(r"\d+", s))
print("re.findall(r'\\w+', s)      =", re.findall(r"\w+", s))
print("re.findall(r'[a-z]+', s)    =", re.findall(r"[a-z]+", s))
print("re.findall(r'[^a-z]+', s)   =", re.findall(r"[^a-z]+", s))
print("re.findall(r'^\\w+', s)     =", re.findall(r"^\w+", s))
print("re.findall(r'\\w+$', s)     =", re.findall(r"\w+$", s))
print("注意：. 不匹配换行 ->", re.findall(r"a.c", "a\nc"))
print("      [\\s\\S] 才跨越换行 ->", re.findall(r"a[\s\S]c", "a\nc"))

print()
print("=" * 60)
print("【3】量词：* + ? {m,n}  和 贪婪 vs 非贪婪")
print("=" * 60)
html = "<p>hello</p><p>world</p>"
print("贪婪   r'<p>.*</p>'      =", re.findall(r"<p>.*</p>", html))
print("非贪婪 r'<p>.*?</p>'     =", re.findall(r"<p>.*?</p>", html))
print("数量   r'a{2,3}'         =", re.findall(r"a{2,3}", "a aa aaa aaaa"))
print("可选   r'colou?r'        =", re.findall(r"colou?r", "color colour"))
print("至少一次 r'\\d+'          =", re.findall(r"\d+", "ab1cd22ef333"))

print()
print("=" * 60)
print("【4】分组：捕获组 ( ) / 非捕获 (?: ) / 命名组 (?P<name> )")
print("=" * 60)
log = "2026-11-14 ERROR 文件写入失败"
print("全部匹配 r'(\\d{4})-(\\d{2})-(\\d{2})' ->",
      re.findall(r"(\d{4})-(\d{2})-(\d{2})", log))
print("⚠️ 有捕获组时 findall 返回的是【组内容】，不是整个匹配！")
print("无捕获组 r'(?:\\d{4})-(\\d{2})-(\\d{2})' ->",
      re.findall(r"(?:\d{4})-(\d{2})-(\d{2})", log))
m2 = re.search(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})", log)
print("命名组 m.group('y') =", m2.group("y"), "| group('m') =", m2.group("m"))
print("group() 全部 =", m2.groups())

print()
print("=" * 60)
print("【5】re.sub 替换：把日期统一格式")
print("=" * 60)
杂 = "会议 2026/11/14 和 2026.11.14 和 2026年11月14日"
print("原文:", 杂)
print("统一后:", re.sub(r"(\d{4})[/.年](\d{2})[/.月](\d{2})日?", r"\1-\2-\3", 杂))
print("只替换数字用 \\1 引用捕获组；命名组用 \\g<name>")

print()
print("=" * 60)
print("【6】标志位 flags")
print("=" * 60)
print("IGNORECASE:", re.findall(r"abc", "ABC abc AbC", re.IGNORECASE))
print("MULTILINE: ^ 每行行首 ->", re.findall(r"^\w+", "one\ntwo\nthree", re.MULTILINE))
print("DOTALL   : . 匹配换行 ->", re.findall(r"a.b", "a\nb", re.DOTALL))

print()
print("=" * 60)
print("【7】re.compile 复用（同一模式用多次时）")
print("=" * 60)
pat = re.compile(r"\d{4}-\d{2}-\d{2}")
print("编译后 findall:", pat.findall(log))
print("编译后 search :", pat.search(log).group())
print("编译后 sub    :", pat.sub("2026-11-14", "日期是 2026-11-14 哦"))

print()
print("=" * 60)
print("【8】实战：提取日期 / 邮箱 / 手机号")
print("=" * 60)
样本 = """张老师，邮箱 zhang.san+tag@company-mail.com
手机 13800138000，学生 wangwu@school.edu.cn
2026-11-14 补做 re 正则基础
2026年11月13日 上课，11月12日复习
备用 li@163.com，座机 010-12345678"""
print("日期(\\d{4}-\\d{2}-\\d{2}) :", re.findall(r"\d{4}-\d{2}-\d{2}", 样本))
print("日期(年月日)            :", re.findall(r"\d{4}年\d{1,2}月\d{1,2}日", 样本))
print("邮箱(简版)             :", re.findall(r"[\w.+-]+@[\w-]+\.\w+", 样本))
print("⚠️ 简版把 wangwu@school.edu.cn 截成 wangwu@school —— 域名多段要用 (?:\\.[\\w-]+)+")
print("邮箱(完整版)           :", re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", 样本))
print("手机号(1开头11位)      :", re.findall(r"1[3-9]\d{9}", 样本))

print()
print("=" * 60)
print("【9】五个最容易踩的坑（实跑验证）")
print("=" * 60)
# 坑1：空匹配
print("坑1 re.findall(r'a*', 'bb') =", re.findall(r"a*", "bb"), "  <- 全是空串")
# 坑2：$ 是行尾不是字符串尾
multi = "第一行\n第二行"
print("坑2 re.search(r'\\w+$', multi) =", re.search(r"\w+$", multi).group(),
      " <- 匹配到的是「第二行」的行尾")
multi2 = "hello\n"
print("   对照 'hello\\n'：")
print("     r'\\w+$'  ->", re.search(r"\w+$", multi2).group(),
      " <- 匹配的是【第一行】的行尾")
print("     r'\\w+\\Z' ->", re.search(r"\w+\Z", multi2),
      " <- 字符串末尾是换行符，\\Z 找不到")
print("   要整个字符串末尾用 \\Z 或 re.fullmatch")
# 坑3：. 不跨行
print("坑3 re.findall(r'a.c', 'a\\nc') =", re.findall(r"a.c", "a\nc"), " <- 匹配不到")
# 坑4：字符类里的 - 和 ^
print("坑4 r'[a-c-e]' 匹配:", re.findall(r"[a-c-e]", "b-"), " <- - 在中间是范围 a到e")
print("   r'[-a-c]' 匹配:", re.findall(r"[-a-c]", "b-"), " <- - 在开头就是普通字符")
# 坑5：Python3 的 \w 和 \d 默认 Unicode
print("坑5 r'\\w+' 匹配中文:", re.findall(r"\w+", "中文abc"))
print("   r'\\d+' 匹配全角数字:", re.findall(r"\d+", "１２３"))

print()
print("=" * 60)
print("【10】转义：特殊字符要加反斜杠 / 用 re.escape")
print("=" * 60)
print("直接匹配 a.c :", re.findall(r"a\.c", "abc a.c"))
print("re.escape     :", re.escape("a.c"), "->", re.findall(re.escape("a.c"), "abc a.c"))
print("re.escape 整句:", re.escape("价格是 3.5 元"), "->",
      re.findall(re.escape("价格是 3.5 元"), "价格是 3.5 元 哦"))

print()
print("✅ 样例全部跑完")
