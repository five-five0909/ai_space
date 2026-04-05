# 集合 API

## 基础操作

```python
# 创建集合
s = {1, 2, 3}
s = set([1, 2, 3])
empty = set()  # 不能用 {}，那是空字典

# 添加/删除
s.add(4)
s.remove(4)     # 不存在会报错
s.discard(4)    # 不存在不报错
s.pop()         # 随机弹出一个

# 集合运算
a = {1, 2, 3}
b = {2, 3, 4}

a | b   # 并集：{1, 2, 3, 4}
a & b   # 交集：{2, 3}
a - b   # 差集：{1}
a ^ b   # 对称差集：{1, 4}
```

## LeetCode 实战场景

### 1. 两数之和 (LC 1)

```python
def two_sum(nums: list, target: int) -> list:
    seen = set()
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [nums.index(complement), i]
        seen.add(num)
```

### 2. 存在重复元素 (LC 217)

```python
def contains_duplicate(nums: list) -> bool:
    return len(nums) != len(set(nums))
```

### 3. 两个数组的交集 (LC 349)

```python
def intersection(nums1: list, nums2: list) -> list:
    return list(set(nums1) & set(nums2))
```

### 4. 快乐数 (LC 202)

```python
def is_happy(n: int) -> bool:
    seen = set()

    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))

    return n == 1
```

### 5. 有效的数独 (LC 36)

```python
def isValidSudoku(board: list) -> bool:
    seen = set()
    for i in range(9):
        for j in range(9):
            num = board[i][j]
            if num != '.':
                box = (i // 3, j // 3, num)
                row = ('row', i, num)
                col = ('col', j, num)
                if seen & {box, row, col}:
                    return False
                seen |= {box, row, col}
    return True
```

## 科研实战场景

### 1. 去重数据集

```python
def deduplicate_dataset(samples: list) -> list:
    seen = set()
    unique = []
    for s in samples:
        s_hash = hash(str(s))
        if s_hash not in seen:
            seen.add(s_hash)
            unique.append(s)
    return unique
```

### 2. 词汇表构建

```python
def build_vocab(texts: list) -> set:
    vocab = set()
    for text in texts:
        vocab.update(text.lower().split())
    return vocab
```

### 3. 检查数据泄露

```python
def check_data_leak(train_ids: list, test_ids: list) -> bool:
    leak = set(train_ids) & set(test_ids)
    if leak:
        print(f"发现 {len(leak)} 个样本泄露")
        return True
    return False
```

## frozenset (不可变集合)

```python
# frozenset 可哈希，可作为字典键
fs = frozenset([1, 2, 3])
d = {fs: "value"}  # OK

# 用于需要不可变集合的场景
config_options = frozenset(['option1', 'option2', 'option3'])
```

## 性能提示

- `in` 操作：O(1) 平均时间复杂度
- 去重操作首选 set
- 大集合交集使用 `&` 操作符
