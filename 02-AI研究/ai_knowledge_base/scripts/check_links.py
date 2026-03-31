#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档链接检查脚本
检查所有Markdown文档中的内部链接是否有效
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_links(filepath):
    """提取Markdown文件中的所有链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 [text](url) 格式的链接
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)

    links = []
    for text, url in matches:
        # 只处理相对路径链接
        if not url.startswith(('http://', 'https://', '#', 'mailto:')):
            links.append({
                'text': text,
                'url': url,
                'line': content[:content.find(f']({url})')].count('\n') + 1
            })

    return links

def check_link_exists(base_path, current_file, link_url):
    """检查链接目标是否存在"""
    current_dir = current_file.parent

    # 处理相对路径
    if link_url.startswith('./'):
        target_path = current_dir / link_url[2:]
    elif link_url.startswith('../'):
        target_path = current_dir / link_url
    else:
        target_path = current_dir / link_url

    # 规范化路径
    try:
        target_path = target_path.resolve()
    except:
        return False, "路径解析失败"

    # 检查文件是否存在
    if target_path.exists():
        return True, "OK"
    else:
        return False, f"文件不存在: {target_path}"

def main():
    base_path = Path(__file__).parent.parent
    all_issues = []

    # 遍历所有目录
    for item in sorted(base_path.iterdir()):
        if item.is_dir() and item.name.startswith(('0', '1', '2', '3', '4')):
            readme_path = item / 'README.md'
            if readme_path.exists():
                links = extract_links(readme_path)

                for link in links:
                    exists, message = check_link_exists(base_path, readme_path, link['url'])

                    if not exists:
                        all_issues.append({
                            'file': str(readme_path.relative_to(base_path)),
                            'line': link['line'],
                            'text': link['text'],
                            'url': link['url'],
                            'message': message
                        })

    # 打印结果
    print("\n" + "=" * 80)
    print("链接检查报告")
    print("=" * 80)

    if all_issues:
        print(f"\n发现 {len(all_issues)} 个问题:\n")
        for issue in all_issues:
            print(f"文件: {issue['file']}")
            print(f"行号: {issue['line']}")
            print(f"链接文本: {issue['text']}")
            print(f"链接地址: {issue['url']}")
            print(f"问题: {issue['message']}")
            print("-" * 40)
    else:
        print("\n所有链接检查通过!")

    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()