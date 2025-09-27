# 在这里实现Lz77压缩算法
import struct
import time

#压缩端口    引用距离[12位] 引用长度[4位] 字符内容[8位]

import struct

def zip_lz77(infile: str, outfile: str):
    with open(infile, "rb") as i:
        data = i.read()
    f = open(outfile, "wb")

    max_length = 15                 #最大引用长度
    window_size = 4095              #滑动窗口长度
    i = 0

    while i < len(data):
        match_distance = 0         #匹配到的前序索引
        match_length = 0           #引用长度
        start_index = max(0, i - window_size)           #确保滑动窗口起始端不小于0

        for j in range(start_index, i):
            length = 0
            while (i + length < len(data)) and data[j + length] == data[i + length]:
                length += 1
                if j + length >= i:     #防止越界
                    break
            if match_length < length <= max_length:         #防止越界 同时防止引用过长在后续写入时溢出
                match_distance = i - j
                match_length = length


        combined = (match_distance << 4) | (match_length & 0xF)             #拼接引用距离和引用长度
        f.write(struct.pack("<H", combined))                        #写入两字节的引用信息

        if i + match_length < len(data):
            f.write(struct.pack("B", data[i + match_length]))        #当无引用 match_length==0 写入当前字符   当有引用 写入引用后一位字符
        else:
            f.write(struct.pack("B", 0))                             # 末尾补零

        i += max(1, match_length + 1)

    f.close()

#解压端口


def unzip_lz77(infile: str, outfile: str):
    with open(infile, "rb") as f:
        compressed = f.read()

    data = bytearray()
    i = 0
    while i < len(compressed):
        #读取token
        token = struct.unpack_from("<H", compressed, i)[0]
        i += 2
        # 还原引用距离和引用长度
        distance = token >> 4
        length = token & 0xF

        start = len(data) - distance
        for j in range(length):
            data.append(data[start + j])

        char = struct.unpack_from("B", compressed, i)[0]
        i += 1
        data.append(char)

    data.pop()                      #删去末位零 保持压缩前后文件一致性
    with open(outfile, "wb") as f:
        f.write(data)

    return data

s_time=time.time()
zip_lz77("trace.huff","trace.lz7")
# unzip_lz77("nov.lz7","nov.txt")
e_time=time.time()
print(e_time-s_time)
print("finish")
