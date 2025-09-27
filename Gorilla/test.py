import gorilla
import numpy as np

# 创建一个浮点数数组
arr = np.random.rand(1000).astype(np.float32)

# 使用 gorilla 压缩数据
compressed = gorilla.compress(arr.tobytes())

# 查看压缩后的大小
print(f"Original size: {arr.nbytes} bytes")
print(f"Compressed size: {len(compressed)} bytes")

# 解压缩数据
decompressed = gorilla.decompress(compressed)

# 将解压缩的数据转换回浮点数数组
decompressed_arr = np.frombuffer(decompressed, dtype=np.float32)

# 验证解压后的数据是否与原始数据一致
assert np.allclose(arr, decompressed_arr), "The decompressed data doesn't match the original!"

print("Compression and decompression were successful.")
