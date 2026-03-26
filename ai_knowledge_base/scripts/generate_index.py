#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引生成脚本
自动生成按主题分类的索引文件
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# 主题分类定义
CATEGORIES = {
    "基础架构": ["01-mamba", "02-transformer", "03-attention", "04-positional-encoding",
                 "05-sequence-modeling", "06-novel-modules"],
    "训练基础设施": ["07-normalization", "08-activation", "09-optimizer", "10-lr-schedule",
                    "11-regularization", "12-loss-functions", "13-data-augmentation"],
    "模型压缩与对齐": ["14-knowledge-distillation", "15-quantization", "16-rlhf-alignment",
                      "17-reasoning"],
    "分布式与多模态": ["18-distributed", "19-tokenization", "20-memory-retrieval",
                      "21-kimi-attnres", "22-kv-cache", "23-moe", "24-vision-multimodal",
                      "25-diffusion"],
    "大模型技术栈": ["26-training-inference", "27-self-supervised", "28-graph-3d",
                    "29-agent", "30-time-series", "31-audio-speech"],
    "工具与框架": ["32-inference-frameworks", "33-local-tools", "34-api-platforms",
                  "35-model-formats", "36-rag-frameworks", "37-vector-db",
                  "38-agent-frameworks", "39-evaluation", "40-training-frameworks"],
    "专业领域": ["41-remote-sensing", "42-hot-topics", "43-pisfm"]
}

# 难度分类（根据主题预估）
DIFFICULTY_MAP = {
    "入门": ["02-transformer", "07-normalization", "08-activation", "09-optimizer",
            "10-lr-schedule", "11-regularization", "12-loss-functions"],
    "进阶": ["01-mamba", "03-attention", "04-positional-encoding", "13-data-augmentation",
            "14-knowledge-distillation", "15-quantization", "17-reasoning",
            "19-tokenization", "20-memory-retrieval", "22-kv-cache", "35-model-formats"],
    "高级": ["05-sequence-modeling", "06-novel-modules", "16-rlhf-alignment",
            "18-distributed", "21-kimi-attnres", "23-moe", "24-vision-multimodal",
            "25-diffusion", "26-training-inference", "27-self-supervised",
            "28-graph-3d", "29-agent", "30-time-series", "31-audio-speech",
            "32-inference-frameworks", "36-rag-frameworks", "37-vector-db",
            "38-agent-frameworks"]
}

# 应用场景分类
APPLICATION_MAP = {
    "大语言模型": ["01-mamba", "02-transformer", "03-attention", "16-rlhf-alignment",
                  "17-reasoning", "19-tokenization", "21-kimi-attnres", "22-kv-cache",
                  "26-training-inference"],
    "计算机视觉": ["24-vision-multimodal", "25-diffusion", "28-graph-3d"],
    "音频处理": ["31-audio-speech"],
    "时间序列": ["30-time-series"],
    "模型部署": ["15-quantization", "32-inference-frameworks", "33-local-tools",
               "34-api-platforms", "35-model-formats"],
    "训练优化": ["09-optimizer", "10-lr-schedule", "11-regularization", "18-distributed",
               "40-training-frameworks"],
    "智能体开发": ["29-agent", "36-rag-frameworks", "38-agent-frameworks"],
    "RAG系统": ["20-memory-retrieval", "36-rag-frameworks", "37-vector-db"]
}

def get_title_from_readme(readme_path):
    """从README文件获取标题"""
    if not readme_path.exists():
        return None

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 获取第一个标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def check_readme_exists(dir_path):
    """检查README.md是否存在"""
    readme_path = dir_path / 'README.md'
    return readme_path.exists()

def generate_topic_index(base_path):
    """生成按主题分类的索引"""
    output = """# 按主题分类索引

> 自动生成，请勿手动修改

---

"""

    for category, dirs in CATEGORIES.items():
        output += f"## {category}\n\n"

        for dir_name in dirs:
            dir_path = base_path / dir_name
            readme_path = dir_path / 'README.md'

            if check_readme_exists(dir_path):
                title = get_title_from_readme(readme_path) or dir_name
                output += f"- [{title}](./{dir_name}/README.md)\n"
            else:
                output += f"- {dir_name} ⏳ 待完善\n"

        output += "\n"

    output += "---\n*最后更新: 2026-03-22*\n"
    return output

def generate_difficulty_index(base_path):
    """生成按难度分类的索引"""
    output = """# 按难度分类索引

> 自动生成，请勿手动修改

---

## 入门级

适合初学者，涵盖基础概念和经典方法。

"""

    for dir_name in DIFFICULTY_MAP["入门"]:
        dir_path = base_path / dir_name
        readme_path = dir_path / 'README.md'

        if check_readme_exists(dir_path):
            title = get_title_from_readme(readme_path) or dir_name
            output += f"- [{title}](./{dir_name}/README.md)\n"

    output += """
## 进阶级

需要一定基础，涉及更深入的技术细节。

"""
    for dir_name in DIFFICULTY_MAP["进阶"]:
        dir_path = base_path / dir_name
        readme_path = dir_path / 'README.md'

        if check_readme_exists(dir_path):
            title = get_title_from_readme(readme_path) or dir_name
            output += f"- [{title}](./{dir_name}/README.md)\n"

    output += """
## 高级

适合有经验的开发者，涉及前沿技术和复杂系统。

"""
    for dir_name in DIFFICULTY_MAP["高级"]:
        dir_path = base_path / dir_name
        readme_path = dir_path / 'README.md'

        if check_readme_exists(dir_path):
            title = get_title_from_readme(readme_path) or dir_name
            output += f"- [{title}](./{dir_name}/README.md)\n"

    output += "\n---\n*最后更新: 2026-03-22*\n"
    return output

def generate_application_index(base_path):
    """生成按应用场景分类的索引"""
    output = """# 按应用场景索引

> 自动生成，请勿手动修改

---

"""

    for app, dirs in APPLICATION_MAP.items():
        output += f"## {app}\n\n"

        for dir_name in dirs:
            dir_path = base_path / dir_name
            readme_path = dir_path / 'README.md'

            if check_readme_exists(dir_path):
                title = get_title_from_readme(readme_path) or dir_name
                output += f"- [{title}](./{dir_name}/README.md)\n"

        output += "\n"

    output += "---\n*最后更新: 2026-03-22*\n"
    return output

def main():
    base_path = Path(__file__).parent.parent

    # 生成主题索引
    topic_index = generate_topic_index(base_path)
    with open(base_path / 'INDEX_BY_TOPIC.md', 'w', encoding='utf-8') as f:
        f.write(topic_index)
    print("已生成: INDEX_BY_TOPIC.md")

    # 生成难度索引
    difficulty_index = generate_difficulty_index(base_path)
    with open(base_path / 'INDEX_BY_DIFFICULTY.md', 'w', encoding='utf-8') as f:
        f.write(difficulty_index)
    print("已生成: INDEX_BY_DIFFICULTY.md")

    # 生成应用场景索引
    application_index = generate_application_index(base_path)
    with open(base_path / 'INDEX_BY_APPLICATION.md', 'w', encoding='utf-8') as f:
        f.write(application_index)
    print("已生成: INDEX_BY_APPLICATION.md")

    print("\n索引文件生成完成!")

if __name__ == '__main__':
    main()