import os
import glob


def remove_empty_lines(file_path):
    """去除文件中的空行"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 过滤空行（只包含空白字符的也算空行）
    non_empty_lines = [line for line in lines if line.strip()]

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(non_empty_lines)

    return len(lines) - len(non_empty_lines)


def main():
    # 获取所有 txt 文件
    txt_files = glob.glob("chapter-*.txt")

    if not txt_files:
        print("未找到 txt 文件")
        return

    total_removed = 0
    for file_path in sorted(txt_files):
        removed = remove_empty_lines(file_path)
        total_removed += removed
        print(f"{file_path}: 删除 {removed} 个空行")

    print(f"\n完成！共删除 {total_removed} 个空行")


if __name__ == "__main__":
    main()
