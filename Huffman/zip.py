# 测试程序 用于测试Huffman编码的压缩功能

import argparse
import Huffman_compression as Huff
import time
import os
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='需要压缩的文件路径')
args = parser.parse_args()


start_time = time.time()

file_name = args.input_file
output_file = os.path.splitext(file_name)[0] + ".huff"
Huff.zip_file(file_name, output_file)
end_time = time.time()


print("压缩完成！")
print(f"输入文件: {file_name}")
print(f"输出文件: {output_file}")
print("用时 {:.4f} 秒".format(end_time - start_time))
