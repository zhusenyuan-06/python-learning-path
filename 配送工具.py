def 生成配送单(园所名, *菜单, **附加):
    print("园所:", 园所名)
    print("菜单:", ", ".join(菜单))
    for 键, 值 in 附加.items():
        print(键 + ":", 值)
