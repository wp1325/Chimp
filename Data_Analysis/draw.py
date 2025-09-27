import segyio
import numpy as np

# 打开 SEGY 文件并读取 trace 数据
with segyio.open("test.segy", "r", ignore_geometry=True) as f:
    # 读取所有 trace
    traces = [trace.tolist() for trace in f.trace]

# 拉平成一维数组
flatten_data = [x for tr in traces for x in tr]

# 将前 1000000 个点保存为二进制文件
np.array(flatten_data[0:1000000], dtype=np.float32).tofile("trace.bin")
