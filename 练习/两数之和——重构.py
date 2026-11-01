# 两数之和 · 第二版（重构版）
# 2026-10-27 写 · 2026-11-01 补说明
#
# ---------------------------------------------------------------
# 📌 这个文件和「两数之和.py」是【同题的两个版本】，两个都保留：
#
#   两数之和.py          → 第一版：朴素双循环，看得懂核心思路
#                          （原代码 + 修正版并列，11-01 批改过）
#   两数之和——重构.py    → 第二版（就是本文件）：在第一版基础上加了
#                          防御 + max_pairs + 异常处理
#
#   为什么留两个而不是合成一个？
#     面试时能讲清「我先写了朴素版，再逐步加固」，
#     比只甩一个最终版更有说服力 —— 你能说清每一步为什么加。
#
#   本文件比第一版多做了 4 件事：
#     ① 防御：nums 不是列表 / target 不是数字 → 返回人话，不崩
#     ② max_pairs：默认只找 1 对，可以改成找 N 对 / 找全部
#     ③ result 当容器用：找到就往里塞，不立刻 return（这样才能找多对）
#     ④ except TypeError：列表里有非数字 → 返回人话
#
#   ⚠️ 注意 ③ 和第一版的差别：
#      第一版找到就 print 然后继续循环 → 天然能找到全部
#      这一版找到就 return → 只能找到一对，所以必须改成「塞进 result」
#      再用 max_pairs 控制什么时候停。这就是 E27「同一段逻辑只写一份」。
#
#   📌 下一版可以往哪走：哈希表解法 O(n)（两数之和的官方最优解是 O(n)），
#      和「和为 K 的子数组」的前缀和+字典是同一个家族。
# ---------------------------------------------------------------

def two_sum(nums, target, max_pairs=1):
    """
    在 nums 中找和为 target 的两两组合，返回下标对列表。
    - max_pairs=1（默认）：找到 1 对就停
    - max_pairs=N：找前 N 对
    - max_pairs=None：找所有对
    返回：[(i,j), ...] 列表；找不到返回 []
    """
    # 防御（沿用 ②）
    if not isinstance(nums, list):
        return "错误：nums 必须是列表"
    if not isinstance(target, (int, float)):
        return "错误：target 必须是数字"

    # 升级点：result 当容器用
    result = []
    try:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    result.append((i, j))  # ← 改 ①：塞进 result，不立刻 return
                    if max_pairs is not None and len(result) >= max_pairs:  # ← 改 ③
                        return result  # ← 满 N 对就 break 出来
    except TypeError:
        return "错误：列表里有非数字元素"

    return result  # ← 改 ④：找不到就是 []


# 测试
print(two_sum([1, 2, 3, 4, 5], 6, max_pairs=1))  # 期望 [(0, 4)]
print(two_sum([1, 2, 3, 4, 5], 6, max_pairs=2))  # 期望 [(0, 4), (1, 3)]
print(two_sum([1, 2, 3, 4, 5], 6, max_pairs=None))  # 期望 [(0, 4), (1, 3)]
print(two_sum([3, 3, 3, 3], 6, max_pairs=None))  # 期望 [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
print(two_sum([1, 2, 3], 100, max_pairs=2))  # 期望 []
print(two_sum([], 5))  # 期望 []


