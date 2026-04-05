# Python 2 vs Python 3

> 注意：Python 2 已于 2020 年停止支持，本文档仅供了解历史差异。

## 主要差异

### 1. print 语句

```python
# Python 2
print "Hello"

# Python 3
print("Hello")
```

### 2. 整数除法

```python
# Python 2
5 / 2  # 2 (整数除法)

# Python 3
5 / 2   # 2.5 (浮点除法)
5 // 2  # 2 (整数除法)
```

### 3. 字符串和 Unicode

```python
# Python 2
s = "hello"      # str (ASCII)
u = u"hello"     # unicode

# Python 3
s = "hello"      # str (Unicode)
b = b"hello"     # bytes
```

### 4. xrange vs range

```python
# Python 2
for i in xrange(1000):  # 惰性求值
    pass

# Python 3
for i in range(1000):  # range 已经是惰性求值
    pass
```

### 5. 异常处理

```python
# Python 2
try:
    pass
except Exception, e:
    pass

# Python 3
try:
    pass
except Exception as e:
    pass
```

## 结论

始终使用 Python 3。所有现代 Python 库和框架都已迁移到 Python 3。
