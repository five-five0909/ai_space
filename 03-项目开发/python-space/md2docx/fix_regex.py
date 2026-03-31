# 修复 md2docx.py 中的图片匹配正则表达式
import re

with open(r'd:\Desktop\md2docx\md2docx.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找并修复第572行 (索引571)
for i, line in enumerate(lines):
    if "image_match = re.match" in line and "line.strip()" in line:
        print(f"找到问题行 {i+1}: {repr(line)}")
        # 替换为正确的正则表达式
        lines[i] = "            image_match = re.match(r'!\\[([^\\]]*)\\]\\(([^)]+)\\)', line.strip())\n"
        print(f"修复后: {repr(lines[i])}")

with open(r'd:\Desktop\md2docx\md2docx.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("修复完成！")
