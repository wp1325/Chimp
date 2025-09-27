# 测试程序 用于测试Huffman编码的解压功能

import argparse
import Huffman_compression as Huff
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='需要解压的文件路径')
parser.add_argument('output_file',help='解压后输出的文件名')

args = parser.parse_args()


start_time = time.time()

file_name = args.input_file
output_name =args.output_file
Huff.unzip_file(file_name, output_name)
end_time = time.time()


print("解压完成！")
print(f"输入文件: {file_name}")
print(f"输出文件: {output_name}")
print("用时 {:.4f} 秒".format(end_time - start_time))
