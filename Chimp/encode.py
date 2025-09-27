# Chimp压缩算法的压缩部分
import time

import segyio
from bitstring import BitStream, BitArray, Bits
import bitstring

from chimp_compression import leading_zero,tail_zero,meaningful_bit,meaningful_bit_length,find_max_leq,non_leadingzero_bit

spacial_list=[0,5,6,7,8,9,10,11]                #用于压缩前导0的特殊值
# data:传入的浮点数数组数据
def encode(data):
    stream=BitStream() #用于存储压缩结果
    # 四类情况统计
    '''
    count_00=0
    count_01=0
    count_11=0
    count_10=0

    bit_10=0
    bit_11=0
    bit_01=0
    '''
    zero_leading=0
    finished_count=0        #统计已经完成处理的数据数量

    #首数不处理 直接保存
    pre_value = bitstring.pack("float:32", data[0])
    stream.append(pre_value)
    pre_leading = 32

    for member_float in data[1:]:
        current_value = bitstring.pack("float:32", member_float)
        # 取异或运算结果
        '''
        print(f"No{finished_count}")
        print(member_float)
        print(f"{pre_value.float}^{current_value.float}")
        print(f"{pre_value.bin}^{current_value.bin}")
        '''
        xor_result = current_value^pre_value
        # print(f"异或结果:{xor_result.bin}")
        # 计算异或结果的前导0和尾随0
        current_leading = leading_zero(xor_result)

        current_tail=tail_zero(xor_result)
        # print(f"前导0:{current_leading}  尾随0:{current_tail}")
        if current_tail>5:                                                    # 尾0大于5的情况    写入0
            stream.append(Bits("0b0"))
            if current_tail==32:             #全为0的情况 此数与前数相同 写入00（情况1）
                stream.append(Bits("0b0"))
                # count_00=count_00+1
                # print("写入00(标志位) 长度:2")
            else:                                                               #与前数不相同 写入01（情况2）
                stream.append(Bits("0b1"))
                # count_01=count_01+1
                #计算最靠近前导0的特殊值和其索引
                spacial_val,index=find_max_leq(current_leading,spacial_list)
                stream.append(bitstring.pack("uint:3", index))            # 写入三位的前导0特殊值索引
                stream.append(bitstring.pack("uint:5", meaningful_bit_length(xor_result)+current_leading-spacial_val))          # 超出特殊值的前导0部分一块写入
                stream.append([0] * (current_leading-spacial_val) + meaningful_bit(xor_result))
                pre_leading = spacial_val
                # print(f"写入01(标志位)+{bitstring.pack("uint:3", index).bin}(前导0特殊值)+{bitstring.pack("uint:5", meaningful_bit_length(xor_result)+current_leading-spacial_val).bin}(有效部分长度)+{([0] * (current_leading-spacial_val) + meaningful_bit(xor_result)).bin}(有效部分) 长度:{10+len(([0] * (current_leading-spacial_val) + meaningful_bit(xor_result)))}")
                # bit_01=bit_01+10+len(([0] * (current_leading-spacial_val) + meaningful_bit(xor_result)))
        else:                                       # 尾0小于5的情况    写入1
            stream.append(Bits("0b1"))
            if current_leading == pre_leading:      # 如果与前一结果前导0相同 写入10(情况3)
                stream.append(Bits("0b0"))
                # count_10=count_10+1
                stream.append((non_leadingzero_bit(xor_result)))            # 写入不含前导0的部分
                # print(f"写入10(标志位)+{non_leadingzero_bit(xor_result).bin}(除前导0部分) 长度:{2+len(non_leadingzero_bit(xor_result))}")
                # bit_10=bit_10+(2+len(non_leadingzero_bit(xor_result)))
            else:                                   # 如果与前一结果前导0不同 写入11(情况4)
                stream.append(Bits("0b1"))
                # count_11=count_11+1
                spacial_val, index = find_max_leq(current_leading, spacial_list)                                # 写入最靠近的前导0特殊值的索引
                stream.append(bitstring.pack("uint:3", index))
                stream.append([0] * (current_leading - spacial_val) + non_leadingzero_bit(xor_result))          # 写入不含前导0的部分
                pre_leading=spacial_val
                # print(f"写入11(标志位)+{bitstring.pack("uint:3", index).bin}(前导0特殊值)+{([0] * (current_leading - spacial_val) + non_leadingzero_bit(xor_result)).bin}(除前导0部分) 长度:{5+len(([0] * (current_leading - spacial_val) + non_leadingzero_bit(xor_result)))}")
                # bit_11=bit_11+(5+len(([0] * (current_leading - spacial_val) + non_leadingzero_bit(xor_result))))
        pre_value=current_value
        finished_count = finished_count + 1
        if finished_count % 1000 == 0:
             print(f"处理了{finished_count}个数据")
    '''
    print(f"count_00 频次:{count_00} 平均bit:{2}")
    print(f"count_01 频次:{count_01} 平均bit:{bit_01/count_01}" )
    print(f"count_10 频次:{count_10} 平均bit:{bit_10/count_10}")
    print(f"count_11 频次:{count_11} 平均bit:{bit_11/count_11}")
    print(f"前导0为0的次数:{zero_leading}")
    '''
    return stream

def test_encode(data):
    # 测试数据：一组浮点数

    # 调用编码函数
    data_len=len(data)
    compressed_stream = BitStream()

    # 写入数据长度
    compressed_stream.append(bitstring.pack("uint:48", data_len))

    # 写入编码后的数据
    compressed_stream.append(encode(data))

    # 输出压缩结果：以二进制字符串表示
    print("压缩结果（比特流）：")
    print(len(compressed_stream))
    print("压缩率:")
    print(len(compressed_stream)/(32*len(data)))
    with open("compressed.chimp", "wb") as f:
        compressed_stream.tofile(f)
    print("压缩结果已保存为compressed.chimp")



with segyio.open("test.segy", "r", ignore_geometry=True) as f:
    # 读取所有 trace
    traces = [trace.tolist() for trace in f.trace]

with segyio.open("test.segy", "r", ignore_geometry=True) as f:
    first_trace = f.trace[0]          # 第一条道（返回的是 numpy.ndarray）
    first_trace_list = first_trace.tolist()  # 如果需要 Python 列表
# 如果需要展开成一维列表
b_time=time.time()
flatten_data = [x for tr in traces for x in tr]
test_encode(flatten_data[0:1000000])
e_time=time.time()
print(f"用时:{e_time-b_time}s")
