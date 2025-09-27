#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
解析 SEGY 文件：分离卷头、道头、浮点数据
依赖: pip install segyio numpy pandas
"""

import numpy as np
import pandas as pd
import segyio


def extract_segy(filename,
                 data_output="segy_data.npy",
                 header_output="trace_headers.csv",
                 binary_output="binary_header.csv",
                 text_output="text_header.txt"):
    """
    解析 SEGY 文件，输出卷头、道头和地震道数据
    :param filename: 输入的 SEG-Y 文件路径
    :param data_output: 地震数据保存的 numpy 文件
    :param header_output: 道头保存的 csv 文件
    :param binary_output: 二进制卷头保存的 csv 文件
    :param text_output: 文本卷头保存的 txt 文件
    :return: (data_array, header_df, binary_header_dict, text_header_str)
    """
    with segyio.open(filename, "r", ignore_geometry=True) as f:
        # -------- 卷头 --------
        # 文本卷头（通常只有 1 个）
        text_header = segyio.tools.wrap(f.text[0])
        with open(text_output, "w", encoding="utf-8") as fw:
            fw.write(text_header)
        print(f"文本卷头已保存到 {text_output}")

        # 二进制卷头
        binary_header = dict(f.bin)  # 转换成普通字典
        pd.DataFrame([binary_header]).to_csv(binary_output, index=False)
        print(f"二进制卷头已保存到 {binary_output}")

        # -------- 地震数据 --------
        n_traces = f.tracecount
        n_samples = f.samples.size
        print(f"文件: {filename}")
        print(f"道数: {n_traces}, 每道采样点数: {n_samples}")

        data = np.array([tr for tr in f.trace])  # shape = (n_traces, n_samples)
        np.save(data_output, data)
        print(f"地震数据已保存到 {data_output}")

        # -------- 道头 --------
        headers = [f.header[i] for i in range(n_traces)]
        header_df = pd.DataFrame(headers)
        header_df.to_csv(header_output, index=False)
        print(f"道头数据已保存到 {header_output}")

        return data, header_df, binary_header, text_header


if __name__ == "__main__":
    data, headers, bin_hdr, txt_hdr = extract_segy("test.segy")
    print("地震数据形状:", data.shape)
    print("道头字段示例:")
    print(headers.head())
    print("二进制卷头:", bin_hdr)
    print("文本卷头:")
    print(txt_hdr)
