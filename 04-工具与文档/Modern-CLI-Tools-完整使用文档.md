# Modern CLI Tools 完整使用文档

> 本文档是 [[MSYS2与Zsh开发环境配置]] 中安装的现代 CLI 工具的详细使用手册。
>
> 工具来源：Scoop 唯一安装源 · PowerShell 和 MSYS2 Zsh 均可用

---

## 工具安装

```powershell
scoop install eza bat fd ripgrep fzf zoxide delta lazygit btop dust
scoop install yazi starship hyperfine tokei procs sd jq xh ouch hexyl grex tealdeer watchexec just gh difftastic bottom
```

---

## 1. eza - 现代 ls 替代品

### 基础用法
```powershell
eza                          # 基础列出
eza -l                       # 长格式
eza -la                      # 包含隐藏文件
eza -lh                      # 人类可读大小
eza --tree                   # 树形结构
eza --tree --level=3         # 限制深度
eza -l --git                 # 显示 git 状态
eza -l --icons               # 显示图标
eza --sort=size              # 按大小排序
eza --sort=modified          # 按修改时间排序
eza -lT --level=2 --git --icons  # 综合常用
```

### 开发场景
```powershell
# 查看项目结构
eza --tree --level=3 --ignore-glob="node_modules|.git|dist|target"

# 查找最近修改的文件
eza -l --sort=modified --reverse

# 只看目录
eza -lD

# 只看文件
eza -lf

# 查看权限详情
eza -l --octal-permissions

# 配置别名 (PowerShell profile)
Set-Alias ls eza
function ll { eza -la --icons --git @args }
function lt { eza --tree --level=3 --icons @args }
```

---

## 2. bat - 现代 cat 替代品

### 基础用法
```powershell
bat file.txt                 # 带语法高亮查看
bat -n file.txt              # 显示行号
bat -A file.txt              # 显示不可见字符
bat --plain file.txt         # 无装饰输出
bat -r 10:20 file.txt        # 查看第10-20行
bat file1.txt file2.txt      # 查看多文件
```

### 开发场景
```powershell
# 配置文件查看
bat ~/.gitconfig
bat package.json
bat Cargo.toml

# 管道使用
cat file.txt | bat -l json   # 强制指定语言
curl -s api.example.com | bat -l json

# diff 查看
bat --diff file.txt          # 显示 git diff

# 列出支持的语言
bat --list-languages

# 列出主题
bat --list-themes

# 设置主题
bat --theme="Dracula" file.txt

# 作为 man 页面 pager
$env:MANPAGER = "sh -c 'col -bx | bat -l man -p'"

# 与 fzf 集成预览
fzf --preview 'bat --color=always {}'
```

### 配置文件
```powershell
# 创建配置 $env:APPDATA\bat\config
--theme="TwoDark"
--style="numbers,changes,header"
--map-syntax "*.conf:INI"
--map-syntax ".env:Bash"
```

---

## 3. fd - 现代 find 替代品

### 基础用法
```powershell
fd pattern                   # 搜索文件名
fd -e js                     # 按扩展名
fd -t f                      # 只找文件 (f/d/l/x)
fd -t d                      # 只找目录
fd -H                        # 包含隐藏文件
fd -I                        # 不忽略 .gitignore
fd -d 3                      # 最大深度3
fd --size +1mb               # 大于1MB的文件
```

### 开发场景
```powershell
# 找所有 TypeScript 文件
fd -e ts -e tsx

# 找所有测试文件
fd -e test.js -e spec.ts
fd "\.test\." -e js -e ts

# 找大文件
fd --size +100mb

# 找最近修改的文件
fd --changed-within 2d

# 找旧文件清理
fd --changed-before 30d -e log

# 批量操作 - 删除 node_modules
fd -t d node_modules --exec rm -rf {}

# 批量操作 - 格式化所有 JSON
fd -e json --exec bat {}

# 找配置文件
fd -H "\.env" -t f

# 排除目录
fd -e ts --exclude node_modules --exclude dist

# 统计文件数
fd -e rs | wc -l

# 执行命令
fd -e png --exec convert {} {.}.jpg  # 批量转换图片

# 与 fzf 集成
fd -t f | fzf
```

---

## 4. ripgrep (rg) - 现代 grep

### 基础用法
```powershell
rg pattern                   # 搜索
rg pattern file.txt          # 在文件中搜索
rg -i pattern                # 忽略大小写
rg -v pattern                # 反向匹配
rg -l pattern                # 只显示文件名
rg -c pattern                # 显示匹配数量
rg -n pattern                # 显示行号
rg --json pattern            # JSON 输出
```

### 开发场景
```powershell
# 搜索函数定义
rg "^function\s+\w+" -t js
rg "def \w+" -t py
rg "fn \w+" -t rust

# 搜索 TODO/FIXME
rg "TODO|FIXME|HACK|BUG" --type-add 'src:*.{js,ts,py,rs}'

# 搜索含上下文
rg "error" -A 3 -B 3        # 前后3行

# 搜索特定类型文件
rg "import" -t ts
rg "require" -t js

# 搜索多个 pattern
rg -e "foo" -e "bar"

# 替换预览 (不修改)
rg "oldFunction" --replace "newFunction"

# 搜索字符串字面量 (不是正则)
rg -F "array[0]"

# 按文件类型分组
rg "TODO" --type-list       # 查看支持的类型

# 统计每个文件匹配数
rg -c "console.log" -t js | sort -t: -k2 -rn

# 搜索二进制
rg -a "pattern" binary_file

# 搜索压缩文件
rg -z "pattern" archive.gz

# 排除目录
rg "pattern" --glob '!node_modules' --glob '!dist'

# 搜索空行
rg "^$" -c file.txt

# 查找超长行
rg ".{100,}" -l
```

---

## 5. fzf - 模糊查找器

### 基础用法
```powershell
fzf                          # 交互选择
fzf --multi                  # 多选 (Tab)
fzf --reverse                # 列表在上
fzf --height 40%             # 窗口高度
fzf --preview 'cat {}'       # 预览窗口
fzf -q "initial query"       # 初始查询
```

### 开发场景
```powershell
# 文件选择
$file = fzf --preview 'bat --color=always {}'
code $file

# 历史命令搜索 (PowerShell)
function fh {
    $cmd = Get-Content (Get-PSReadlineOption).HistorySavePath | 
           Select-Object -Unique | fzf --tac
    Invoke-Expression $cmd
}

# Git branch 切换
function fgb {
    $branch = git branch --all | fzf | ForEach-Object { $_.Trim() -replace '^remotes/origin/', '' }
    git checkout $branch
}

# Git log 浏览
function fgl {
    git log --oneline --graph | fzf --ansi --preview 'git show --color=always {1}'
}

# 进程 kill
function fkill {
    $pid = procs | fzf | ForEach-Object { ($_ -split '\s+')[1] }
    Stop-Process $pid
}

# cd 到项目
function fcd {
    $dir = fd -t d --max-depth 4 | fzf --preview 'eza --tree --level=2 {}'
    Set-Location $dir
}

# 搜索并编辑
function fe {
    $file = rg --files | fzf --preview 'bat --color=always {}'
    if ($file) { code $file }
}

# npm scripts
function fnpm {
    $script = cat package.json | jq -r '.scripts | keys[]' | fzf
    npm run $script
}

# 环境变量查看
function fenv {
    Get-ChildItem env: | ForEach-Object { "$($_.Name)=$($_.Value)" } | fzf
}

# 端口查看
function fport {
    netstat -ano | fzf
}
```

### fzf 配置 (PowerShell Profile)
```powershell
$env:FZF_DEFAULT_COMMAND = 'fd --type f --hidden --follow'
$env:FZF_DEFAULT_OPTS = @"
--height 60%
--layout=reverse
--border
--preview 'bat --color=always --line-range :50 {}'
--bind 'ctrl-/:toggle-preview'
--color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc
"@
```

---

## 6. zoxide - 智能 cd

### 基础用法
```powershell
z foo                        # 跳转到匹配 foo 的目录
z foo bar                    # 匹配包含 foo 和 bar 的目录
z -                          # 跳转上一个目录
zi                           # 交互式选择 (需要 fzf)
z ..                         # 上级目录
```

### 开发场景
```powershell
# 初始化 (PowerShell Profile)
Invoke-Expression (& { (zoxide init powershell | Out-String) })

# 快速跳转到项目
z myproject                  # 自动找到最频繁的 myproject 路径
z proj src                   # 跳转包含 proj 和 src 的目录

# 查看数据库
zoxide query --list          # 所有记录
zoxide query --list --score  # 带分数

# 手动添加
zoxide add /path/to/dir

# 移除记录
zoxide remove /path/to/dir

# 搜索特定路径
zoxide query myproject

# 与 fzf 集成的交互跳转
zi                           # 模糊搜索所有历史目录
```

---

## 7. delta - Git Diff 增强

### 基础用法
```powershell
# 配置 git 使用 delta (~/.gitconfig)
git config --global core.pager delta
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
git config --global delta.line-numbers true
git config --global delta.side-by-side true
```

### .gitconfig 完整配置
```ini
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true
    line-numbers = true
    side-by-side = true
    syntax-theme = Dracula
    file-style = bold yellow ul
    file-decoration-style = none
    hunk-header-style = file line-number syntax

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
```

### 开发场景
```powershell
# 基本 diff
git diff                     # 自动使用 delta
git show HEAD                # 显示最后提交
git log -p                   # 带 patch 的日志

# 并排比较
delta file1.txt file2.txt

# 禁用并排 (窄屏)
git diff | delta --side-by-side=false

# diff 两个分支
git diff main..feature | delta

# 查看 stash
git stash show -p | delta
```

---

## 8. lazygit - Git TUI

### 键盘操作
```
# 导航
hjkl / 方向键        移动
Tab                  切换面板
[ ]                  切换标签

# 文件操作
Space                暂存/取消暂存
a                    暂存所有
c                    提交
C                    使用编辑器提交
A                    修改上次提交
P                    Push
p                    Pull

# 分支操作
n                    新建分支
space                切换分支
M                    合并到当前
r                    rebase

# Stash
s                    stash
g                    pop stash

# 其他
?                    帮助
R                    刷新
:                    自定义命令
+/-                  展开/收起

# diff 导航
e                    编辑文件
o                    打开文件
```

### 开发场景
```powershell
lg                           # 启动 lazygit (别名)
```

### lazygit 配置

`$env:APPDATA\lazygit\config.yml`：

```yaml
gui:
  theme:
    activeBorderColor: ['#89b4fa', 'bold']
  showIcons: true

customCommands:
  - key: 'C'
    command: 'git commit -m "{{index .PromptResponses 0}}"'
    context: 'files'
    prompts:
      - type: 'input'
        title: 'Commit message'
      
  - key: '<c-r>'
    command: 'git rebase -i HEAD~{{index .PromptResponses 0}}'
    context: 'commits'
    prompts:
      - type: 'input'
        title: 'How many commits to rebase?'
```

---

## 9. btop - 系统监控

### 基础操作
```
# 键盘操作
m                    切换内存视图
n                    网络视图
d                    磁盘视图
p                    进程视图
f                    过滤进程
k                    Kill 进程
+/-                  调整更新间隔
1-9                  排序选项
q                    退出
```

### 使用场景
```powershell
btop                         # 启动
btop --utf-force             # 强制 UTF-8
```

---

## 10. dust - 磁盘使用分析

### 基础用法
```powershell
dust                         # 当前目录
dust -d 3                    # 深度3
dust -n 20                   # 显示前20
dust -r                      # 反向排序
dust -p                      # 显示百分比
dust /path/to/dir            # 指定目录
```

### 开发场景
```powershell
# 找大目录
dust -d 2 ~

# 分析项目
dust -d 3 ./myproject

# 排除目录
dust --ignore-directory node_modules

# 找最大文件
dust -f                      # 只显示文件

# 分析系统磁盘
dust /

# 开发清理场景
dust -d 2 ~/.npm             # npm 缓存
dust -d 2 ~/.cargo           # Rust 缓存
dust -d 2 ~/AppData          # Windows 应用数据
```

---

## 11. yazi - 终端文件管理器

### 键盘操作
```
# 导航
hjkl / 方向键        移动
Enter                进入/打开
Backspace           返回上级
gg / G               首/尾
o                    排序

# 文件操作
a                    创建文件/目录
r                    重命名
d                    删除到垃圾桶
D                    永久删除
c                    复制
x                    剪切
p                    粘贴
y                    yank (复制路径)

# 选择
Space                多选
v                    视觉模式
V                    全选

# 预览
Tab                  切换预览
z                    搜索 (zoxide)
f                    过滤

# 其他
.                    显示隐藏文件
/                    搜索
q                    退出
```

### 配置

yazi 配置目录：`$env:APPDATA\yazi\config\`

```toml
# yazi.toml
[manager]
ratio = [1, 3, 4]
show_hidden = false
show_symlink = true
```

### 开发场景
```powershell
yazi                         # 启动
yazi /path/to/project       # 打开指定目录

# Shell 集成 - 退出时 cd 到当前目录
function y {
    $tmp = [System.IO.Path]::GetTempFileName()
    yazi --cwd-file=$tmp @args
    $cwd = Get-Content $tmp
    if ($cwd -and $cwd -ne $PWD.Path) {
        Set-Location $cwd
    }
    Remove-Item $tmp
}
```

---

## 12. starship - Shell 提示符

### 安装配置
```powershell
# PowerShell Profile 添加
Invoke-Expression (&starship init powershell)
```

### 配置文件 `~/.config/starship.toml`

```toml
format = """
[╭─](bold green)$os$username$hostname$directory$git_branch$git_status$git_metrics
[╰─](bold green)$character"""

[os]
disabled = false
style = "bold blue"

[username]
show_always = false
style_user = "bold yellow"
format = "[$user]($style) "

[directory]
style = "bold cyan"
truncate_to_repo = true
truncation_length = 4
format = "[$path]($style)[$read_only]($read_only_style) "

[git_branch]
symbol = " "
style = "bold purple"
format = "on [$symbol$branch]($style) "

[git_status]
format = '([\[$all_status$ahead_behind\]]($style) )'
style = "bold red"
conflicted = "⚡"
ahead = "⇡${count}"
behind = "⇣${count}"
untracked = "?"
modified = "!"
staged = "+"
deleted = "✗"

[nodejs]
symbol = " "
format = "[$symbol($version )]($style)"

[rust]
symbol = " "
format = "[$symbol($version )]($style)"

[python]
symbol = " "
format = "[$symbol($version )]($style)"

[docker_context]
symbol = " "
format = "[$symbol$context]($style) "

[package]
disabled = false
format = "[$symbol$version]($style) "

[time]
disabled = false
format = "[$time]($style) "
time_format = "%H:%M"
```

---

## 13. hyperfine - 命令基准测试

### 基础用法
```powershell
hyperfine 'command'          # 基准测试
hyperfine --runs 100 'cmd'   # 指定运行次数
hyperfine --warmup 5 'cmd'   # 预热运行
hyperfine 'cmd1' 'cmd2'      # 比较两个命令
```

### 开发场景
```powershell
# 比较工具性能
hyperfine 'fd -e rs' 'find . -name "*.rs"'
hyperfine 'rg "TODO"' 'grep -r "TODO" .'

# 比较构建工具
hyperfine 'npm run build' 'pnpm build' 'yarn build'

# 带参数变化的测试
hyperfine --parameter-scan n 1 10 'sort -S{n}M bigfile.txt'

# 导出结果
hyperfine --export-json results.json 'cmd1' 'cmd2'
hyperfine --export-markdown results.md 'cmd1' 'cmd2'

# 测试脚本启动时间
hyperfine --shell=none 'node --version'
hyperfine 'python3 -c "print(1)"' 'ruby -e "puts 1"'

# 测试 API 响应
hyperfine 'curl -s https://api.example.com/health'

# 准备和清理
hyperfine --prepare 'cargo clean' 'cargo build'

# 忽略错误
hyperfine --ignore-failure 'might-fail-command'
```

---

## 14. tokei - 代码统计

### 基础用法
```powershell
tokei                        # 当前目录统计
tokei src/                   # 指定目录
tokei -e node_modules        # 排除目录
tokei -t JavaScript,TypeScript  # 指定语言
tokei -o json                # JSON 输出
tokei -o toml                # TOML 输出
```

### 开发场景
```powershell
# 项目总览
tokei --sort lines

# 排除测试和依赖
tokei -e node_modules -e dist -e .git -e coverage

# 按语言过滤
tokei -t Rust,Python,JavaScript

# 导出报告
tokei -o json | jq '.Total'

# 统计特定文件类型
tokei -t Markdown

# 详细输出
tokei -v

# CI 报告
tokei -o json | jq '{
  total_lines: .Total.lines,
  code_lines: .Total.code,
  comment_lines: .Total.comments
}'
```

---

## 15. procs - 现代 ps

### 基础用法
```powershell
procs                        # 所有进程
procs node                   # 搜索进程名
procs --tree                 # 进程树
procs --watch                # 实时监控
procs --sortd cpu            # 按 CPU 排序
procs --sortd mem            # 按内存排序
```

### 开发场景
```powershell
# 找开发服务器
procs node
procs python
procs java

# 监控特定进程
procs --watch node

# 找占用端口的进程
procs --tcp 3000

# 进程树
procs --tree

# 显示完整命令
procs --no-header

# 找僵尸进程
procs | rg zombie

# 按内存排序
procs --sortd mem | head
```

---

## 16. sd - 现代 sed 替代

### 基础用法
```powershell
sd 'old' 'new' file.txt      # 替换
sd -n 5 'old' 'new' file.txt # 替换前5个
cat file | sd 'old' 'new'    # 管道
sd -p 'old' 'new' file.txt   # 预览不修改
```

### 开发场景
```powershell
# 批量重命名变量
sd 'oldVarName' 'newVarName' src/*.ts

# 更新版本号
sd '\"version\": \"1.0.0\"' '"version": "1.1.0"' package.json

# 替换 API URL
sd 'http://localhost:3000' 'https://api.production.com' config/*.json

# 删除行 (替换为空)
cat file.txt | sd '^\s*//.*\n' ''   # 删除注释

# 多文件替换
fd -e ts | ForEach-Object { sd 'require\(' 'import(' $_ }

# 正则替换
sd '(\d{4})-(\d{2})-(\d{2})' '$3/$2/$1' dates.txt

# 替换整行
sd '^DEBUG=.*' 'DEBUG=false' .env

# 字符串字面量替换 (无正则)
sd -s 'foo.bar()' 'foo.baz()' file.js

# 批量处理
fd -e js --exec sd 'console.log' '// console.log' {}
```

---

## 17. jq - JSON 处理器

### 基础用法
```powershell
jq '.' file.json             # 格式化
jq '.key' file.json          # 获取字段
jq '.key.nested' file.json   # 嵌套字段
jq '.array[]' file.json      # 数组展开
jq '.[0]' file.json          # 数组第一个
jq -r '.key' file.json       # 原始字符串输出
jq -c '.' file.json          # 紧凑输出
```

### 开发场景
```powershell
# API 响应处理
curl -s https://api.github.com/repos/user/repo | jq '{name: .name, stars: .stargazers_count}'

# 数组过滤
jq '.users[] | select(.age > 18)' users.json

# 字段提取
jq '.[] | .name' users.json
jq -r '.[] | "\(.name),\(.email)"' users.json  # CSV 格式

# 转换
jq '.[] | {id: .id, fullname: "\(.firstName) \(.lastName)"}' users.json

# 统计
jq '.[] | .score' data.json | jq -s 'add/length'  # 平均值

# package.json 操作
jq '.dependencies | keys[]' package.json
jq '.scripts' package.json

# 构建查询
cat api_response.json | jq '
  .data
  | .[] 
  | select(.status == "active")
  | {id, name, email: .contact.email}
'

# 修改 JSON
jq '.version = "2.0.0"' package.json

# 合并 JSON
jq -s '.[0] * .[1]' base.json override.json

# 去重
jq '[.[] | .type] | unique' data.json

# 条件处理
jq '.[] | if .score > 90 then "A" elif .score > 80 then "B" else "C" end' grades.json

# 错误处理
jq '.field // "default"' file.json

# 环境变量
jq --arg name "John" '.[] | select(.name == $name)' users.json

# 多文件
jq -s '.' file1.json file2.json
```

---

## 18. xh - 现代 HTTP 客户端

### 基础用法
```powershell
xh GET https://api.example.com
xh POST https://api.example.com key=value
xh https://api.example.com              # 默认 GET
xh -j https://api.example.com          # JSON 模式
xh -f https://api.example.com          # Form 模式
xh -d https://api.example.com/file     # 下载
```

### 开发场景
```powershell
# REST API 测试
xh GET https://api.github.com/users/username
xh POST https://api.example.com/users \
    name="John" email="john@example.com"

# 带认证
xh GET https://api.example.com/protected \
    Authorization:"Bearer $token"

# JSON 请求体
xh POST https://api.example.com/data \
    Content-Type:application/json \
    '{"key": "value"}'

# 查看请求详情
xh --verbose GET https://api.example.com

# 只看 headers
xh --headers GET https://api.example.com

# 下载文件
xh -d https://example.com/file.zip -o myfile.zip

# 跟随重定向
xh --follow https://example.com

# 设置超时
xh --timeout 10 GET https://api.example.com

# 上传文件
xh POST https://api.example.com/upload \
    file@./document.pdf

# 使用 session
xh --session ./session.json POST https://api.example.com/login \
    username=admin password=secret

# GraphQL
xh POST https://api.example.com/graphql \
    query='{ user { name email } }'

# 保存为 curl 命令
xh --curl GET https://api.example.com
```

---

## 19. ouch - 压缩/解压工具

### 基础用法
```powershell
ouch compress files/ archive.zip        # 压缩
ouch decompress archive.zip             # 解压
ouch decompress archive.tar.gz -d dir/ # 解压到指定目录
ouch list archive.zip                   # 查看内容
```

### 开发场景
```powershell
# 创建各种格式
ouch compress dist/ release-v1.0.tar.gz
ouch compress logs/ logs.zip
ouch compress backup/ backup.tar.bz2
ouch compress project/ project.7z

# 批量解压
fd -e zip | ForEach-Object { ouch decompress $_ }

# 查看不解压
ouch list release.tar.gz

# 压缩多个文件
ouch compress file1.txt file2.txt file3.txt archive.zip

# 解压到当前目录
ouch decompress archive.zip --dir .

# 自动识别格式
ouch decompress unknown_file  # 自动检测格式
```

---

## 20. hexyl - 十六进制查看器

### 基础用法
```powershell
hexyl file.bin               # 查看文件
hexyl -n 256 file.bin        # 只看前256字节
hexyl --skip 100 file.bin    # 跳过前100字节
hexyl -b 8 file.bin          # 每行8字节
cat file | hexyl             # 管道输入
```

### 开发场景
```powershell
# 分析二进制文件
hexyl executable.exe | head -50

# 查看文件头 (magic bytes)
hexyl -n 16 unknown.file

# 比较二进制文件
hexyl file1.bin > hex1.txt
hexyl file2.bin > hex2.txt
delta hex1.txt hex2.txt

# 常见文件头
# JPEG: FF D8 FF
# PNG:  89 50 4E 47
# PDF:  25 50 44 46

# 调试序列化数据
hexyl serialized.dat

# 查看字符串编码
echo "Hello" | hexyl
```

---

## 21. grex - 正则表达式生成器

### 基础用法
```powershell
grex "abc" "abd" "abe"       # 生成匹配这些字符串的正则
grex -d "abc" "123"          # 只用数字类
grex -w "hello" "world"      # 用 \w
grex -s "foo" "bar"          # 简化输出
grex -c "Test1" "Test2"      # 大小写不敏感
```

### 开发场景
```powershell
# 生成邮箱正则
grex "user@example.com" "admin@test.org"

# 生成日期正则
grex "2024-01-01" "2023-12-31" "2024-06-15"

# 生成 IP 地址正则
grex "192.168.1.1" "10.0.0.1" "172.16.0.1"

# 生成 URL 正则
grex "https://example.com" "http://test.org"

# 生成电话号码正则
grex "555-1234" "555-5678" "555-9012"

# 测试生成的正则
$pattern = grex "v1.0.0" "v2.1.3" "v10.2.1"
"v3.4.5" -match $pattern
```

---

## 22. tealdeer (tldr) - 命令速查

### 基础用法
```powershell
tldr git                     # git 速查
tldr tar                     # tar 速查
tldr -u                      # 更新缓存
tldr -l                      # 列出所有命令
tldr -p linux git            # 指定平台
```

### 开发场景
```powershell
# 快速查命令
tldr curl
tldr docker
tldr kubectl
tldr ffmpeg
tldr rsync
tldr ssh
tldr gpg

# 搜索功能
tldr -s "compress"           # 搜索含 compress 的命令
```

### 配置

`$env:APPDATA\tealdeer\config.toml`：

```toml
[display]
use_pager = true
pager_command = "bat -p"

[updates]
auto_update = true
auto_update_interval_hours = 24
```

---

## 23. watchexec - 文件监控执行

### 基础用法
```powershell
watchexec 'command'                    # 监控当前目录
watchexec -e rs 'cargo test'          # 监控 .rs 文件
watchexec -w src/ 'npm run build'     # 监控指定目录
watchexec -c 'command'                # 执行前清屏
watchexec --on-busy-update restart    # 忙时重启
```

### 开发场景
```powershell
# Rust 开发
watchexec -e rs -c 'cargo test 2>&1'
watchexec -e rs 'cargo build'
watchexec -e rs,toml 'cargo clippy'

# Node.js 开发
watchexec -e js,ts -c 'npm test'
watchexec -e ts 'npx tsc --noEmit'
watchexec -e json 'npm run lint'

# Python 开发
watchexec -e py -c 'python -m pytest'
watchexec -e py 'python -m mypy src/'

# 忽略目录
watchexec -i node_modules -e ts 'tsc'

# 延迟执行 (等待编辑完成)
watchexec --debounce 500ms -e ts 'npm run build'

# 传递信号
watchexec --signal SIGTERM -e py 'python server.py'

# 只在第一次执行
watchexec --once 'make setup'
```

---

## 24. just - 任务运行器

### Justfile 语法

```makefile
# Justfile

# 默认任务
default:
    just --list

# 变量
version := "1.0.0"
binary := "myapp"

# 依赖关系
build: test
    cargo build --release

test:
    cargo test

# 带参数
deploy env="staging":
    echo "Deploying to {{env}}"
    ./deploy.sh {{env}}

# 条件
release tag:
    #!/usr/bin/env bash
    if [ "$(git status --porcelain)" ]; then
        echo "Working directory is dirty"
        exit 1
    fi
    git tag -a {{tag}} -m "Release {{tag}}"
    git push --tags

# 私有任务
_setup:
    echo "Setting up..."

# 跨平台
run:
    {{ if os() == "windows" { ".\app.exe" } else { "./app" } }}
```

### 开发场景 Justfile 模板

**Web 项目：**

```makefile
dev:
    npm run dev

build:
    npm run build

test:
    npm test

test-watch:
    npm run test:watch

lint:
    npm run lint

lint-fix:
    npm run lint:fix

format:
    prettier --write .

type-check:
    npx tsc --noEmit

clean:
    rm -rf dist node_modules/.cache

install:
    npm ci

deploy env="production":
    npm run build
    rsync -avz dist/ user@server:/var/www/{{env}}/

db-migrate:
    npx prisma migrate dev

db-seed:
    node scripts/seed.js
```

**Rust 项目：**

```makefile
fmt:
    cargo fmt

clippy:
    cargo clippy -- -D warnings

doc:
    cargo doc --open

bench:
    cargo bench
```

```powershell
# 常用命令
just                         # 运行默认任务
just build                   # 运行 build
just deploy production       # 带参数
just --list                  # 列出所有任务
just --dry-run build         # 预览不执行
```

---

## 25. gh - GitHub CLI

### 基础用法
```powershell
gh auth login                # 登录
gh repo clone user/repo      # 克隆
gh repo create               # 创建仓库
gh issue list                # 列出 issues
gh pr list                   # 列出 PRs
gh pr create                 # 创建 PR
gh release list              # 列出发布
```

### 开发场景
```powershell
# Repository 操作
gh repo create myproject --private
gh repo fork user/repo --clone
gh repo view --web

# Issue 管理
gh issue create --title "Bug" --body "Description"
gh issue list --label bug
gh issue list --assignee @me
gh issue view 42
gh issue close 42
gh issue comment 42 --body "Fixed in PR #43"

# PR 工作流
gh pr create --title "Feature" --body "Description" --base main
gh pr list --state open
gh pr view 15
gh pr review 15 --approve
gh pr review 15 --request-changes --body "Please fix..."
gh pr merge 15 --squash
gh pr checkout 15             # 本地检出 PR

# Actions
gh workflow list
gh workflow run deploy.yml
gh run list
gh run view 123
gh run watch                  # 实时查看

# Release
gh release create v1.0.0 --notes "Release notes"
gh release create v1.0.0 dist/* --title "v1.0.0"
gh release download v1.0.0

# Gist
gh gist create file.txt
gh gist create --public script.sh
gh gist list

# API 调用
gh api repos/user/repo
gh api graphql -f query='{ viewer { login } }'

# 搜索
gh search repos "language:rust stars:>1000"
gh search issues "is:open label:bug"

# Codespaces
gh codespace create
gh codespace list
gh codespace code  # 在 VS Code 打开
```

---

## 26. difftastic - 语法感知 diff

### 基础用法
```powershell
difft file1.js file2.js      # 比较文件
difft --display side-by-side file1 file2

# Git 集成
git config --global diff.external difft
git diff                     # 自动使用 difftastic
```

### Git 配置
```powershell
# 设置为 git difftool
git config --global difftool.difftastic.cmd 'difft "$LOCAL" "$REMOTE"'
git config --global difftool.prompt false
git difftool HEAD~1

# 环境变量
$env:GIT_EXTERNAL_DIFF = "difft"
git log -p --ext-diff        # 在 log 中使用
```

### 开发场景
```powershell
# 比较两个版本
difft old_version.py new_version.py

# 比较 JSON (语法感知，忽略格式差异)
difft old.json new.json

# 比较 HTML
difft old.html new.html

# 设置显示模式
difft --display inline file1 file2
difft --display side-by-side file1 file2

# 语言覆盖
difft --language python file1.txt file2.txt

# 上下文行数
difft --context 5 file1 file2
```

---

## 27. bottom (btm) - 系统监控 TUI

### 基础操作
```
# 键盘
? / h                帮助
q / Ctrl+C           退出
dd                   删除/Kill 进程
e                    展开组件
t                    进程树视图
/                    搜索进程
P                    按 PID 排序
N                    按名称排序
C                    按 CPU 排序
M                    按内存排序
Tab                  切换面板
```

### 使用场景
```powershell
btm                          # 启动
btm --battery                # 显示电池
btm --process_command        # 显示完整命令
btm -r 500                   # 500ms 刷新率
btm --tree                   # 进程树模式
```

### 配置文件 `~/.config/bottom/bottom.toml`

```toml
[flags]
rate = 500
color = "nord"
tree = false
battery = true
process_command = true

[row]
  [[row.child]]
  type = "cpu"
  [[row.child]]
  type = "mem"
```

---

## PowerShell Profile 完整配置

```powershell
# $PROFILE 文件内容

# ===== 初始化工具 =====
Invoke-Expression (&starship init powershell)
Invoke-Expression (& { (zoxide init powershell | Out-String) })

# ===== 别名 =====
Set-Alias cat bat
Set-Alias find fd
Set-Alias grep rg
Set-Alias top btm
Set-Alias ps procs
Set-Alias lg lazygit

# ===== eza 别名 =====
function ls { eza --icons @args }
function ll { eza -la --icons --git @args }
function lt { eza --tree --level=3 --icons --ignore-glob="node_modules|.git|dist" @args }
function la { eza -a --icons @args }

# ===== fzf 配置 =====
$env:FZF_DEFAULT_COMMAND = 'fd --type f --hidden --follow --exclude .git'
$env:FZF_DEFAULT_OPTS = '--height 60% --layout=reverse --border --preview "bat --color=always --line-range :50 {}"'

# ===== 开发函数 =====

# 模糊文件打开
function fe {
    $file = fd -t f | fzf --preview 'bat --color=always {}'
    if ($file) { code $file }
}

# 模糊 cd
function fcd {
    $dir = fd -t d --max-depth 4 | fzf --preview 'eza --tree --level=2 {}'
    if ($dir) { Set-Location $dir }
}

# Git branch 切换
function fgb {
    $branch = git branch --all | 
              Where-Object { $_ -notmatch '^\*' } |
              ForEach-Object { $_.Trim() } |
              fzf --preview 'git log --oneline --color=always {}'
    if ($branch) { git checkout ($branch -replace '^remotes/origin/', '') }
}

# 历史搜索
function fh {
    $cmd = Get-Content (Get-PSReadlineOption).HistorySavePath |
           Select-Object -Unique |
           fzf --tac --no-sort
    if ($cmd) { Invoke-Expression $cmd }
}

# yazi 集成
function y {
    $tmp = [System.IO.Path]::GetTempFileName()
    yazi --cwd-file=$tmp @args
    $cwd = Get-Content $tmp -ErrorAction SilentlyContinue
    if ($cwd -and (Test-Path $cwd) -and $cwd -ne $PWD.Path) {
        Set-Location $cwd
    }
    Remove-Item $tmp -ErrorAction SilentlyContinue
}

# 快速查找并查看
function fp {
    rg --line-number '' | 
    fzf --delimiter ':' \
        --preview 'bat --color=always --highlight-line {2} {1}' \
        --preview-window '+{2}-5'
}

# HTTP 工具
function api { xh @args }

# 代码统计
function loc { tokei -e node_modules,dist,.git @args }

# 磁盘分析
function dua { dust -d 3 --ignore-directory node_modules,dist,.git @args }

# 端口查找
function port { netstat -ano | rg $args }

# 快速 HTTP Server
function serve {
    $port = if ($args[0]) { $args[0] } else { 8080 }
    Write-Host "Serving on http://localhost:$port"
    xh GET "http://localhost:$port" 2>/dev/null
}
```

---

## 场景化工作流

### 🔍 代码调查工作流
```powershell
# 1. 找到相关文件
fd -e ts -e js | fzf --preview 'bat --color=always {}'

# 2. 搜索代码
rg "functionName" -A 5 -B 2

# 3. 查看文件结构
eza --tree --level=3 src/

# 4. 分析代码量
tokei src/

# 5. 查看历史变更
git log --oneline | fzf --preview 'git show --color=always {1}' | awk '{print $1}' | xargs git show
```

### 🚀 部署工作流
```powershell
# 1. 检查代码状态
lazygit

# 2. 运行测试
just test

# 3. 构建性能测试
hyperfine 'just build'

# 4. 压缩产物
ouch compress dist/ release-v1.0.tar.gz

# 5. 发布
gh release create v1.0.0 release-v1.0.tar.gz

# 6. 监控部署
btm
```

### 🐛 调试工作流
```powershell
# 1. 找错误日志
rg "ERROR|FATAL" logs/ -A 3

# 2. 监控文件变化
watchexec -e log 'tail -n 20 app.log'

# 3. 分析二进制
hexyl core.dump | head -100

# 4. 检查进程
procs --watch myapp

# 5. 系统资源
btop
```

### 📦 依赖管理工作流
```powershell
# 1. 分析磁盘使用
dust ~/.npm -d 3
dust ~/.cargo -d 2

# 2. 找大文件
fd --size +10mb | fzf

# 3. 查看 package.json
bat package.json
jq '.dependencies' package.json | bat -l json

# 4. 检查安全
gh api repos/{owner}/{repo}/vulnerability-alerts
```

### 🔄 重构工作流
```powershell
# 1. 找所有使用点
rg "oldFunctionName" --type ts -n

# 2. 预览替换
sd -p 'oldFunctionName' 'newFunctionName' src/*.ts

# 3. 执行替换
fd -e ts | ForEach-Object { sd 'oldFunctionName' 'newFunctionName' $_ }

# 4. 验证更改
lazygit

# 5. 运行测试
just test
```

---

## 给 Claude Code 类工具的提示词

```
你是一个精通现代 CLI 工具链的高级工程师助手。在我的开发环境中已安装以下工具，你在给出任何涉及命令行操作的建议时，必须优先使用这些现代工具，而不是传统的 Unix 工具。

## 已安装的现代工具映射

| 场景 | 使用工具 | 替代的传统工具 |
|------|---------|--------------|
| 列出文件 | eza | ls |
| 查看文件内容 | bat | cat |
| 搜索文件 | fd | find |
| 搜索内容 | rg (ripgrep) | grep |
| 交互选择 | fzf | 无 |
| 目录跳转 | zoxide (z) | cd |
| Git diff | delta | diff |
| Git TUI | lazygit | git cli |
| 系统监控 | btop / btm (bottom) | top/htop |
| 磁盘分析 | dust | du |
| 文件管理 | yazi | ranger/mc |
| HTTP请求 | xh | curl/wget |
| 文本替换 | sd | sed |
| JSON处理 | jq | python -m json |
| 进程查看 | procs | ps |
| 压缩解压 | ouch | tar/zip |
| 十六进制 | hexyl | xxd/hexdump |
| 正则生成 | grex | 手写 |
| 命令速查 | tldr | man |
| 文件监控 | watchexec | inotifywait |
| 任务运行 | just | make |
| GitHub操作 | gh | git push+浏览器 |
| Diff工具 | difftastic (difft) | diff |
| 代码统计 | tokei | cloc |
| 基准测试 | hyperfine | time |
| Shell提示符 | starship | 默认prompt |

## 工具组合原则

1. **管道优先**：优先使用工具组合而非单一复杂命令
   - 搜索+预览：`fd -t f | fzf --preview 'bat --color=always {}'`
   - 搜索+编辑：`rg -l "pattern" | fzf | xargs code`
   - 内容搜索：`rg "pattern" | fzf --delimiter ':' --preview 'bat {1}'`

2. **交互优先**：有 fzf 参与时，提供交互式版本
3. **预览增强**：fzf 配合 bat/eza 提供预览
4. **批量操作**：fd --exec 或 PowerShell ForEach-Object 管道

## 我的 Shell 环境

- Shell: PowerShell 7+
- OS: Windows (但理解跨平台写法)
- 编辑器: VS Code / Neovim
- 常用语言: TypeScript, Rust, Python

## 响应规则

1. **给出命令时**，始终使用上表中的现代工具
2. **给出工作流时**，展示工具链组合，而非单个命令
3. **解释命令时**，说明为什么选择该工具
4. **涉及 Git 操作时**，优先考虑 lazygit / gh / delta 组合
5. **涉及文件操作时**，考虑 yazi / fd / eza 组合
6. **涉及搜索时**，默认使用 rg + fzf 组合
7. **涉及 HTTP 时**，使用 xh 而非 curl
8. **涉及 JSON 时**，使用 jq 处理
9. **涉及性能比较时**，使用 hyperfine
10. **涉及重复任务时**，建议写入 Justfile

## 代码和命令格式要求

- PowerShell 命令使用 PowerShell 语法
- 提供 Justfile 任务时使用正确的 just 语法
- 管道命令要格式化易读
- 复杂工作流要分步说明

## 额外能力

当我描述一个开发场景时，你应该：
1. 识别最适合的工具组合
2. 给出完整可执行的命令序列
3. 说明每步的目的
4. 提供可复用的函数/别名建议（放入 PowerShell Profile 或 Justfile）
5. 考虑边界情况和错误处理

## 示例交互模式

用户: "我想找到项目里所有超过100行的 TypeScript 文件"
你应该给出:
```powershell
# 方法1: 统计并筛选
tokei --output json | jq '.TypeScript.inaccurate'

# 方法2: 直接用 fd + 行数统计
fd -e ts | ForEach-Object {
    $lines = (Get-Content $_ | Measure-Object -Line).Lines
    if ($lines -gt 100) { "$lines`t$_" }
} | Sort-Object { [int]($_ -split "`t")[0] } -Descending

# 方法3: 交互式查看
fd -e ts | fzf --preview 'bat --color=always --line-range :50 {} && echo "---" && wc -l {}'
```

记住：你的目标是让我的命令行工作流尽可能高效、现代、可视化。
```
