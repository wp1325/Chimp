import time

import segyio
from bitstring import BitStream, BitArray, Bits
import bitstring
import random
# 求先导零 leading_zero
def leading_zero(ba):
    l_z = 0
    while ba[l_z] != 1:
        l_z = l_z + 1
    return l_z

# 求尾零 tail_zero
def tail_zero(ba):
    t_z = len(ba) - 1
    while ba[t_z] != 1:
        t_z = t_z - 1
    return t_z

# 求有效部分的长度 meaningful_bit_length
def meaningful_bit_length(ba):
    l_z = leading_zero(ba)
    t_z = tail_zero(ba)
    m_b_l = len(ba) - l_z - (len(ba) - t_z - 1)
    return m_b_l

# 求有效部分实际内容 meaningful_bit
def meaningful_bit(ba):
    l_z = leading_zero(ba)
    t_z = tail_zero(ba)
    m_b = ba[l_z:t_z + 1]
    return m_b

# 编码函数 input为传入的float浮点数数组
def encode(input):
    stream = BitStream()  # 用于存储输出结果
    count_0=0
    count_11=0
    count_10=0
    i=0
    # 保存第一个值
    pre_value = bitstring.pack("float:32", input[0])
    stream.append(pre_value)
    pre_leading = 32
    pre_tail = 0

    for member_float in input[1:]:
        current_value = bitstring.pack("float:32", member_float)
        # 取异或运算结果
        xor_result = BitArray(bytes=current_value.bytes) ^ BitArray(bytes=pre_value.bytes)

        # 如果运算结果为 0 --------> 两数相等 存入0标志位
        if xor_result.bytes == b'\x00' * len(xor_result.bytes):
            stream.append(Bits("0b0"))
            count_0=count_0+1
        else:
            current_leading = leading_zero(xor_result)
            current_tail = tail_zero(xor_result)

            if current_leading >= pre_leading and current_tail == pre_tail:
                stream.append(Bits("0b10"))
                stream.append(meaningful_bit(xor_result))
                count_10=count_10+1

            else:
                stream.append(Bits("0b11"))
                count_11=count_11+1
                if current_leading>15:
                    stream.append(bitstring.pack("uint:4", 15))
                    stream.append(bitstring.pack("uint:5", meaningful_bit_length(xor_result)+current_leading-15))
                    stream.append([0]*(current_leading-15)+meaningful_bit(xor_result))
                    current_leading=15
                else:
                    stream.append(bitstring.pack("uint:4", current_leading))
                    stream.append(bitstring.pack("uint:5", meaningful_bit_length(xor_result)))
                    stream.append(meaningful_bit(xor_result))
                pre_leading = current_leading
                pre_tail = current_tail
        pre_value = current_value
        i=i+1
        if i%1000==0:
            print(f"处理了{i}个数据")
    print("count_0:"+str(count_0))
    print("count_11:" + str(count_11))
    print("count_10:" + str(count_10))
    return stream

# 生成测试函数，打印压缩结果
def test_encode(data):
    # 测试数据：一组浮点数

    # 调用编码函数
    compressed_stream = encode(data)

    # 输出压缩结果：以二进制字符串表示
    print("压缩结果（比特流）：")
    print(len(compressed_stream))
    print("压缩率:")
    print(len(compressed_stream)/(32*len(data)))
    '''
    if len(compressed_stream) % 8 != 0:
        padding = 8 - (len(compressed_stream) % 8)
        compressed_stream.append('0b' + '0' * padding)
    '''

filename="test.segy"
with segyio.open(filename, "r", ignore_geometry=True) as f:
    # 读取所有 trace
    traces = [trace.tolist() for trace in f.trace]

# 如果需要展开成一维列表
flatten_data = [x for tr in traces for x in tr]
b_time=time.time()

test_encode(flatten_data[0:100000])

e_time=time.time()
print(f"用时:{e_time-b_time}s")