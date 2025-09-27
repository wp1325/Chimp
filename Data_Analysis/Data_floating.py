# 统计测试数据中前导0和尾随0的结果

import struct
from collections import Counter

import segyio


def float_to_bits32(f: float) -> int:
    """将 float 转成 32 位二进制整数表示 (IEEE 754 单精度)"""
    return struct.unpack('>I', struct.pack('>f', f))[0]

def count_leading_zeros(x: int, bits=32) -> int:
    """统计前导零"""
    if x == 0:
        return bits
    return bits - x.bit_length()

def count_trailing_zeros(x: int, bits=32) -> int:
    """统计尾随零"""
    if x == 0:
        return bits
    tz = 0
    while x & 1 == 0:
        tz += 1
        x >>= 1
    return tz

def analyze_floats32_distribution(arr):
    lz_dist = Counter()
    tz_dist = Counter()
    for i in range(1, len(arr)):
        a_bits = float_to_bits32(arr[i-1])
        b_bits = float_to_bits32(arr[i])
        xor_val = a_bits ^ b_bits
        lz = count_leading_zeros(xor_val, 32)
        tz = count_trailing_zeros(xor_val, 32)
        lz_dist[lz] += 1
        tz_dist[tz] += 1
    return dict(sorted(lz_dist.items())), dict(sorted(tz_dist.items()))

with segyio.open("test.segy", "r", ignore_geometry=True) as f:
    # 读取所有 trace
    traces = [trace.tolist() for trace in f.trace]

# 如果需要展开成一维列表
flatten_data = [x for tr in traces for x in tr]


with segyio.open("test.segy", "r", ignore_geometry=True) as f:
    first_trace = f.trace[0]          # 第一条道（返回的是 numpy.ndarray）
    first_trace_list = first_trace.tolist()  # 如果需要 Python 列表
lz_dist, tz_dist = analyze_floats32_distribution(first_trace_list)

print("前导零分布:")
for lz, count in lz_dist.items():
    print(f"前导零数量: {lz} 出现次数: {count} ")

print("\n尾随零分布:")
for tz, count in tz_dist.items():
    print(f"尾随零数量: {tz} 出现次数: {count} ")
