# /install-psmux

安装 psmux 工具。

## 适用场景

- 首次使用项目实验系统
- 后台任务管理器缺失
- 准备启动长时间实验

## 检测步骤

### 1. 检查是否已安装

```powershell
$psmux = Get-Command psmux -ErrorAction SilentlyContinue

if ($psmux) {
    Write-Output "psmux 已安装: $($psmux.Source)"
    psmux --version
    return
}
```

### 2. 检测包管理器

按优先级检测：

```powershell
$scoop = Get-Command scoop -ErrorAction SilentlyContinue
$winget = Get-Command winget -ErrorAction SilentlyContinue
$choco = Get-Command choco -ErrorAction SilentlyContinue

Write-Output "可用包管理器:"
if ($scoop) { Write-Output "  - scoop: 可用" }
if ($winget) { Write-Output "  - winget: 可用" }
if ($choco) { Write-Output "  - choco: 可用" }
```

## 安装流程

### 方案 A: Scoop（首选）

#### 1. 检查 psmux 是否在 scoop bucket 中

```powershell
scoop search psmux
```

如果在：

```powershell
scoop install psmux
```

#### 2. 如果不在 scoop 中

检查 GitHub 仓库：

```powershell
# 确认 git 可用
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Output "安装 git..."
    scoop install git
}

# 克隆仓库
Write-Output "从 GitHub 克隆 psmux..."
git clone https://github.com/psmux/psmux.git "$env:USERPROFILE\psmux"

# 查看 README 确认安装方式
Get-Content "$env:USERPROFILE\psmux\README.md"
```

**重要**: 必须先查看 README 中的安装说明，不能假设安装方式。

常见安装模式：

1. **PowerShell 模块**:
   ```powershell
   Copy-Item -Recurse "$env:USERPROFILE\psmux\module" "$env:USERPROFILE\Documents\PowerShell\Modules\psmux"
   ```

2. **添加到 PATH**:
   ```powershell
   # 添加到用户 PATH
   $path = [Environment]::GetEnvironmentVariable("Path", "User")
   $newPath = "$env:USERPROFILE\psmux\bin"
   if ($path -notlike "*$newPath*") {
       [Environment]::SetEnvironmentVariable("Path", "$path;$newPath", "User")
   }
   ```

3. **安装脚本**:
   ```powershell
   & "$env:USERPROFILE\psmux\install.ps1"
   ```

### 方案 B: Winget

```powershell
winget search psmux
```

如果存在：

```powershell
winget install psmux
```

### 方案 C: Chocolatey

```powershell
choco search psmux
```

如果存在：

```powershell
choco install psmux -y
```

### 方案 D: 手动安装

如果自动安装都不可用：

1. 访问 https://github.com/psmux/psmux/releases
2. 下载最新 release
3. 解压到 `$env:USERPROFILE\psmux`
4. 按照 README 配置

## 验证安装

```powershell
# 重新加载环境
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 验证
Get-Command psmux
psmux --version
psmux --help
```

## 降级方案

如果 psmux 无法安装：

```powershell
Write-Warning "psmux 安装失败，将使用 Start-Process 作为降级方案"
Write-Output "降级限制:"
Write-Output "  - 无法持久化管理多个会话"
Write-Output "  - 无法在终端关闭后恢复"
Write-Output "  - 需要手动记录 PID"

# 使用降级启动方式
$launcher_type = "start-process"
```

## 安装后配置

### 创建默认配置

```powershell
# psmux 配置目录
$configDir = "$env:USERPROFILE\.psmux"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir
}

# 默认配置
$config = @{
    defaultShell = "powershell"
    sessionDir = "$env:USERPROFILE\.psmux\sessions"
    logDir = "$env:USERPROFILE\.psmux\logs"
}

$config | ConvertTo-Json | Out-File "$configDir\config.json"
```

## 常用命令速查

安装完成后，确认以下命令可用：

```powershell
# 创建新会话
psmux new -n <session_name> -- <command>

# 列出会话
psmux list

# 连接到会话
psmux attach -n <session_name>

# 分离会话
# Ctrl+B, D (或按照实际配置)

# 终止会话
psmux kill -n <session_name>

# 查看帮助
psmux --help
```

## 故障排除

### 权限问题

```powershell
# 检查执行策略
Get-ExecutionPolicy

# 如果受限，设置宽松策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PATH 问题

```powershell
# 检查 PATH
$env:Path -split ';' | Where-Object { $_ -like "*psmux*" }

# 手动添加
$env:Path += ";<psmux_install_dir>"
```

### 版本冲突

```powershell
# 检查已安装版本
psmux --version

# 如果需要更新
scoop update psmux
# 或重新从 GitHub 安装
```

## 返回值

```
psmux 安装状态: <已安装/未安装/安装失败>
安装方式: <scoop/winget/choco/manual/none>
可执行路径: <path>
版本: <version>
降级方案: <start-process>
```