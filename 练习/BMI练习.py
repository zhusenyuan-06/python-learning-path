def bmi(weight_kg, height_m):
    """BMI = 体重(kg) / 身高(m)²"""

    # ① 顶部 isinstance 验类型（坑 28）
    if not isinstance(weight_kg, (int, float)):
        return "错误：weight_kg 必须是数字"
    if not isinstance(height_m, (int, float)):
        return "错误：height_m 必须是数字"

    # ② try/except 包裹核心计算（坑 26）
    try:
        if height_m <= 0:
            raise ValueError("身高必须 > 0")
        else:
            return weight_kg / (height_m ** 2)   # ← 你来填（一行 return，用 BMI 公式）
    except (ValueError, ZeroDivisionError) as e:
        return f"错误：{e}"


# ③ 文件底部调用 + 4 个测试（坑 25 + 坑 27 启动）
print(bmi(70, 1.75))  # 期望 ≈ 22.86（完整 22.857142857...）
print(bmi("abc", 1.75))  # 期望 错误：weight_kg 必须是数字
print(bmi(60, 0))  # 期望 错误：身高必须 > 0
print(bmi(60, -1.7))  # 期望 错误：身高必须 > 0



def 看(*数字):
    print(数字)

看([1, 2, 3])     # 输出什么？
看(1, 2, 3)       # 输出什么？

数字们 = [1, 2, 3]
看(*数字们)       # 输出什么？为什么和 ③ 的第一行不一样？


