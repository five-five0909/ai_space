#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接运行批量下载（无交互模式）"""

from batch_download import DouyinBatchDownloader
import os

def main():
    print("=" * 60)
    print("抖音视频批量下载工具（自动模式）")
    print("=" * 60)

    csv_file = "抖音视频下载链接.csv"
    output_dir = "downloads_final"

    if not os.path.exists(csv_file):
        print(f"[ERROR] CSV文件不存在: {csv_file}")
        return

    print(f"\n[INFO] CSV文件: {csv_file}")
    print(f"[INFO] 输出目录: {output_dir}")

    try:
        downloader = DouyinBatchDownloader(csv_file, output_dir)
        videos = downloader.load_csv()

        if videos:
            print(f"\n[INFO] 开始下载 {len(videos)} 个视频")
            user_input = input("\n确认开始下载? (y/n): ").strip().lower()
            if user_input == 'y':
                downloader.process()
            else:
                print("[INFO] 已取消")
        else:
            print("[ERROR] 没有找到可处理的视频")

    except KeyboardInterrupt:
        print("\n\n[INFO] 用户取消操作")
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
