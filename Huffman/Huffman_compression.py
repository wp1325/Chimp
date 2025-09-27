import heapq
import struct

# 定义哈夫曼树节点
class Node:
    def __init__(self, byte, freq):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def is_leaf(self):
        return self.left is None and self.right is None


# 统计字节频率
def count_freq(data: bytes):
    freqs = {}
    for b in data:
        freqs[b] = freqs.get(b, 0) + 1
    return freqs


# 构建哈夫曼树
def build_tree(freqs: dict):
    heap = [Node(byte, freq) for byte, freq in freqs.items()]
    heapq.heapify(heap)

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
    dict_bytes = bytearray()
    for byte, code in codes.items():
        code_len = len(code)
        dict_bytes.append(byte)          # 字节值
        dict_bytes.append(code_len)      # 编码长度

        # 按8位打包
        for i in range(0, code_len, 8):  #编码内容
            chunk = code[i:i+8]
            dict_bytes.append(int(chunk.ljust(8, "0"), 2))  # 不足补0
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
        # 1. 写入 padding 信息（1 字节）
        f.write(struct.pack("B", padding))
        # 2. 写入字典长度（4 字节）
        f.write(struct.pack("I", len(dict_bytes)))
        # 3. 写入字典内容（压缩字典）
        f.write(dict_bytes)
        # 4. 写入压缩数据
        f.write(compressed_data)


# 解压函数
def unzip_file(infile: str, outfile: str):
    with open(infile, "rb") as f:
        # 1. 读取 padding 信息
        padding = struct.unpack("B", f.read(1))[0]
        # 2. 读取字典长度
        dict_len = struct.unpack("I", f.read(4))[0]
        # 3. 读取字典内容
        dict_bytes = f.read(dict_len)
        codes = decode_dict(dict_bytes)

        # 反转字典（编码 -> 字节）
        reverse_codes = {v: k for k, v in codes.items()}

        # 4. 读取压缩数据
        compressed_data = f.read()
        bitstring = "".join(f"{byte:08b}" for byte in compressed_data)
        bitstring = bitstring[:-padding] if padding > 0 else bitstring

    # 解码
    decoded_bytes = bytearray()
    buffer = ""
    for bit in bitstring:
        buffer += bit
        if buffer in reverse_codes:
            decoded_bytes.append(reverse_codes[buffer])
            buffer = ""

    # 写入解压结果
    with open(outfile, "wb") as f:
        f.write(decoded_bytes)
