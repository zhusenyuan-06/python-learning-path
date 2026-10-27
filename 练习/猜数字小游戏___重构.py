import random

#times = 0
#s = random.randint(1,90)
#print('我生成了一一个1~90的数字')

#while True:
#    times +=1
#    g = int(input('你的猜测：'))

#    if g>s:
#        print('大了')
#    elif g<s:
#        print(
#            '小了'
#        )
#    else:
#        print('对了')
#        break


def make_answer():
    """随机生成 1~100 的整数答案"""
    return random.randint(1, 100)   # ← 写"return"、不写"print"


def judge(guess, answer):
    """比大小：返回 '大了' / '小了' / '对了'"""
    if guess > answer:
        return "大了"
    elif guess < answer:
        return "小了"
    else:
        return "对了"


def read_guess():
    """从用户读一个合法整数，return 出去（如果输入非法就一直问）"""
    while True:
        s = input("你的猜测：")
        try:
            return int(s)        # 转得成整数就 return 出去
        except ValueError:
            print("请输入整数！")


def play():
    """主游戏循环：生成答案 → 反复读猜测 → 比大小 → 对了就 break"""
    answer = make_answer()  # 1. 先出答案
    times = 0  # 2. 计数器（接老版本的 times）
    print("我生成了一个 1~100 的数字，开始猜！")

    while True:
        g = read_guess()  # 3. 拿合法整数（这里会真的等用户输入）
        times += 1  # 4. 计数

        result = judge(g, answer)  # 5. 比大小 → return '大了'/'小了'/'对了'
        print(result)  # 6. 把判断结果显示给用户

        if result == "对了":  # 7. 对了就退出
            print(f"猜对了！共猜了 {times} 次")
            break


# 启动游戏（这是唯一一句"调用"，让 play() 真正跑起来）
play()