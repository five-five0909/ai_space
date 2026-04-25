# WSL2 Zsh 安装与配置完全指南

## 一、安装 Zsh

```bash
sudo apt update && sudo apt install -y zsh

# 验证
zsh --version

# 设为默认 shell
chsh -s $(which zsh)

# 重启终端后生效，验证
echo $SHELL
```

---

## 二、安装 Oh My Zsh

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

安装完自动生成 `~/.zshrc`，Oh My Zsh 插件目录在：
```
~/.oh-my-zsh/plugins/        # 内置插件
~/.oh-my-zsh/custom/plugins/ # 第三方插件
```

---

## 三、主题配置

### 3.1 内置主题（开箱即用）

编辑 `~/.zshrc`：
```bash
ZSH_THEME="agnoster"   # 常用选项：robbyrussell / agnoster / fino / bira
```

### 3.2 Powerlevel10k（推荐，最强主题）

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
    ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

`~/.zshrc` 中设置：
```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
```

重启终端后自动进入配置向导，或手动触发：
```bash
p10k configure
```

> 需要安装 Nerd Font 字体，推荐 MesloLGS NF，在 Windows Terminal 字体设置里选择

---

## 四、必装插件

### 4.1 内置插件（直接启用，无需安装）

编辑 `~/.zshrc` 的 plugins 行：

```bash
plugins=(
    git                  # git 命令缩写，最常用
    z                    # 目录快速跳转，cd 的替代
    extract              # 万能解压，x xxx.tar.gz
    sudo                 # 双击 ESC 自动加 sudo
    docker               # docker 命令补全
    docker-compose       # docker-compose 补全
    conda                # conda 环境提示
    node                 # node 版本提示
    npm                  # npm 命令补全
    pip                  # pip 命令补全
    python               # python 命令补全
    mvn                  # maven 命令补全
    gradle               # gradle 命令补全
    copypath             # 复制当前路径到剪贴板
    copyfile             # 复制文件内容到剪贴板
    dirhistory           # alt+左右 切换目录历史
    history              # 历史命令搜索
    jsontools            # json 格式化工具
    web-search           # 终端直接搜索 google bing
)
```

### 4.2 第三方插件（需要安装）

**zsh-autosuggestions（命令自动补全建议，必装）**
```bash
git clone https://github.com/zsh-users/zsh-autosuggestions \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

**zsh-syntax-highlighting（命令语法高亮，必装）**
```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

**zsh-completions（更多命令补全）**
```bash
git clone https://github.com/zsh-users/zsh-completions \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions
```

**zsh-history-substring-search（上下键搜索历史）**
```bash
git clone https://github.com/zsh-users/zsh-history-substring-search \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
```

**autojump（比 z 更智能的目录跳转）**
```bash
sudo apt install -y autojump
```

安装完成后 plugins 加入所有第三方插件：
```bash
plugins=(
    git z extract sudo
    docker docker-compose
    conda node npm pip python
    mvn gradle
    copypath copyfile
    dirhistory history
    jsontools web-search
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
    zsh-history-substring-search
    autojump
)
```

---

## 五、实用 zshrc 配置

在 `~/.zshrc` 末尾追加：

```bash
# ── 历史记录 ────────────────────────────────
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt HIST_IGNORE_DUPS      # 忽略重复命令
setopt HIST_IGNORE_SPACE     # 忽略空格开头的命令
setopt SHARE_HISTORY         # 多终端共享历史

# ── 补全增强 ────────────────────────────────
autoload -U compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'  # 补全忽略大小写

# ── 常用别名 ────────────────────────────────
alias ll='ls -alF'
alias la='ls -A'
alias cls='clear'
alias zshrc='vim ~/.zshrc'
alias src='source ~/.zshrc'
alias update='sudo apt update && sudo apt upgrade -y'

# ── WSL2 动态代理 ───────────────────────────
export HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
export http_proxy="http://${HOST_IP}:7897"
export https_proxy="http://${HOST_IP}:7897"
export no_proxy="localhost,127.0.0.1"

# ── npm 全局包自动同步 hook ─────────────────
npm() {
    command npm "$@"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        if [[ "$*" == *"-g"* || "$*" == *"--global"* ]]; then
            if [[ "$1" =~ ^(install|i|uninstall|un|link|ln)$ ]]; then
                echo ">>> 自动同步 npm 全局包..."
                sudo /usr/local/bin/sync-npm-global-tool.sh
            fi
        fi
    fi
    return $exit_code
}
```

生效：
```bash
source ~/.zshrc
```

---

## 六、常用快捷键

| 快捷键 | 功能 |
|---|---|
| `Tab` | 补全命令/路径 |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + A` | 光标移到行首 |
| `Ctrl + E` | 光标移到行尾 |
| `Ctrl + U` | 清空当前行 |
| `Ctrl + L` | 清屏 |
| `ESC ESC` | 自动加 sudo |
| `Alt + ←/→` | 目录历史前进后退 |
| `↑` | 历史命令搜索（装了 history-substring-search）|

---

## 七、Oh My Zsh 常用命令

```bash
# 更新 Oh My Zsh
omz update

# 查看所有内置主题
ls ~/.oh-my-zsh/themes/

# 查看所有内置插件
ls ~/.oh-my-zsh/plugins/

# 重载配置
source ~/.zshrc
```

---

## 八、故障排查

```bash
# 插件报错，检查是否正确克隆
ls ~/.oh-my-zsh/custom/plugins/

# 主题乱码，检查字体
p10k configure

# 补全不生效
rm -f ~/.zcompdump && compinit

# 查看当前加载的插件
echo $plugins
```

---

# WSL2 npm 全局包自动同步方案

## 原理

npm 根据安装方式不同，全局包会放在不同路径。通过自动探测所有可能路径，软链接到 `/usr/local/bin`，让任何 shell 环境都能访问。

---

## 覆盖的 Node 安装方式

| 安装方式 | 全局包路径 |
|---|---|
| nvm | `~/.nvm/versions/node/<version>/bin` |
| apt | `/usr/bin` |
| 官网二进制 | `/usr/local/bin` |
| volta | `~/.volta/bin` |
| fnm | `~/.fnm/node-versions/<version>/installation/bin` |
| homebrew | `/home/linuxbrew/.linuxbrew/bin` |

---

## 第一步：创建同步脚本

```bash
sudo tee /usr/local/bin/sync-npm-global-tool.sh <<'EOF'
#!/bin/bash

# ── 自动探测所有 node 安装方式 ──────────────────────

find_npm_global_bin() {

    # 方式1: nvm 当前激活版本（最优先）
    if [ -n "$NVM_BIN" ] && [ -d "$NVM_BIN" ]; then
        echo "$NVM_BIN"
        return
    fi

    # 方式2: nvm default alias
    if [ -f "/root/.nvm/alias/default" ]; then
        local ver=$(cat /root/.nvm/alias/default)
        # 处理 lts/* 这种别名
        if [[ "$ver" == lts/* ]]; then
            ver=$(cat "/root/.nvm/alias/${ver}" 2>/dev/null)
        fi
        local path="/root/.nvm/versions/node/${ver}/bin"
        [ -d "$path" ] && echo "$path" && return
    fi

    # 方式3: nvm 已安装中最新版本
    local nvm_latest=$(ls -d /root/.nvm/versions/node/*/bin 2>/dev/null \
        | sort -t'v' -k2 -V | tail -1)
    [ -n "$nvm_latest" ] && echo "$nvm_latest" && return

    # 方式4: volta
    if [ -d "$HOME/.volta/bin" ]; then
        echo "$HOME/.volta/bin"
        return
    fi

    # 方式5: fnm
    local fnm_latest=$(ls -d $HOME/.fnm/node-versions/*/installation/bin 2>/dev/null \
        | sort -V | tail -1)
    [ -n "$fnm_latest" ] && echo "$fnm_latest" && return

    # 方式6: homebrew on linux
    if [ -f "/home/linuxbrew/.linuxbrew/bin/npm" ]; then
        echo "/home/linuxbrew/.linuxbrew/bin"
        return
    fi

    # 方式7: npm prefix（apt 或手动安装兜底）
    if command -v npm &>/dev/null; then
        local prefix=$(npm config get prefix 2>/dev/null)
        [ -n "$prefix" ] && [ -d "${prefix}/bin" ] && echo "${prefix}/bin" && return
    fi

    # 方式8: 系统路径 fallback
    for path in /usr/local/bin /usr/bin; do
        [ -f "$path/npm" ] && echo "$path" && return
    done
}

GLOBAL_BIN=$(find_npm_global_bin)

if [ -z "$GLOBAL_BIN" ] || [ ! -d "$GLOBAL_BIN" ]; then
    echo "[sync] ❌ 未找到任何 node 安装路径"
    exit 1
fi

echo "[sync] 检测到路径: $GLOBAL_BIN"
echo "[sync] 开始同步全局包到 /usr/local/bin..."

synced=0
skipped=0

for bin in "$GLOBAL_BIN"/*; do
    name=$(basename "$bin")

    # 跳过 node 核心工具
    [[ "$name" =~ ^(node|npm|npx|corepack|npm-cli\.js|node_modules)$ ]] && \
        ((skipped++)) && continue

    # 跳过非可执行文件
    [ -x "$bin" ] || continue

    ln -sf "$bin" /usr/local/bin/"$name"
    echo "  ✓ $name"
    ((synced++))
done

echo ""
echo "[sync] 完成！同步 ${synced} 个，跳过 ${skipped} 个"
echo "[sync] 路径来源: $GLOBAL_BIN"
EOF

sudo chmod +x /usr/local/bin/sync-npm-global-tool.sh
```

---

## 第二步：开机自动执行（systemd）

```bash
sudo tee /etc/systemd/system/sync-npm-global-tool.service <<EOF
[Unit]
Description=Sync npm global tools to /usr/local/bin
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/sync-npm-global-tool.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable sync-npm-global-tool.service
sudo systemctl start sync-npm-global-tool.service
```

---

## 触发场景覆盖

| 场景 | 触发方式 |
|---|---|
| WSL2 每次启动 | systemd 服务自动执行 |
| `npm install -g xxx` | zshrc hook 自动触发 |
| `npm i -g xxx` | zshrc hook 自动触发 |
| `npm uninstall -g xxx` | zshrc hook 自动触发 |
| `npm link` | zshrc hook 自动触发 |
| 安装失败 | 不触发（检查 exit code）|
| 手动执行 | `sudo sync-npm-global-tool.sh` |

---

## 验证

```bash
# 查看同步结果
sudo /usr/local/bin/sync-npm-global-tool.sh

# 验证 claude 是否可用
which claude
claude --version

# 查看 systemd 服务状态
sudo systemctl status sync-npm-global-tool.service
```

---

## 注意事项

- nvm 切换版本后（`nvm use xx`），需手动执行一次同步
- 如果用 volta/fnm，切换版本同理
- 卸载工具后 `/usr/local/bin` 里的软链接会变成死链，同步脚本重跑会覆盖，不影响使用
