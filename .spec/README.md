# 项目规范目录

本目录存放工程开发相关规范文档，Claude Code 在编程时会自动遵守。

## 目录结构

```
.spec/
├── README.md              # 本文件，规范目录说明
├── coding-standards.md    # 编码规范
├── project-conventions.md # 项目约定
└── templates/             # 模板文件
```

## 使用方法

1. **添加规范**：在对应 `.md` 文件中编写规范
2. **Claude 自动加载**：项目 `.claude/CLAUDE.md` 会引用本目录
3. **规范优先级**：项目规范 > 全局规范

## 规范文件说明

| 文件 | 用途 |
|------|------|
| `coding-standards.md` | 代码风格、命名约定、错误处理等 |
| `project-conventions.md` | 目录结构、模块划分、技术栈约定 |

## 注意事项

- 每个规范文件控制在 200 行以内
- 使用清晰的标题层级
- 示例代码使用代码块包裹