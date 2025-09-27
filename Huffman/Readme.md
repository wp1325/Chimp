# 实现了通过Huffman编码对文件进行压缩
---
Huffman_compression.py    ----主程序，完成了Huffman编码的代码实现 同时定义了zip_file与unzip_file 两个主要的压缩与解压缩的函数接口</br>
zip.py---- 提供了命令行的操作界面，让使用者能够直接通过命令行输入的形式对文件进行压缩 默认输出文件为xxxx.huff格式(例如压缩test.txt文件 输出 test.huff文件 后续解压时需要对huff文件进行操作)
```
python zip.py xxxxxx.txt(需要压缩的文件路径)
```
unzip.py---- 提供了命令行的操作界面，让使用者能够直接通过命令行输入的形式对文件进行解压 需要输入解压的huff格式文件路径与输出文件的文件名
```
python unzip.py xxxxxx.huff(需要解压的文件路径) xxxxxx.xxx(解压完成后输出的文件名及其格式)
```

Huffman_compression.py
---

```python
class Node:
    #定义哈夫曼树的节点
    def __init__(self, byte, freq):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None
    #对比两个节点之间的权重
    def __lt__(self, other):
        return self.freq < other.freq
    #判断该节点是否是叶节点（没有任何子节点）
    def is_leaf(self):
        return self.left is None and self.right is None
    # 统计字节频率  用于后续哈夫曼树的构筑
    def count_freq(data: bytes):
        freqs = {}              #生成字典用于存储各字节的出现频率
        for b in data:
            freqs[b] = freqs.get(b, 0) + 1      #get方法返回b字节出现的频率并进行累加计数，如果没有找到默认返回0
        return freqs
        # 构建哈夫曼树
    def build_tree(freqs: dict):
        heap = [Node(byte, freq) for byte, freq in freqs.items()]
        # 调用heapq中的heapify方法搭建小根堆（堆顶元素最小）
        heapq.heapify(heap)
        #对小根堆进行操作 构建哈夫曼树
        while len(heap) > 1:
            n1 = heapq.heappop(heap)
            n2 = heapq.heappop(heap)
            new_node = Node(None, n1.freq + n2.freq)
            new_node.left = n1
            new_node.right = n2
            heapq.heappush(heap, new_node)

        return heap[0]
    # 生成编码表
    def generate_codes(node, prefix="", codes=None):
        if codes is None:
            codes = {}
        if node.is_leaf():
            codes[node.byte] = prefix
        else:
            generate_codes(node.left, prefix + "0", codes)
            generate_codes(node.right, prefix + "1", codes)
        return codes
    # 将编码表转换为二进制格式
    def encode_dict(codes):
        """
        将哈夫曼编码表序列化为二进制数据
        格式：
        [字符(1字节)][编码长度(1字节)][编码内容(若干字节)]
        """
        dict_bytes = bytearray()            #创建可变字节数组
        for byte, code in codes.items():
            code_len = len(code)
            dict_bytes.append(byte)          # 字节值
            dict_bytes.append(code_len)      # 编码长度

            # 按8位打包
            for i in range(0, code_len, 8):
                chunk = code[i:i+8]
                dict_bytes.append(int(chunk.ljust(8, "0"), 2))  # 不足补0（ljust函数实现）
        return dict_bytes


    def decode_dict(dict_bytes):
    """
    从二进制数据解析出哈夫曼编码表
    """
    codes = {}
    i = 0
    while i < len(dict_bytes):
        byte = dict_bytes[i]
        code_len = dict_bytes[i + 1]
        i += 2

        bits = ""
        for _ in range((code_len + 7) // 8):  # 需要多少字节存储
            bits += f"{dict_bytes[i]:08b}"
            i += 1

        codes[byte] = bits[:code_len]  # 截取有效长度
    return codes

    # 压缩函数
    def zip_file(infile: str, outfile: str):
        #输入压缩文件的路径以及压缩后输出文件的文件名作为参数9
        with open(infile, "rb") as f:
            data = f.read()

        freqs = count_freq(data)
        root = build_tree(freqs)
        codes = generate_codes(root)

        # 编码数据
        bitstring = "".join(codes[b] for b in data)

        # 计算填充位数（保证 bitstring 长度是 8 的倍数）
        padding = (8 - len(bitstring) % 8) % 8
        bitstring += "0" * padding

        # 转换为字节
        compressed_data = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = int(bitstring[i:i+8], 2)
            compressed_data.append(byte)

        # 编码字典
        dict_bytes = encode_dict(codes)

        # 保存压缩文件
        with open(outfile, "wb") as f:
            # 1. 写入 padding 信息（1 字节） B代表1字节无符号整数
            f.write(struct.pack("B", padding))
            # 2. 写入字典长度（4 字节） I代表1字节无符号整数
            f.write(struct.pack("I", len(dict_bytes)))
            # 3. 写入字典内容（压缩字典）
            f.write(dict_bytes)
            # 4. 写入压缩数据
            f.write(compressed_data)



```