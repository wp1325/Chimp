Debug
---
```python
  #修改前
  f.write(struct.pack("B", data[i+1]))  # 写入下一个字符数据 1字节
  #修改后
  f.write(struct.pack("B", data[i+match_length]))  # 写入下一个字符数据 1字节
```
只考虑了单字符引用的情况，导致在长引用时

设置的max_length并没有正确的对引用长度进行约束 导致后续在写入时引用不完全而导致有数据缺失
```python
    #修改前
    while i < len(data):
        match_distance = 0  # 查找到的前序索引
        match_length = 0  # 引用长度
        char = data[i]
        start_index = max(0, i - window_size)  # 确保得到滑动窗口的起始位置
        for j in range(start_index, i):
            length = 0
            while (i + length < len(data)) and data[j + length] == data[i + length]:
                length += 1
            if j + length >= i:  # 防止越界
                break
            if length > match_length:
                match_distance = i - j
                match_length = length
            if length >= max_length:
                break  #此时match_length 已被设置为越界值

    #修改后
    if match_length < length <= max_length:         #防止越界 同时防止引用过长在后续写入时溢出
        match_distance = i - j
        match_length = length
```