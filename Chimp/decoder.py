# Chimp压缩算法的解压部分
from bitstring import ConstBitStream
import bitstring

from Chimp.chimp_compression import leading_zero

spacial_list=[0,5,6,7,8,9,10,11]                #用于压缩前导0的特殊值


def decode(infile:str,outfile:str):
    # 读取待解压内容
    with open(infile, "rb") as f:
        compressed = f.read()
    bitstream = ConstBitStream(bytes=compressed)
    # 存储解压结果的字节数组
    # 读取总浮点数数量
    data_len_bit=bitstream.read(48)
    data_len = int(data_len_bit.bin, 2)

    first_value =bitstream.read(32)
    data = bytearray(first_value.bytes)
    prev_value=first_value
    prev_l_z=0
    i=1
    print(f"No.{i}:",first_value.float)
    try:
        while i<data_len:

            flag=bitstream.read(2)
            if flag=='0b00':            # 标志位为00 说明与前数相等
                current_value=prev_value
            elif flag=='0b01':
                # 读取前导0索引与有效部位长度 并转换为整数
                l_z_bit=bitstream.read(3)
                center_count_bit=bitstream.read(5)
                l_z = int(l_z_bit.bin, 2)
                center_count=int(center_count_bit.bin,2)
                center_bit=bitstream.read(center_count)
                full_bit=[0]*spacial_list[l_z]+center_bit+[0]*(32-spacial_list[l_z]-center_count)
                prev_l_z=spacial_list[l_z]
                current_value=prev_value^full_bit

            elif flag=='0b10':
                center_count = 32-prev_l_z
                center_bit = bitstream.read(center_count)
                full_bit = ([0] * prev_l_z + center_bit)
                current_value = prev_value ^ full_bit

            else:
                l_z_bit=bitstream.read(3)
                l_z = int(l_z_bit.bin, 2)
                center_count = 32 - spacial_list[l_z]
                center_bit = bitstream.read(center_count)
                full_bit = ([0] * spacial_list[l_z] + center_bit)
                current_value = prev_value ^ full_bit
                prev_l_z=spacial_list[l_z]
            data.extend(current_value.bytes)
            prev_value=current_value
            i=i+1
            print(f"No.{i}:", current_value.float)
        with open(outfile,"wb")as f:
            f.write(data)

    except Exception as error:
        print(f"在第{i}个值出错")
decode("compressed.chimp","out.bin")