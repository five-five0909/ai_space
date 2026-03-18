#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抖音视频批量下载工具（命令行版本）
直接读取CSV文件并批量下载视频
"""

import csv
import os
import io
import re
import requests
import time
from datetime import datetime

class DouyinBatchDownloader:
    def __init__(self, csv_file, output_dir="downloads"):
        """
        初始化批量下载器

        Args:
            csv_file: CSV文件路径
            output_dir: 输出目录
        """
        self.csv_file = csv_file
        self.output_dir = output_dir
        self.video_list = []
        self.api_url = "https://api.pearktrue.cn/api/video/douyin/"

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"[INFO] 创建输出目录: {output_dir}")

    def load_csv(self):
        """加载CSV文件"""
        print(f"\n[INFO] 正在读取CSV文件: {self.csv_file}")

        # 尝试多种编码格式读取CSV文件
        encodings = ['utf-8', 'gbk', 'gb2312']
        csv_content = None

        for encoding in encodings:
            try:
                with open(self.csv_file, 'r', encoding=encoding) as f:
                    csv_content = f.read()
                print(f"[INFO] 使用编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue

        if csv_content is None:
            raise Exception("无法解码CSV文件")

        # 使用StringIO来模拟文件对象
        csv_file_obj = io.StringIO(csv_content)
        reader = csv.reader(csv_file_obj)

        # 跳过头部（如果有）
        header = next(reader, None)

        # 读取数据
        for row in reader:
            if len(row) >= 3:  # 确保至少有3列
                # 清理文件名，移除非法字符
                title = re.sub(r'[<>:"/\\|?*]', '_', row[1])
                self.video_list.append({
                    'id': row[0],
                    'title': title,
                    'url': row[2]
                })

        print(f"[INFO] 成功加载 {len(self.video_list)} 个视频链接")
        return self.video_list

    def parse_video(self, video_info):
        """
        解析单个视频链接

        Args:
            video_info: 视频信息字典

        Returns:
            tuple: (视频URL, 是否成功)
        """
        try:
            params = {"url": video_info['url']}
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get("code") == 200:
                video_url = result.get("data", {}).get('url')
                if video_url:
                    return video_url, True

            return None, False

        except Exception as e:
            print(f"  [ERROR] 解析失败: {str(e)}")
            return None, False

    def download_video(self, video_url, save_path):
        """
        下载单个视频文件

        Args:
            video_url: 视频下载地址
            save_path: 保存路径
        """
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            return True

        except Exception as e:
            print(f"  [ERROR] 下载失败: {str(e)}")
            return False

    def process(self):
        """批量处理所有视频"""
        if not self.video_list:
            print("[ERROR] 没有可处理的视频数据")
            return

        total = len(self.video_list)
        successful = 0
        failed = 0

        print(f"\n[INFO] 开始批量下载，共 {total} 个视频")
        print("=" * 60)

        for i, video_info in enumerate(self.video_list, 1):
            print(f"\n[{i}/{total}] 正在处理: {video_info['title'][:50]}")

            # 解析视频链接
            video_url, parsed = self.parse_video(video_info)

            if not parsed or not video_url:
                print(f"  [FAIL] 解析失败，跳过")
                failed += 1
                continue

            # 生成文件名
            filename = f"{video_info['id']}-{video_info['title']}.mp4"
            save_path = os.path.join(self.output_dir, filename)

            # 下载视频
            downloaded = self.download_video(video_url, save_path)

            if downloaded:
                print(f"  [OK] 下载完成")
                successful += 1
            else:
                print(f"  [FAIL] 下载失败")
                failed += 1

            # 添加延时，避免请求过快
            if i < total:
                time.sleep(0.5)

        # 显示最终结果
        print("\n" + "=" * 60)
        print(f"[FINISH] 批量下载完成!")
        print(f"  成功: {successful} 个")
        print(f"  失败: {failed} 个")
        print(f"  总计: {total} 个")
        print(f"  保存目录: {os.path.abspath(self.output_dir)}")
        print("=" * 60)

def main():
    """主函数"""
    print("=" * 60)
    print("抖音视频批量下载工具（命令行版本）")
    print("=" * 60)

    # 默认CSV文件路径
    csv_file = "抖音视频下载链接.csv"

    # 检查CSV文件是否存在
    if not os.path.exists(csv_file):
        csv_file = input("\n请输入CSV文件路径: ").strip()
        if not os.path.exists(csv_file):
            print(f"[ERROR] 文件不存在: {csv_file}")
            return

    # 询问输出目录
    output_dir = input(f"\n请输入输出目录 (默认: downloads): ").strip()
    if not output_dir:
        output_dir = "downloads"

    # 创建下载器并开始处理
    try:
        downloader = DouyinBatchDownloader(csv_file, output_dir)
        downloader.load_csv()
        downloader.process()
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户取消操作")
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
