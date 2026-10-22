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


