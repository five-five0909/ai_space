# MSYS2 UCRT64 + Zsh 主力开发环境配置

> **Scoop/vmr 管工具链，MSYS2 只做 shell runtime，Zsh 做交互层，AI CLI 继承统一环境。**
>
> Scoop 路径：`Split-Path (Get-Command scoop.ps1).Source` · MSYS2 路径：`scoop prefix msys2` · vmr/SDK @ `E:\SDK-TOOL`

---

## 架构总览

```
Windows Terminal
├─ PowerShell 7          ← Windows 主力 shell
└─ UCRT64 Zsh            ← AI CLI / bash 脚本专用
   │
   启动链路：
   ubash.ps1 → bash --login → ~/.bashrc → exec zsh
   │
   工具链来源（唯一真相源）：
   Scoop/vmr → node / python / java / git / rg / fd / jq / curl ...
   │
   pacman 只装 3 个：zsh / less / tree
   │
   共享环境文件：~/.ai-cli-env
   bash / zsh / AI CLI 全部 source 同一份
```

---

## 1. 安装 MSYS2

```powershell
scoop install msys2
```

安装后位置：`$(scoop prefix msys2)`

首次初始化（只需一次，进去后直接 `exit`）：

```powershell
& "$(scoop prefix msys2)\msys2_shell.cmd" -defterm -here -no-start -ucrt64
```

---

## 2. 开启 PATH 继承

```powershell
$msys2 = scoop prefix msys2
(Get-Content "$msys2\ucrt64.ini") -replace '#MSYS2_PATH_TYPE=inherit','MSYS2_PATH_TYPE=inherit' | Set-Content "$msys2\ucrt64.ini"
```

验证：

```powershell
Get-Content "$(scoop prefix msys2)\ucrt64.ini"
```

`MSYS2_PATH_TYPE=inherit` 前面没有 `#` 即可。

---

## 3. HOME 统一

让 MSYS2 的 `~` 指向 Windows 用户目录，两个 shell 共享 `.gitconfig`、SSH key 等：

```powershell
[System.Environment]::SetEnvironmentVariable("HOME", $env:USERPROFILE, "User")
```

设置后**重启终端**生效。

> ⚠️ **必须在安装 Oh My Zsh 之前完成此步**。否则 Oh My Zsh 会装到 MSYS2 默认的 `/home/用户名/` 下，而你的 `~` 指向 `C:\Users\用户名`，导致 `.zshrc` 找不到 `.oh-my-zsh` 目录。
>
> 如果已经装反了，修复方法：
>
> ```bash
> # 把 Oh My Zsh 和配置文件从旧 home 搬到新 home
> cp -r /home/Administrator/.oh-my-zsh ~/
> cp /home/Administrator/.bashrc ~/
> cp /home/Administrator/.zshrc ~/
> cp /home/Administrator/.ai-cli-env ~/
> ```

---

## 4. 创建启动入口 ubash.ps1

> **为什么不用 `msys2_shell.cmd`**：它通过 cmd.exe 中转，只拿到系统级 PATH，Scoop/vmr 的用户级 PATH 全部丢失（`node: command not found`）。直接调 bash.exe 从 PowerShell fork，完整继承用户级 PATH。

创建文件 `ubash.ps1`（放到 Scoop shims 目录下）：

```powershell
$shimsDir = Split-Path (Get-Command scoop.ps1).Source
notepad "$shimsDir\ubash.ps1"
```

写入：

```powershell
$env:MSYSTEM = "UCRT64"
$env:CHERE_INVOKING = "1"
$env:MSYS2_PATH_TYPE = "inherit"
$env:UCRT64_START_DIR = (Get-Location).Path

& "$(scoop prefix msys2)\usr\bin\bash.exe" --login
```

> `UCRT64_START_DIR` 会把当前目录传给 bash，配合 `.bashrc` 中的 cd 逻辑，实现右键菜单"在此处打开"的功能。

保存后在 PowerShell 中即可用 `ubash` 进入 UCRT64 bash。

---

## 5. MSYS2 换清华镜像

通过 `ubash` 进入 UCRT64 bash，执行：

```bash
sed -i "s#https\?://mirror.msys2.org/#https://mirrors.tuna.tsinghua.edu.cn/msys2/#g" /etc/pacman.d/mirrorlist*
```

---

## 6. pacman 只装 shell runtime

```bash
pacman -Syu
```

如果提示关闭终端就关掉，重新 `ubash` 进入，再 `pacman -Syu` 一次。

然后只装这 3 个：

```bash
pacman -S --needed zsh less tree
```

验证：

```bash
which zsh && zsh --version
```

**禁止** `pacman -S git nodejs python curl jq` ——这些全部走 Scoop/vmr。

---

## 7. 创建 ~/.ai-cli-env（共享环境文件）

这个文件是整个方案的核心枢纽。bash、zsh、AI CLI 三方全部 source 同一份：

```bash
cat > ~/.ai-cli-env << 'ENVEOF'
# ============================================================
# 共享环境 | bash / zsh / AI CLI 全部 source 这一份
# ============================================================

# 编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 编辑器
export EDITOR=code
export VISUAL=code

# Git
export GIT_OPTIONAL_LOCKS=0

# 避免重复追加 PATH
path_prepend() {
  case ":$PATH:" in
    *":$1:"*) ;;
    *) PATH="$1:$PATH" ;;
  esac
}

# 路径补强（确保 Scoop shims 优先级最高）
# SCOOP 变量由 ubash.ps1 继承，自动适配任意安装目录
if [ -n "$SCOOP" ]; then
    path_prepend "$(cygpath "$SCOOP/shims")"
else
    # 回退：手动指定（按实际安装位置修改）
    path_prepend "/e/Scoop/shims"
fi

# 代理（v2rayN 端口 7897）
proxy_on() {
    export http_proxy="http://127.0.0.1:7897"
    export https_proxy="http://127.0.0.1:7897"
    export all_proxy="socks5://127.0.0.1:7897"
    export no_proxy="localhost,127.0.0.1,::1"
    echo "🌐 代理已开启 (127.0.0.1:7897)"
}

proxy_off() {
    unset http_proxy https_proxy all_proxy no_proxy
    echo "🔒 代理已关闭"
}

# Conda（Anaconda @ E:\SDK-TOOL\anaconda）
CONDA_ROOT="/e/SDK-TOOL/anaconda"
if [ -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]; then
    . "$CONDA_ROOT/etc/profile.d/conda.sh"
fi

# 路径转换
win2unix() { echo "$1" | sed -e 's|\\|/|g' -e 's|^\([A-Za-z]\):|/\L\1|'; }
unix2win() { echo "$1" | sed -e 's|^/\([a-z]\)/|\U\1:\\|' -e 's|/|\\|g'; }

# 临时禁用 MSYS2 路径转换（按需使用）
nopath() { MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" "$@"; }
ENVEOF
```

---

## 8. 创建 ~/.bashrc

```bash
cat > ~/.bashrc << 'BASHEOF'
# MSYS2 UCRT64 bash bootstrap
# 职责：加载共享环境 → 进入 zsh

# 加载共享环境
[ -f "$HOME/.ai-cli-env" ] && source "$HOME/.ai-cli-env"

# bash 基础配置（兜底用，日常在 zsh 里）
HISTSIZE=10000
HISTFILESIZE=20000
HISTCONTROL=ignoredups:erasedups
shopt -s histappend

alias ll='ls -alh --color=auto'

# 交互式 shell 自动进入 zsh
# AI CLI 内部调用 bash -c "xxx" 时不会触发（非交互式）
if [[ $- == *i* ]] && [ -t 1 ] && [ -z "$ZSH_VERSION" ] && command -v zsh >/dev/null 2>&1; then
    # 恢复右键菜单"在此处打开"传入的目录
    if [ -n "$UCRT64_START_DIR" ]; then
        _dir="$UCRT64_START_DIR"
        unset UCRT64_START_DIR
        cd "$_dir" 2>/dev/null
    fi
    # 不用 -l，避免 login shell 重新 cd 到 HOME
    exec zsh
fi
BASHEOF
```

---

## 9. 安装 Oh My Zsh + 插件

先确认 HOME 已经指向 Windows 用户目录：

```bash
echo $HOME
# 应输出 /c/Users/Administrator，不是 /home/Administrator
```

如果不对，回到第 3 步设置 HOME 并重启终端。

```bash
proxy_on

RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

验证 Oh My Zsh 装在了正确位置：

```bash
ls ~/.oh-my-zsh/oh-my-zsh.sh
# 应该存在，如果报 No such file 说明 HOME 没设对
```

---

## 10. 创建 ~/.zshrc

Oh My Zsh 安装时会自动生成 `~/.zshrc`，直接覆盖它：

```bash
cat > ~/.zshrc << 'ZSHEOF'
# ============================================================
# MSYS2 UCRT64 + Oh My Zsh
# Scoop/vmr 管工具链，MSYS2 只做 shell runtime
# ============================================================

export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(
  git
  npm
  node
  python
  pip
  colored-man-pages
  zsh-autosuggestions
  zsh-syntax-highlighting
)

source "$ZSH/oh-my-zsh.sh"

# 加载共享环境（和 bash / AI CLI 同一份）
[ -f "$HOME/.ai-cli-env" ] && source "$HOME/.ai-cli-env"

# 历史记录
HISTSIZE=10000
SAVEHIST=20000
HISTFILE="$HOME/.zsh_history"
setopt APPEND_HISTORY SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE EXTENDED_HISTORY

# 别名
alias ..='cd ..'
alias ...='cd ../..'
alias ll='ls -alh --color=auto'
alias la='ls -A --color=auto'

alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -20'
alias gd='git diff'

alias py='python'
alias pip='python -m pip'
alias ni='npm install'
alias nr='npm run'
alias nrd='npm run dev'

alias dev='cd /e/projects'

# 启动信息
echo ""
echo "🚀 UCRT64 Zsh | Oh My Zsh | $(date '+%Y-%m-%d %H:%M')"
echo "   node $(node -v 2>/dev/null || echo 'N/A') | python $(python --version 2>&1 | cut -d' ' -f2) | git $(git --version 2>/dev/null | cut -d' ' -f3)"
echo ""
ZSHEOF
```

---

## 11. Windows Terminal Profile

设置 → 打开 JSON 文件 → `profiles.list` 添加。

> JSON 不支持动态求值，需要写实际路径。先在 PowerShell 中获取你的实际路径：
>
> ```powershell
> # ubash.ps1 路径
> "$(Split-Path (Get-Command scoop.ps1).Source)\ubash.ps1"
> # icon 路径
> "$(scoop prefix msys2)\ucrt64.ico"
> ```
>
> 把输出结果替换到下面 JSON 中（注意正斜杠）。

```json
{
    "guid": "{17da3cac-b318-431e-8a3e-7fcdefe6d114}",
    "name": "UCRT64 Zsh",
    "commandline": "powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File E:/Scoop/shims/ubash.ps1",
    "icon": "E:/Scoop/apps/msys2/current/ucrt64.ico",
    "font": {
        "face": "JetBrainsMono Nerd Font",
        "size": 14
    }
}
```

> 不设 `startingDirectory`，这样右键菜单"在此处打开终端"会进入对应目录。从开始菜单打开则默认到用户目录。

---

## 12. VS Code 集成

`Ctrl+Shift+P` → `Open User Settings (JSON)`，添加：

> 同样需要写实际路径。获取方式：`Split-Path (Get-Command scoop.ps1).Source` + `\ubash.ps1`，注意双反斜杠转义。

```json
{
    "terminal.integrated.profiles.windows": {
        "UCRT64 Zsh": {
            "path": "powershell.exe",
            "args": [
                "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", "E:\\Scoop\\shims\\ubash.ps1"
            ]
        }
    }
}
```

---

## 13. Warp 终端集成

Tab Config 文件位置：`~\AppData\Roaming\openwarp\OpenWarp\data\tab_configs\`

创建或编辑 `.toml` 文件，写入：

```toml
name = "UCRT64 Zsh"
title = "UCRT64 Zsh"
[[panes]]
id = "p1"
type = "terminal"
is_focused = true
shell = "powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File E:/Scoop/shims/ubash.ps1"
```

> 不设 `directory` 字段，Warp 会使用当前工作目录。

> `ubash.ps1` 路径同样需要替换为实际路径，获取方式：`"$(Split-Path (Get-Command scoop.ps1).Source)\ubash.ps1"`

---

## 14. Pi CLI 配置

安装：

```bash
npm install -g @earendil-works/pi-coding-agent
```

如果 Pi 找不到 bash，手动指定（在 PowerShell 中执行）：

```powershell
$bashPath = "$(scoop prefix msys2)\usr\bin\bash.exe" -replace '\\','\\'
New-Item -Path "$env:USERPROFILE\.pi\agent" -ItemType Directory -Force | Out-Null
@"
{
    "shellPath": "$bashPath"
}
"@ | Set-Content "$env:USERPROFILE\.pi\agent\settings.json"
```

最稳方式是从 UCRT64 Zsh 里直接 `pi`，Pi 会继承当前环境。

---

## 验证清单

打开 Windows Terminal 的 UCRT64 Zsh tab：

```bash
# shell 环境
echo "SHELL=$SHELL  ZSH=$ZSH_VERSION  MSYSTEM=$MSYSTEM"

# 工具链来源（应全部来自 Scoop/vmr，bash/zsh 来自 /usr/bin 正常）
for x in bash zsh node npm python git java mvn rg fd jq curl; do
  printf "%-8s -> " "$x"
  command -v "$x" || echo "NOT FOUND"
done

# 版本
node -v && python --version && git --version

# PATH 前 15 项
echo "$PATH" | tr ':' '\n' | head -15

# AI CLI
which claude
which pi
```

预期：

```
node     -> /e/SDK-TOOL/versions/node_versions/node/node
npm      -> /e/SDK-TOOL/versions/node_versions/node/npm
python   -> /e/SDK-TOOL/versions/python_versions/python/python
git      -> /e/Scoop/shims/git
java     -> /e/SDK-TOOL/versions/jdk_versions/jdk/bin/java
rg       -> /e/Scoop/shims/rg
bash     -> /usr/bin/bash
zsh      -> /usr/bin/zsh
```

---

## AI CLI 使用

从 UCRT64 Zsh 里启动，自动继承整个环境：

```bash
pi          # Pi CLI
claude      # Claude Code
opencode    # OpenCode
cline       # Cline CLI
```

AI CLI 看到的是 PATH 里的真实命令，不是 alias。不要期待它理解 `ni`/`gs`，它会直接跑 `npm install`/`git status`。

---

## 路径转换

不全局禁用 `MSYS_NO_PATHCONV`，按需使用 `.ai-cli-env` 中定义的 `nopath` 函数：

```bash
# 普通命令正常用
curl https://api.example.com/v1/users

# 如果路径被误转，加 nopath
nopath curl https://api.example.com/v1/users

# 给 Windows 原生程序传路径
node "$(cygpath -w ./script.js)"
```

---

## 升级维护

```powershell
# Scoop 全量更新
scoop update *
```

```bash
# MSYS2 runtime 更新（在 UCRT64 里）
pacman -Syu

# 检查是否误装了开发工具链到 pacman（应该没输出）
pacman -Q | grep -E 'node|python|git|curl|jq|gcc|mingw'
```

Scoop 更新 MSYS2 后 `ucrt64.ini` 可能被覆盖，PowerShell `$PROFILE` 中加：

```powershell
function Update-MSYS2 {
    scoop update msys2
    $ini = "$(scoop prefix msys2)\ucrt64.ini"
    (Get-Content $ini) -replace '#MSYS2_PATH_TYPE=inherit','MSYS2_PATH_TYPE=inherit' | Set-Content $ini
    Write-Host "✅ MSYS2 已更新，PATH 继承已恢复" -ForegroundColor Green
}
```

> 实际上 `ubash.ps1` 已经注入了 `MSYS2_PATH_TYPE=inherit`，ini 被覆盖不影响启动。但保持正确是好习惯。

---

## 日常工作流

| 场景 | 推荐 Shell | 说明 |
|---|---|---|
| Windows 系统管理 | PowerShell 7 | 原生命令最稳 |
| Spring Boot / Java | PowerShell 7 或 UCRT64 Zsh | Java 工具链来自 Scoop/vmr |
| Vue / React / Node | UCRT64 Zsh | npm/pnpm/bun 可用 |
| Pi / Claude Code / Cline | UCRT64 Zsh | 从 zsh 启动继承环境 |
| Python / Conda | 两边都行 | bash 中 conda 已初始化 |
| Git 操作 | 两边都行 | 同一个 git |
| bash 脚本 | UCRT64 Zsh / bash | 可以用 |

---

## 边界：什么时候用 WSL2

| 用 UCRT64 Zsh | 用 WSL2 |
|---|---|
| Spring Boot / Vue / React | Docker-heavy 项目 |
| npm/pnpm/bun 前端开发 | Makefile-heavy 项目 |
| Pi / Claude Code / Cline CLI | Linux CI 复现 |
| Python 日常脚本 | native C/C++ dependency |
| Git 操作 | systemd / Linux daemon |
| 简单 bash 脚本 | PISFM 深度学习训练（GPU） |
