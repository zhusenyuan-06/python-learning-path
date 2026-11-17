# -*- coding: utf-8 -*-
"""修正 T53 + 新增 T55（POST 探针结论与 git 实推结论【双向】可能不一致）"""
import json
import datetime
from pathlib import Path

坑文件 = Path(r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject/笔记/工具链/工具链坑.json')

d = json.loads(坑文件.read_text(encoding='utf-8'))
按id = {it['id']: it for it in d['items']}
print('原有条数:', len(d['items']))

# ---- 修正 T53：补上双向不一致的实证 ----
t53 = 按id['T53']
t53['教训'] = ('⛔ 「curl 通」和「git 通」是两个独立事实，而且【双向】都会不一致：'
               'curl 报 000 的 IP，git 实推反而能连上；curl 报 200 的 IP，git 实推连不上 ⛔ '
               '换 IP 之前先把两种客户端的表现都摆出来')
t53['怎么防'] = ('① POST 探针只当【候选排序参考】，不是判据 —— 200 只说明「认证这条路通」，'
                 '不代表 git 能连上该机器（T55）② 最终必须 git 实推，且候选要逐个试过（T23）'
                 '③ git 侧失败时先比状态码矩阵，别把「curl 通但 git 不通」等同于「IP 不可用」')
t53['实测结果'] = ('2026-11-17 三轮实测：19:35 探针 20.27.177.113/20.200.245.247/4.237.22.38 全 200 → '
                   'git 绑 20.27.177.113 一次推成功；19:4x 同样三个 IP 探针全 000（窗口轮换）；'
                   '19:47 探针 20.200.245.247→200 但 git 绑它连不上 21 秒，'
                   '而探针判死（000）的 20.27.177.113 却被 git 一次推成功')
print('✅ 修正 T53')

新坑 = {
    'id': 'T55',
    'title': 'POST 探针的 200 ≠ 能 push —— 探针结论只作排序参考，最终判据只有 git 实推',
    'hits': 1,
    'severity': '中',
    '场景': '2026-11-17 用新增的 POST 探针（工具/push_post_probe.py）替代逐个 git push 试错',
    '现象': '探针说 20.200.245.247「认证通过·可 push」（200），git 绑它却 21 秒连不上；'
            '探针说 20.27.177.113「链路不通」（000），git 绑它一次就推成功',
    '原因': '探针（curl）和 git（自带 libcurl）是两套 TLS/HTTP 栈，校园网/运营商链路对两者的干扰窗口不一致；'
            '再加上可达集合在分钟级轮换（T20），探针结果天然会过期',
    '教训': '⛔ 别把探针的 200 写成「可 push」的结论 —— T52 的判读表要加一句「必要非充分」⛔ '
            '「探针判死的 IP」里往往藏着唯一能用的那个',
    '怎么防': '① 探针输出只写「认证通过·候选优先」，别写「可 push」② push 循环必须把【所有候选】都试过（T23）'
              '③ 判据仍然是 T30 的主判据：git push 退出码 0 + "<old>..<new>  main -> main"',
    '发现时间': '2026-11-17',
}

added = 0
if 新坑['id'] in 按id:
    print('跳过已存在:', 新坑['id'])
else:
    d['items'].append(新坑)
    added = 1
    print('✅ 写入', 新坑['id'], 新坑['title'][:44])

d['updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
坑文件.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print('新增 %d 条，现共 %d 条' % (added, len(d['items'])))
