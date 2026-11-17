# -*- coding: utf-8 -*-
"""11.17 练习：PDF 解析（补 11-17 上午「PyPDF2/pdfplumber 解析 PDF 文本」+ 下午「提取课件某页文本」两档欠账）

════════════════════════════════════════════════════════════════════
这个文件分【四段】，顺序别搞乱：

  📘 【讲解区】只读 —— 三个库的能力对比 + 五个坑，只有这一处讲
  🅰️ 【任务区】只读 —— 6 个任务，标明要做什么、期望什么
  ✍️ 【作答区】—— 你写代码的地方（TODO 1-① …）
  ✅ 【自动检查】—— 跑完看这里，别改
  🔒 【参考答案】—— 放最后，做完再看

⭐ 作答区【故意不给 API 片段】：
   只在上面的讲解区讲过一次，答的时候要自己从讲解区「回忆」写法。
   这叫「提取练习」，比你直接抄一遍有效得多。

⭐⭐ 每个任务函数都有【返回值约定】：
   自动检查会【真的调用你写的函数】，拿它的 return 值跟期望比对。
   所以 —— 打印出来不算数，必须把结果 return 出来。

⭐⭐⭐ 素材路径：
   真实课件 PDF 在 C:\\Users\\15816\\Downloads\\ 下（6 份，都是你自己的复习资料）
   主素材 = 《计算机网络基础》复习 题-答案版.pdf（8 页，文本清晰，最适合练）
   反面素材 = 《大学物理实验（一）》讲义.pdf（98 页，其中 44 页是【扫描图片页】，提取不到文字）
"""

import os
import sqlite3
from pathlib import Path

# ============================================================
# 📘【讲解区】只读 —— 别改这里，改了也不影响检查，但你会失去对照
# ============================================================

print("""
════════════════════════════════════════════════════════════════
📘 讲解区 · PDF 解析
════════════════════════════════════════════════════════════════

【一】你要装哪几个库？—— 本机已经全装好了，别 pip install

  PyPDF2     3.0.1    最老牌，纯 Python，写法最简单
  pdfplumber 0.11.10  基于 pdfminer.six，能提表格（但慢）
  pymupdf    2.0.0    aka fitz —— 最快，本机实测 98 页只用 0.79 秒
  PIL        有        图像处理（PDF 解析用不上，别管）

  ⚠️ fitz 是【被弃用的老名字】，import 会警告 FutureWarning。
     正确写法：import pymupdf   然后用 pymupdf.open(...)

【二】三个库怎么打开 PDF？（本机实测，6 份 PDF 全部有文本层）

  PyPDF2:
      reader = PyPDF2.PdfReader(路径)          # 读文件
      n = len(reader.pages)                    # 页数
      text = reader.pages[0].extract_text()    # 第 1 页文字

  pdfplumber:
      with pdfplumber.open(路径) as pdf:        # 必须用 with 关文件
          n = len(pdf.pages)
          text = pdf.pages[0].extract_text()

  pymupdf:
      doc = pymupdf.open(路径)                 # 不用 with，但你要自己 close()
      n = doc.page_count
      text = doc[0].get_text()                 # 注意是 get_text 不是 extract_text
      doc.close()

【三】⭐⭐⭐ 三个库的真实差异（本机实测，别背，实跑记）

  ┌──────────────┬────────────┬─────────────┬─────────────┐
  │              │  PyPDF2    │ pdfplumber  │  pymupdf    │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 取第1页文字  │pages[0]    │ pages[0]    │ doc[0]      │
  │              │.extract_   │ .extract_   │ .get_text() │
  │              │ text()     │ text()      │             │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 98页耗时     │  23~27 秒  │  47 秒      │  0.79 秒 ⚡ │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 页眉「第1页」 │  ✅ 保留 │  ❌ 丢掉   │  ✅ 保留    │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 空格处理     │ 无空格     │ 无空格      │ 保留空格   │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 空文本页     │  '' 空串   │  '' 空串    │  '' 空串    │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 能知页面有   │   ❌ 不知  │   ❌ 不知   │ ✅ get_     │
  │ 没有图片     │            │             │ images()    │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 提表格       │    ❌      │  ✅ 要页面上 │  ❌         │
  │              │            │  真有表格线 │             │
  ├──────────────┼────────────┼─────────────┼─────────────┤
  │ 关键词定位   │    ❌      │    ❌       │ ✅ search_  │
  │              │            │            │  for()      │
  └──────────────┴────────────┴─────────────┴─────────────┘

  → pymupdf 比 PyPDF2 快【29~35 倍】，还多两个别人没有的能力
  → ⭐ 但三个库取的文字【不完全一样】（页眉、空格都不同）
    → 校验文本不能直接比字符串，要比关键词 / 去空格后比 / 只比长度

【四】⭐ 五个坑（全部本机实测出来的）

  坑 1 · 三种空结果长得不一样
        PyPDF2 空文本页   → ''        （空字符串，不是 None）
        pdfplumber 空页   → ''        （同上）
        pymupdf 空页      → ''        （同上）
        ⚠️ 但【文件打不开】时三个库抛的是不同异常：
            PyPDF2   → PdfReadError
            pdfplumber → PDFSyntaxError / FileNotFoundError
            pymupdf  → pymupdf.FileNotFoundError
        → 所以判断"这页没文字"要用【长度判断】，不要用 `is None`

  坑 2 · ⭐⭐⭐ 扫描图片页提取不到文字（今天最大的坑）
        《大学物理实验（一）》讲义.pdf 共 98 页，
        其中【44 页是扫描图片】—— 页面里只有图片，没有文字层。
        用 extract_text() 拿到的是空字符串。
        怎么知道它是图片页？pymupdf 能查：
            len(doc[i].get_images()) > 0   → 这页有图，很可能是扫描页
        → 真实项目里这类页要靠 OCR（本机没装 pytesseract）

  坑 3 · 页码从 0 开始
        doc[0] 是【第 1 页】，不是第 0 页
        人说的「第 3 页」= doc[2]

  坑 4 · pdfplumber 必须用 with，否则文件不关
        with pdfplumber.open(路径) as pdf:
            ...
        # 出了 with 块，文件才真的关闭
        （pymupdf 反而【不】自动关，要自己 doc.close()）

  坑 5 · pdfplumber 提取表格【要页面上真有表格线】
        《计算机网络基础》复习题 第 1 页没有表格 → extract_tables() 返回 []
        但它的【第 5 页】有一张答案对照表（题号/答案，14 列）→ 能提出来
        《工程数学复习题》第 4、5 页也有表
        → 【表格在哪页得逐页试】，不能只看第一页就下结论
        → 而且表格里会出现 \\n（单元格里换行），处理时要 replace("\\n", "")

  坑 6 · ⭐⭐⭐⭐ 写完答案【自己验证时】，别拿「全文 ==」当判据
        我做完这 6 题后用 pdfplumber 独立重算，结果「任务3 全文」判不一致：
            pymupdf 拼出来 5400 字符 / pdfplumber 拼出来 5462 字符
        差点以为是答案写错了。查下去发现：
            去掉所有空白后，两边【长度完全相同】（4878 = 4878）
            两边【字符出现频次完全相同】（一个字都不多不少）
            差别只是【页眉「第1页，共8页」在每页的开头还是结尾】
        → 内容完全等价，只是排版顺序不同
        → ⭐ 正确判据是「去空白 + 去掉页眉后比字符多重集」或「比关键词/长度区间」
        → ⭐ 验证工具的判据本身也会错（T38）：
          看到不一致时，先怀疑【判据】，再怀疑【被验证的对象】

【五】文件路径怎么写？

        from pathlib import Path
        素材目录 = Path(r"C:/Users/15816/Downloads")
        pdf路径 = 素材目录 / "《计算机网络基础》复习 题-答案版.pdf"

        ⚠️ 路径里有中文和书名号《》，一定要用 r"..." 原始字符串
        ⚠️ 用 Path 比拼字符串好：/ 运算符会自动加分隔符

【六】sqlite3.connect 会不会自己造文件？

        会！！如果你路径写错，它会【静默创建一个 0 字节的假库】
        → 每次 connect 前先 assert 路径存在
""")


# ============================================================
# 🅰️【任务区】只读 —— 6 个任务
# ============================================================

素材目录 = Path(r"C:/Users/15816/Downloads")
主素材 = 素材目录 / "《计算机网络基础》复习 题-答案版.pdf"
扫描素材 = 素材目录 / "《大学物理实验（一）》讲义.pdf"
工程素材 = 素材目录 / "2025-2026-1工程数学复习题.pdf"

print("""
════════════════════════════════════════════════════════════════
🅰️ 任务区 · 6 个任务
════════════════════════════════════════════════════════════════

【任务 1】数一数有几页
  做什么：打开 主素材，返回它的总页数（int）
  期望：8
  考点：三个库都能数页，但你要能说清用哪个

【任务 2】取第 3 页的文字
  做什么：打开 主素材，返回【第 3 页】的纯文本（str）
         ⚠️ 人说的「第 3 页」在代码里是 [2]
  期望：是 str，长度 > 700，且包含 'CRC'（这页开头是二进制串 + CRC 校验）
  考点：页码从 0 开始这个坑
  ⚠️ 注意：这页开头是「1010101 11110011 0000」这种二进制串，
         是 PDF 里的【真内容】不是乱码 —— 提取出来就该长这样

【任务 3】全文拼起来
  做什么：打开 主素材，把【每一页】的文字用换行拼成一个长字符串，返回
  期望：str，且长度 > 3000
  考点：遍历所有页 + 拼接

【任务 4】找出含关键词的页码
  做什么：打开 主素材，返回【所有包含 '时延' 两个字的页的页码列表】（list[int]）
         ⚠️ 页码要用【人看的 1 开始】，不是代码里的 0 开始
  期望：正好是 [1, 3, 6]（实测值）
  考点：遍历时把 0 开始的 index 转成 1 开始的页码
  ⚠️ 注意：第 2 页没有 '时延' —— 如果你算出 [1,2,3,6]，说明你把别的字也匹配上了

【任务 5】⭐⭐⭐ 找出「扫描图片页」
  做什么：打开 扫描素材（《大学物理实验（一）》讲义.pdf，98 页），
         返回【提取不到文字的那些页的人看页码列表】（list[int]）
  期望：正好是 44 页，第 4 页在列表里（第 1~3 页有文字，第 4 页开始是扫描图）
  考点：⭐ 本题是今天真正的核心 —— 学会区分「有文字的页」和「只有图的页」
        提示：可以先试 extract_text() 拿文字，也可以用 pymupdf 看 get_images()
        ⚠️ 用哪几个库都行，但【只能扫前 50 页】来控制时间（后面几页再扫）
        💡 这 44 页里每页都有图片 —— 真实项目碰到这种要靠 OCR（本机没装）

【任务 6】存成 CSV（这是 11-18 上午「课件 PDF→提取文本→存 CSV」的前半步）
  做什么：打开 主素材，把每一页的文字存进一个 SQLite 库，
         表名 页文本，列：页码(int) / 文字(text)
         然后返回【存进去的行数】（int）
  期望：8
  考点：这是 PDF 提取的【落地一步】—— 不存进数据库，提取出来也没用
        ⚠️ sqlite3.connect 的路径写错会静默生成 0 字节假库
        ⚠️ 别忘了 con.commit()，否则关闭连接时数据回滚
""")


# ============================================================
# ✍️【作答区】—— 标准答案 + 逐行注释版（用来对照学习）
# ============================================================
# ⭐ 下面每行代码都有注释。做练习时可以先自己写，写完再对照这里看差在哪。
#    要清空重做时，把每个函数体删掉、只留 TODO 行即可。

# 只导入了 pymupdf —— 它是三个库里唯一能回答
# 「这一页到底有没有图片」的（任务 5 要用），而且快 29~35 倍。
import pymupdf

# 任务 6 要写的 SQLite 库文件放哪：
# __file__.parent = 本文件所在目录，保证不管从哪个目录运行，
# 库文件都落在 练习/ 下面（不会到处乱扔）。
库文件 = Path(__file__).parent / "练习库_PDF.sqlite"


def 任务1_数页数():
    """返回 主素材 的总页数（int）。"""
    # 第1步：open 打开 PDF 文件，拿到一个 doc 对象
    #        （pymupdf 用 open()；PyPDF2 用 PdfReader()）
    doc = pymupdf.open(主素材)
    # 第2步：读页数。pymupdf 的页数是【属性】doc.page_count，不是函数
    #        （PyPDF2 是 len(reader.pages)，pdfplumber 是 len(pdf.pages)）
    页数 = doc.page_count
    # 第3步：关文件。pymupdf 【不会自动关】，必须自己 close()
    #        （pdfplumber 用 with 自动关，PyPDF2 不用管）
    doc.close()
    # 第4步：return 交出去。自动检查会真的调用这个函数、拿返回值比对
    return 页数


def 任务2_取第3页():
    """返回 主素材【第 3 页】的纯文本（str）。"""
    # 第1步：打开 PDF
    doc = pymupdf.open(主素材)
    # 第2步：⭐ 取第 3 页 → 写 doc[2]，不是 doc[3]
    #        索引从 0 开始：doc[0]=第1页, doc[1]=第2页, doc[2]=第3页
    #        方法名是 get_text()（PyPDF2/pdfplumber 叫 extract_text()）
    文字 = doc[2].get_text()
    # 第3步：关文件
    doc.close()
    # 第4步：return（题目要的是纯文本 str，不是打印出来）
    return 文字


def 任务3_拼全文():
    """返回 主素材 全部页面的文字拼成的长字符串（str）。"""
    # 第1步：打开 PDF
    doc = pymupdf.open(主素材)
    # 第2步：准备一个空列表当「收集筐」
    全部 = []
    # 第3步：遍历每一页。range(doc.page_count) = 0,1,2,...,7（共 8 页）
    for 序号 in range(doc.page_count):
        # 第3步a：取这一页的文字，塞进收集筐
        #          这里的变量名故意叫 序号，它是【0 开始的】，不是页码
        全部.append(doc[序号].get_text())
    # 第4步：关文件（先关再拼更规范）
    doc.close()
    # 第5步：⭐ 用换行符把列表拼成一个长字符串
    #        写法是：换行符.join(列表) —— 元素之间插一个换行
    #        （不 join 直接 return 全部，返回的是 list 不是 str，会判错）
    return chr(10).join(全部)


def 任务4_找关键词页():
    """返回 主素材 中所有含 '时延' 的页的【人看页码】列表（list[int]）。"""
    # 第1步：打开 PDF
    doc = pymupdf.open(主素材)
    # 第2步：准备空列表装「命中了关键词的页码」
    命中页码 = []
    # 第3步：逐页检查
    for 序号 in range(doc.page_count):
        # 第3步a：取这一页的文字
        文字 = doc[序号].get_text()
        # 第3步b：⭐ 判断这一页有没有 '时延' 这两个字
        #        Python 的 in 就是「里面有没有」—— 有就返回 True
        if "时延" in 文字:
            # 第3步c：⭐ 命中了，把页码记下来
            #          序号 + 1 —— 序号从 0 开始，人看的页码从 1 开始
            #          （索引 0 是人看的第 1 页，所以要 +1）
            命中页码.append(序号 + 1)
    # 第4步：关文件
    doc.close()
    # 第5步：return 列表。实测结果是 [1, 3, 6]
    return 命中页码


def 任务5_找扫描页():
    """返回 扫描素材 中提取不到文字的页的【人看页码】列表（list[int]）。"""
    # 第1步：打开那份 98 页的物理讲义
    doc = pymupdf.open(扫描素材)
    # 第2步：准备空列表装「扫描页的页码」
    扫描页码 = []
    # 第3步：⭐ 只扫前 50 页（题目限制）
    #        range(50) = 0~49，也就是人的第 1~50 页
    #        为什么不扫全部？这题考的是【方法】，不是【速度】
    for 序号 in range(50):
        # 第3步a：⭐ 取这一页的文字
        文字 = doc[序号].get_text()
        # 第3步b：⭐ 核心判断 —— strip() 去掉首尾空白后，长度是不是 0
        #        为什么用 strip()？有的页提取出来是「只有空白没有内容」的情况，
        #        不 strip 会误判成有文字
        if len(文字.strip()) == 0:
            # 第3步c：这页没有文字层 → 是扫描图片页，记下页码
            扫描页码.append(序号 + 1)
    # 第4步：关文件
    doc.close()
    # 第5步：return。实测结果：44 页，第 4 页 ~ 第 47 页
    return 扫描页码


def 任务6_存进数据库():
    """把 主素材 每页文字存进 SQLite，返回存进去的行数（int）。"""
    # 第1步：⭐ 先删掉旧的库文件，保证每次跑结果都一样
    #        不删的话第二次跑会「表已存在」报错，或者行数翻倍
    if 库文件.exists():
        库文件.unlink()
    # 第2步：打开 PDF
    doc = pymupdf.open(主素材)
    # 第3步：⭐ 连数据库。sqlite3.connect 的路径写错会【静默创建 0 字节假库】
    #        这里连的是上面定义好的 库文件（要么被删了重建，要么正确使用）
    con = sqlite3.connect(库文件)
    # 第4步：拿一个游标（游标 = 用来发命令给数据库的对象）
    cur = con.cursor()
    # 第5步：建表。两列：页码(int) + 文字(text)
    #        IF NOT EXISTS = 「不存在才建」，防止重复建表报错
    cur.execute("CREATE TABLE IF NOT EXISTS 页文本 (页码 INTEGER, 文字 TEXT)")
    # 第6步：逐页把文字写进去
    for 序号 in range(doc.page_count):
        # 第6步a：⭐ 用 ? 占位符传参（参数化查询）
        #        不要用字符串拼接把内容塞进 SQL —— 那是 SQL 注入漏洞
        #        第二个 ? 传整页文字（几千字），同样没问题
        cur.execute("INSERT INTO 页文本 (页码, 文字) VALUES (?, ?)",
                    (序号 + 1, doc[序号].get_text()))
    # 第7步：⭐ 必须 commit！不提交的话，关闭连接时数据会被回滚掉
    con.commit()
    # 第8步：查一下到底存进去几行（COUNT(*) 数的是行数，不是 rowcount）
    行数 = cur.execute("SELECT COUNT(*) FROM 页文本").fetchone()[0]
    # 第9步：关数据库连接
    con.close()
    # 第10步：关 PDF 文件
    doc.close()
    # 第11步：return 行数。实测 = 8（8 页 → 8 行）
    return 行数


# ============================================================
# ✅【自动检查】—— 跑完看这里，别改
# ============================================================

def _检查():
    print("=" * 60)
    print("✅ 自动检查")
    print("=" * 60)

    结果 = []

    # --- 任务 1 ---
    try:
        r1 = 任务1_数页数()
        好 = (r1 == 8)
        print("第1题 数页数        → %-12s %s" % (repr(r1), "✅" if 好 else "❌ 期望 8"))
        结果.append(好)
    except Exception as e:
        print("第1题 数页数        → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    # --- 任务 2 ---
    try:
        r2 = 任务2_取第3页()
        好 = (isinstance(r2, str) and len(r2) > 700 and "CRC" in r2)
        print("第2题 取第3页       → %-12s %s" % (type(r2).__name__, "✅" if 好 else "❌ 期望 str 长度>700 且含 'CRC'"))
        结果.append(好)
    except Exception as e:
        print("第2题 取第3页       → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    # --- 任务 3 ---
    try:
        r3 = 任务3_拼全文()
        好 = (isinstance(r3, str) and len(r3) > 3000)
        print("第3题 拼全文        → %-12s %s" % (type(r3).__name__, "✅" if 好 else "❌ 期望 str 且长度>3000"))
        结果.append(好)
    except Exception as e:
        print("第3题 拼全文        → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    # --- 任务 4 ---
    try:
        r4 = 任务4_找关键词页()
        好 = (r4 == [1, 3, 6])
        print("第4题 找关键词页    → %-12s %s" % (r4, "✅" if 好 else "❌ 期望 [1, 3, 6]"))
        结果.append(好)
    except Exception as e:
        print("第4题 找关键词页    → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    # --- 任务 5 ---
    try:
        r5 = 任务5_找扫描页()
        好 = (isinstance(r5, list) and len(r5) == 44 and 4 in r5
              and all(isinstance(x, int) for x in r5))
        print("第5题 找扫描页      → %-12s %s" % (len(r5) if isinstance(r5, list) else r5,
              "✅" if 好 else "❌ 期望 44 页的 list[int] 且含 4"))
        结果.append(好)
    except Exception as e:
        print("第5题 找扫描页      → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    # --- 任务 6 ---
    try:
        r6 = 任务6_存进数据库()
        好 = (r6 == 8)
        print("第6题 存进数据库    → %-12s %s" % (r6, "✅" if 好 else "❌ 期望 8"))
        结果.append(好)
    except Exception as e:
        print("第6题 存进数据库    → 报错 %s: %s" % (type(e).__name__, e))
        结果.append(False)

    print("-" * 60)
    对 = 结果.count(True)
    print("通过 %d / %d" % (对, len(结果)))
    if 对 == len(结果):
        print("🎉 全对！")
    print()
    print("⚠️ 任务 6 会真的写一个 .sqlite 文件到当前目录，跑完记得看一眼。")
    return 对 == len(结果)


if __name__ == "__main__":
    _检查()


# ============================================================
# 🔒【参考答案】—— 做完再看
# ============================================================

参考答案代码 = '''
import pymupdf
import PyPDF2
import sqlite3
from pathlib import Path

素材目录 = Path(r"C:/Users/15816/Downloads")
主素材 = 素材目录 / "《计算机网络基础》复习 题-答案版.pdf"
扫描素材 = 素材目录 / "《大学物理实验（一）》讲义.pdf"
库文件 = Path("练习库_PDF.sqlite")


# --- 任务 1 ---
def 任务1_数页数():
    doc = pymupdf.open(主素材)
    n = doc.page_count
    doc.close()
    return n


# --- 任务 2 ---
def 任务2_取第3页():
    doc = pymupdf.open(主素材)
    text = doc[2].get_text()          # [2] = 人的「第 3 页」
    doc.close()
    return text


# --- 任务 3 ---
def 任务3_拼全文():
    doc = pymupdf.open(主素材)
    全部 = []
    for i in range(doc.page_count):
        全部.append(doc[i].get_text())
    doc.close()
    return "\\n".join(全部)


# --- 任务 4 ---
def 任务4_找关键词页():
    doc = pymupdf.open(主素材)
    命中 = []
    for i in range(doc.page_count):
        if "时延" in doc[i].get_text():
            命中.append(i + 1)          # 0 开始的 index → 1 开始的页码
    doc.close()
    return 命中


# --- 任务 5 ---
def 任务5_找扫描页():
    doc = pymupdf.open(扫描素材)
    扫描页 = []
    for i in range(50):                # 只扫前 50 页
        if len(doc[i].get_text().strip()) == 0:
            扫描页.append(i + 1)
    doc.close()
    return 扫描页


# --- 任务 6 ---
def 任务6_存进数据库():
    if 库文件.exists():
        库文件.unlink()                # 先删旧的，保证每次结果一样
    doc = pymupdf.open(主素材)
    con = sqlite3.connect(库文件)
    cur = con.cursor()
    cur.execute("CREATE TABLE 页文本 (页码 INTEGER, 文字 TEXT)")
    for i in range(doc.page_count):
        cur.execute("INSERT INTO 页文本 (页码, 文字) VALUES (?, ?)",
                    (i + 1, doc[i].get_text()))
    con.commit()
    行数 = cur.execute("SELECT COUNT(*) FROM 页文本").fetchone()[0]
    con.close()
    doc.close()
    return 行数
'''
