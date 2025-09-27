import matplotlib.pyplot as plt
from obspy.io.segy.segy import _read_segy

# 读取 SEGY 文件
filename = "example.segy"   # 替换成你的文件名
stream = _read_segy(filename)

# 提取第一道
trace = stream.traces[0]      # 第一条道
data = trace.data             # 道数据（numpy array）
npts = trace.stats.npts       # 采样点数
dt = trace.stats.delta        # 采样间隔（秒）

# 构建时间轴
time = [i * dt for i in range(npts)]

# 绘制波形
plt.figure(figsize=(10, 4))
plt.plot(time, data, linewidth=0.8)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("First Trace from SEGY")
plt.grid(True)
plt.show()
