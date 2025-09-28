import time

import segyio
from bitstring import BitStream, BitArray, Bits
import bitstring
spacial_list=[0,5,6,7,8,9,10,11]                #用于压缩前导0的特殊值

# 求先导零 leading_zero
def leading_zero(ba):
    l_z = 0
    # 限制最大32，避免越界
    while l_z < 32 and l_z < len(ba) and ba[l_z] != 1:
        l_z += 1
    return l_z

def tail_zero(ba):
    t_z = 0
    idx = len(ba) - 1
    # 限制最多32，避免越界
    while idx >= 0 and t_z < 32 and ba[idx] != 1:
        t_z += 1
        idx -= 1
    return t_z

# 求有效部分的长度 meaningful_bit_length
def meaningful_bit_length(ba):
    l_z = leading_zero(ba)
    t_z = tail_zero(ba)
    return len(ba) - l_z - t_z

# 求有效部分实际内容 meaningful_bit
def meaningful_bit(ba):
    l_z = leading_zero(ba)
    t_z = tail_zero(ba)
    m_b = ba[l_z:len(ba)-(t_z)]
    return m_b
# 寻找特殊值列表中不大于前导0的数中的最大值
def find_max_leq(target, nums):
    max_val = None
    index = -1

    for i, val in enumerate(nums):
        if val <= target:
            if max_val is None or val > max_val:
                max_val = val
                index = i

    return max_val, index


def non_leadingzero_bit(ba):
    l_z = leading_zero(ba)
    nz_b=ba[l_z:]
    return nz_b



