#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库统计脚本
统计所有文档的字数、行数、代码块数量等信息
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def count_chinese_chars(text):
    """统计中文字符数"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def count_code_blocks(text):
    """统计代码块数量"""
    return len(re.findall(r'```', text)) // 2

def count_formulas(text):
    """统计数学公式数量"""
    # 块级公式
    block_formulas = len(re.findall(r'\$\$', text))
    # 行内公式
    inline_formulas = len(re.findall(r'(?<!\$)\$(?!\$)([^\$]+)\$(?!\$)', text))
    return block_formulas // 2 + inline_formulas

def count_links(text):
    """统计链接数量"""
    return len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text))

def analyze_markdown_file(filepath):
    """分析单个Markdown文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    stats = {
        'filepath': str(filepath),
        'total_chars': len(content),
        'chinese_chars': count_chinese_chars(content),
        'total_lines': len(lines),
        'non_empty_lines': sum(1 for line in lines if line.strip()),
        'code_blocks': count_code_blocks(content),
        'formulas': count_formulas(content),
        'links': count_links(content),
    }

    return stats

def format_number(n):
    """格式化数字，添加千位分隔符"""
    return f"{n:,}"

def main():
    base_path = Path(__file__).parent.parent
    stats_list = []

    # 遍历所有目录
    for item in sorted(base_path.iterdir()):
        if item.is_dir() and item.name.startswith(('0', '1', '2', '3', '4')):
            readme_path = item / 'README.md'
            if readme_path.exists():
                stats = analyze_markdown_file(readme_path)
                stats['category'] = item.name
                stats_list.append(stats)

    # 打印统计结果
    print("\n" + "=" * 80)
    print("AI/ML 知识库统计报告")
    print("=" * 80)

    print(f"\n{'目录':<25} {'行数':>8} {'中文字符':>10} {'代码块':>6} {'公式':>6} {'链接':>6}")
    print("-" * 80)

    totals = defaultdict(int)

    for stats in stats_list:
        print(f"{stats['category']:<25} {stats['total_lines']:>8} {stats['chinese_chars']:>10} {stats['code_blocks']:>6} {stats['formulas']:>6} {stats['links']:>6}")
        for key in ['total_lines', 'chinese_chars', 'code_blocks', 'formulas', 'links']:
            totals[key] += stats[key]

    print("-" * 80)
    print(f"{'总计':<25} {totals['total_lines']:>8} {totals['chinese_chars']:>10} {totals['code_blocks']:>6} {totals['formulas']:>6} {totals['links']:>6}")

    print("\n" + "=" * 80)
    print("汇总信息")
    print("=" * 80)
    print(f"文档总数: {len(stats_list)} 篇")
    print(f"总行数: {format_number(totals['total_lines'])} 行")
    print(f"中文字符: {format_number(totals['chinese_chars'])} 字")
    print(f"代码块: {format_number(totals['code_blocks'])} 个")
    print(f"数学公式: {format_number(totals['formulas'])} 个")
    print(f"链接数: {format_number(totals['links'])} 个")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()