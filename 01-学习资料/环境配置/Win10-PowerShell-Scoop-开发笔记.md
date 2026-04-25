# Win 10 开发者 PowerShell + Scoop 完整指南

> 目标：用 PowerShell 作为日常开发终端，配合 Scoop 管理工具链，全部装在 E 盘，适合 AI CLI / Claude Code / Git / Node / Python 开发。
> 最后更新：2026-04-09

---

## 目录

1. [PowerShell 基本特点](#一powershell-基本特点速览)
2. [基础操作速查表](#二powershell-基础操作速查表)
3. [开发查询命令](#三开发查询命令一览)
4. [管道操作](#四管道操作核心用法)
5. [进程与服务管理](#五进程与服务管理)
6. [网络与接口调试](#六网络与接口调试)
7. [环境变量管理](#七环境变量管理)
8. [实用开发操作](#八实用开发操作)
9. [自定义别名配置](#九自定义别名配置重要)
10. [开发增强工具](#十开发增强工具一览)
11. [Scoop 包管理](#十一scoop-常用命令完整一览)
12. [NSSM 服务管理](#十二nssm-使用完全指南)
13. [开发者高频组合](#十三开发者日常高频组合)
14. [PROFILE 增强配置](#十四profile-增强配置推荐)
15. [优先记忆清单](#十五建议优先记住的命令清单)
16. [日常开发操作流](#十六日常开发操作流)
17. [三层架构总结](#十七总结powershell-使用三层架构)
18. [Scoop + PowerShell 一键迁移指南](#十八scoop--powershell-开发环境一键迁移指南)
19. [常见问题排查](#附录常见问题排查)

---

### 一、PowerShell 基本特点速览

| 特点 | 说明 | 示例 |
| --- | --- | --- |
| 命令风格 | 采用「动词-名词」结构 | `Get-ChildItem`、`Set-Location`、`Get-Command` |
| 别名丰富 | 支持 Linux 风格简写 | `ls` = `Get-ChildItem`，`cd` = `Set-Location`，`cat` = `Get-Content` |
| 管道强大 | 传递的是对象，不只是纯文本 | 可直接 `Select-Object`、`Where-Object`、`Sort-Object` |

---

### 二、PowerShell 基础操作速查表

#### 2.1 目录与路径操作

| 序号 | 功能 | 标准写法 | 简写 | 示例 |
| --- | --- | --- | --- | --- |
| 1 | 看当前目录 | `Get-Location` | `pwd` | 查看当前所在路径 |
| 2 | 列出当前目录文件 | `Get-ChildItem` | `ls` / `dir` | 查看当前目录下的文件和文件夹 |
| 3 | 进入目录 | `Set-Location .\demo-project` | `cd .\demo-project` | 进入 `demo-project` 目录 |
| 3.1 | 返回上一级 | `Set-Location ..` | `cd ..` | 返回父目录 |
| 3.2 | 返回上两级 | `Set-Location ..\..` | `cd ..\..` | 返回上两层目录 |
| 3.3 | 跳到指定盘符 | `Set-Location E:\` | `cd E:\` | 跳到 E 盘根目录 |

#### 2.2 文件创建与删除

| 序号 | 功能 | 标准写法 | 简写 | 示例 |
| --- | --- | --- | --- | --- |
| 4 | 创建目录 | `New-Item -ItemType Directory test-project` | `mkdir test-project` | 新建文件夹 |
| 5 | 创建文件 | `New-Item -ItemType File .\index.js` | `ni .\index.js` | 新建文件 |
| 5.1 | 一次创建多个文件 | `New-Item app.js, README.md, .gitignore` | `ni app.js, README.md, .gitignore` | 一次创建多个文件 |
| 6 | 查看文件内容 | `Get-Content .\README.md` | `cat .\README.md` | 查看文件全文 |
| 6.1 | 查看最后 20 行 | `Get-Content .\README.md -Tail 20` | 无 | 常用于查看日志尾部 |
| 6.2 | 持续追踪日志 | `Get-Content .\app.log -Wait` | 无 | 类似 `tail -f` |
| 7 | 覆盖写入文件 | `Set-Content .\note.txt "hello powershell"` | 无 | 会覆盖原内容 |
| 7.1 | 追加写入文件 | `Add-Content .\note.txt "second line"` | 无 | 在原内容后追加 |
| 8 | 复制文件 | `Copy-Item .\README.md .\README.bak.md` | `cp .\README.md .\README.bak.md` | 复制文件 |
| 8.1 | 移动 / 重命名文件 | `Move-Item .\old.txt .\new.txt` | `mv .\old.txt .\new.txt` | 可用于移动或改名 |
| 8.2 | 删除文件 | `Remove-Item .\test.txt` | `rm .\test.txt` | 删除单个文件 |
| 8.3 | 删除目录 | `Remove-Item .\dist -Recurse -Force` | 无 | 强制递归删除文件夹 |

---

### 三、开发查询命令一览

| 序号 | 功能 | 命令 | 示例说明 |
| --- | --- | --- | --- |
| 1 | 查命令来自哪里 | `Get-Command git` | 查看当前终端实际调用的是哪个 `git` |
| 2 | 查命令帮助 | `Get-Help Get-ChildItem` | 查看某个命令的基础帮助 |
| 2.1 | 查看详细帮助 | `Get-Help Get-ChildItem -Full` | 显示完整帮助信息 |
| 2.2 | 只看示例 | `Get-Help Get-ChildItem -Examples` | 只看命令用法示例 |
| 3 | 搜索文本内容 | `Select-String -Path .\*.md -Pattern "Scoop"` | 在当前目录的 `.md` 文件中搜索关键词 |
| 4 | 查找文件 | `Get-ChildItem -Recurse -Filter *.js` | 递归查找当前目录下所有 `.js` 文件 |
| 4.1 | 只看文件完整路径 | `Get-ChildItem -Recurse -Filter *.js | Select-Object FullName` | 只输出文件完整路径 |
| 5 | 统计文件数量 | `(Get-ChildItem -Recurse -Filter *.js).Count` | 统计 `.js` 文件数量 |
| 5.1 | 统计文本行数 | `Get-Content .\README.md | Measure-Object -Line` | 统计某个文件的总行数 |

---

### 四、管道操作核心用法

| 序号 | 功能 | 命令 | 示例说明 |
| --- | --- | --- | --- |
| 1 | 列出文件后再筛选 | `Get-ChildItem | Where-Object { $_.Name -like "*.md" }` | 先列出文件，再筛选 `.md` 文件 |
| 1.1 | 简写风格筛选文件 | `ls | Where-Object { $_.Name -like "*.md" }` | 用 `ls` 代替 `Get-ChildItem` |
| 2 | 只取某些字段 | `Get-ChildItem | Select-Object Name, Length, LastWriteTime` | 只显示需要的字段 |
| 2.1 | 简化查看字段 | `ls | Select-Object Name, Length` | 只看文件名和大小 |
| 3 | 排序 | `Get-ChildItem | Sort-Object Length -Descending` | 按文件大小从大到小排序 |
| 4 | 过滤进程 | `Get-Process | Where-Object { $_.ProcessName -like "*code*" }` | 查找名称里带 `code` 的进程 |

---

### 五、进程与服务管理

| 序号 | 功能 | 命令 | 说明 |
| --- | --- | --- | --- |
| 1 | 查看所有进程 | `Get-Process` | 查看当前系统进程 |
| 1.1 | 查看指定进程 | `Get-Process node` | 查看 `node` 进程 |
| 2 | 按名称结束进程 | `Stop-Process -Name node -Force` | 强制结束指定进程 |
| 2.1 | 按 PID 结束进程 | `Stop-Process -Id 12345 -Force` | 根据进程 ID 结束 |
| 3 | 启动程序 | `Start-Process notepad` | 启动记事本 |
| 3.1 | 打开当前目录 | `Start-Process .` | 在资源管理器中打开当前目录 |
| 3.2 | 用 VS Code 打开当前目录 | `code .` | 快速进入项目开发 |

---

### 六、网络与接口调试

| 序号 | 功能 | 标准写法 | 简写 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | 请求接口 | `Invoke-RestMethod https://api.github.com/repos/microsoft/terminal` | `irm https://api.github.com/repos/microsoft/terminal` | 获取 JSON 接口数据 |
| 1.1 | 请求接口后取字段 | `$repo = irm https://api.github.com/repos/microsoft/terminal`<br>`$repo.full_name`<br>`$repo.stargazers_count` | 无 | 适合调试 API |
| 2 | 下载文件 | `Invoke-WebRequest https://example.com/file.zip -OutFile .\file.zip` | `iwr https://example.com/file.zip -OutFile .\file.zip` | 下载文件到本地 |
| 3 | 查看端口占用 | `netstat -ano | findstr :3000` | 无 | 查 Node / Vite / Next.js 端口冲突很常用 |

---

### 七、环境变量管理

| 序号 | 功能 | 命令 | 说明 |
| --- | --- | --- | --- |
| 1 | 查看 Path 环境变量 | `$env:Path` | 查看当前环境变量 |
| 1.1 | 查看 Node 环境变量 | `$env:NODE_ENV` | 查看 `NODE_ENV` |
| 2 | 临时设置环境变量 | `$env:NODE_ENV = "development"` | 只对当前 PowerShell 会话生效 |
| 3 | 永久设置用户环境变量 | `[Environment]::SetEnvironmentVariable("MY_TOOLS", "E:\Tools", "User")` | 写入用户级环境变量 |
| 3.1 | 永久设置系统环境变量 | `[Environment]::SetEnvironmentVariable("MY_TOOLS", "E:\Tools", "Machine")` | 写入系统级环境变量，通常要管理员权限 |

---

### 八、实用开发操作

| 序号 | 功能 | 命令 | 说明 |
| --- | --- | --- | --- |
| 1 | 执行脚本 | `.\build.ps1` | 执行当前目录脚本 |
| 2 | 查看配置文件路径 | `$PROFILE` | 查看当前 PowerShell 配置文件路径 |
| 2.1 | 打开配置文件 | `notepad $PROFILE` | 编辑 PowerShell 配置 |
| 3 | 重新加载配置文件 | `. $PROFILE` | 改完配置后立即生效 |
| 4 | 查看所有别名 | `Get-Alias` | 查看系统中的命令别名 |
| 4.1 | 查看某个别名 | `Get-Alias ls` | 查看 `ls` 对应的真实命令 |

---

### 九、自定义别名配置（重要）

#### 9.1 推荐设置的常用别名

| 原命令 | 建议别名 | 设置命令 | 用途 |
| --- | --- | --- | --- |
| `Get-Command` | `whereis` | `Set-Alias -Name whereis -Value Get-Command` | 查命令来源 |
| `Get-Content` | `cat` | `Set-Alias -Name cat -Value Get-Content` | 查看文件内容 |
| `Get-ChildItem` | `ls` | `Set-Alias -Name ls -Value Get-ChildItem` | 列出目录文件 |
| `Set-Location` | `cd` | `Set-Alias -Name cd -Value Set-Location` | 切换目录 |
| `Remove-Item` | `rm` | `Set-Alias -Name rm -Value Remove-Item` | 删除文件 |
| `Copy-Item` | `cp` | `Set-Alias -Name cp -Value Copy-Item` | 复制文件 |
| `Move-Item` | `mv` | `Set-Alias -Name mv -Value Move-Item` | 移动文件 |
| `New-Item` | `ni` | `Set-Alias -Name ni -Value New-Item` | 新建文件/目录 |
| `Select-String` | `grep` | `Set-Alias -Name grep -Value Select-String` | 搜索文本 |
| `Invoke-RestMethod` | `curl` | `Set-Alias -Name curl -Value Invoke-RestMethod` | 请求接口 |

#### 9.2 完整别名配置文件

将以下内容添加到 `$PROFILE` 文件末尾：

```powershell
# ========== 别名设置 ==========

# 基础命令别名
Set-Alias -Name whereis -Value Get-Command
Set-Alias -Name cat -Value Get-Content
Set-Alias -Name ls -Value Get-ChildItem
Set-Alias -Name cd -Value Set-Location
Set-Alias -Name rm -Value Remove-Item
Set-Alias -Name cp -Value Copy-Item
Set-Alias -Name mv -Value Move-Item
Set-Alias -Name ni -Value New-Item
Set-Alias -Name grep -Value Select-String
Set-Alias -Name curl -Value Invoke-RestMethod

# ========== 自定义函数 ==========

# whereis 函数 - 快速查看命令来源
function whereis($name) {
    Get-Command $name -ErrorAction SilentlyContinue |
    Select-Object Name, Source, Version | Format-Table -AutoSize
}

# 简化版 grep 函数
function grep($pattern, $path = ".") {
    Select-String -Path $path -Pattern $pattern
}
```

#### 9.3 别名使用示例

| 命令 | 作用 | 说明 |
| --- | --- | --- |
| `whereis git` | 查看 git 来自哪里 | 快速定位命令路径 |
| `whereis node` | 查看 node 来自哪里 | 检查环境配置 |
| `whereis claude` | 查看 claude 来自哪里 | AI 工具定位 |
| `grep "TODO" *.ps1` | 在当前目录搜索 TODO | 快速找到待办事项 |
| `curl https://api.github.com` | 请求接口 | 获取 JSON 数据 |

---

### 十、开发增强工具一览

| 工具 | 常用命令 | 作用 | 说明 |
| --- | --- | --- | --- |
| `rg` | `rg "useEffect"` | 全文搜索 | 搜索关键词 |
| `rg` | `rg "console\.log"` | 递归搜索 | 搜索特定语句 |
| `rg` | `rg "TODO" -g "*.ts"` | 按文件类型搜索 | 只搜索 `.ts` 文件 |
| `rg` | `rg "axios" .\` | 实战搜索 | 比 `Select-String` 更快 |
| `fd` | `fd config` | 按文件名查找 | 查找包含 `config` 的文件 |
| `fd` | `fd -e ts` | 按扩展名查找 | 查找所有 `.ts` 文件 |
| `fd` | `fd package.json` | 精确查找 | 查 `package.json` |
| `bat` | `bat .\README.md` | 查看文件 | 带高亮显示 |
| `bat` | `bat .\package.json` | 看配置文件 | 更适合开发场景 |
| `fzf` | `fd | fzf` | 模糊搜索 | 文件列表 + 交互筛选 |
| `erdtree` | `erd` | 看目录树 | 快速理解项目结构 |
| `erdtree` | `erdtree` | 看当前目录树 | 功能同上 |
| `jq` | `Get-Content .\package.json | jq` | 格式化 JSON | 更易读 |
| `jq` | `Get-Content .\package.json | jq ".scripts"` | 提取字段 | 获取某个 JSON 字段 |

---

### 十一、Scoop 常用命令完整一览

> Scoop — Windows 命令行包管理器，像 Linux apt/brew 一样优雅地管理软件。

#### 11.1 核心命令速查

| 序号 | 功能 | 命令 | 说明 |
| --- | --- | --- | --- |
| 1 | 查看 Scoop 版本 | `scoop --version` | 检查是否安装成功 |
| 1.1 | 查看 Scoop 路径 | `$env:SCOOP` `$env:SCOOP_GLOBAL` | 查看用户和全局安装路径 |
| 2 | 搜索软件 | `scoop search git` | 搜索某个软件 |
| 2.1 | 搜索 Python | `scoop search python` | 常用于找多个可选包 |
| 3 | 安装软件 | `scoop install git` | 安装单个软件 |
| 3.1 | 安装多个软件 | `scoop install git ripgrep fd jq bat` | 一次安装多个工具 |
| 4 | 卸载软件 | `scoop uninstall git` | 卸载软件 |
| 5 | 更新 Scoop 本体 | `scoop update` | 更新 Scoop 自身 |
| 6 | 更新某个软件 | `scoop update git` | 更新指定软件 |
| 6.1 | 更新全部软件 | `scoop update *` | 更新所有已安装软件 |
| 7 | 查看已安装软件 | `scoop list` | 列出本机已安装软件 |
| 8 | 查看软件信息 | `scoop info git` | 查看软件详情 |
| 8.1 | 查看软件安装位置 | `scoop info delta` | 查看安装目录与版本 |
| 9 | 检查问题 | `scoop checkup` | 适合排查环境异常 |
| 10 | 添加 bucket | `scoop bucket add extras` `scoop bucket add nerd-fonts` | 添加额外软件源 |
| 10.1 | 查看 bucket | `scoop bucket list` | 查看已添加的软件源 |
| 11 | 配置 aria2 加速 | `scoop config aria2-max-connection-per-server 16` `scoop config aria2-split 16` `scoop config aria2-min-split-size 1M` | 开启多线程下载 |
| 11.1 | 查看 Scoop 配置 | `scoop config` | 查看当前配置项 |
| 12 | 查看命令实际路径 | `Get-Command git` `Get-Command rg` `Get-Command fd` | 检查是否已被 Scoop 接管 |

#### 11.2 Scoop 安装命令

```powershell
# 设置执行策略
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 安装 Scoop
irm get.scoop.sh | iex

# 自定义安装路径（可选）
$env:SCOOP = "D:\Scoop"
irm get.scoop.sh | iex
```

#### 11.3 常用 Bucket 源

| Bucket | 命令 | 说明 |
| --- | --- | --- |
| main | `scoop bucket add main` | 默认源（无需手动添加） |
| extras | `scoop bucket add extras` | 扩展软件，最常用 |
| versions | `scoop bucket add versions` | 软件历史版本 |
| nerd-fonts | `scoop bucket add nerd-fonts` | 编程字体合集 |
| java | `scoop bucket add java` | JDK 相关 |
| games | `scoop bucket add games` | 游戏工具类 |

#### 11.4 Aria2 多线程下载配置

| 配置项 | 命令 | 说明 |
| --- | --- | --- |
| 安装 aria2 | `scoop install aria2` | 先安装 aria2 |
| 启用 aria2 | `scoop config aria2-enabled true` | 启用 aria2 |
| 每服务器最大连接数 | `scoop config aria2-max-connection-per-server 16` | 每服务器最大连接数 |
| 分片数 | `scoop config aria2-split 16` | 分片数 |
| 最小分片大小 | `scoop config aria2-min-split-size 1M` | 最小分片大小 |

---

### 十二、NSSM 使用完全指南

> NSSM（Non-Sucking Service Manager）— Windows 服务管理神器，可将任意程序注册为 Windows 系统服务。

#### 12.1 安装

```bash
# 使用 Scoop 安装（推荐）
scoop install nssm

# 或手动下载
# https://nssm.cc/download
```

#### 12.2 核心命令一览

##### 安装服务

| 命令 | 说明 | 示例 |
| --- | --- | --- |
| `nssm install <服务名> <程序路径>` | 基础安装 | `nssm install MyService "C:\Python312\python.exe"` |
| `nssm install <服务名> <程序路径> <参数>` | 带参数安装 | `nssm install MyService "C:\Python312\python.exe" "C:\scripts\app.py"` |

##### 服务启停管理

| 命令 | 说明 |
| --- | --- |
| `nssm start <服务名>` | 启动服务 |
| `nssm stop <服务名>` | 停止服务 |
| `nssm restart <服务名>` | 重启服务 |
| `nssm status <服务名>` | 查看服务状态 |

##### 编辑服务配置

| 命令 | 说明 |
| --- | --- |
| `nssm edit <服务名>` | 打开 GUI 图形界面编辑（推荐） |
| `nssm set <服务名> <参数项> <值>` | 命令行方式修改单项配置 |
| `nssm get <服务名> <参数项>` | 查看某项配置 |

##### 卸载服务

| 命令 | 说明 |
| --- | --- |
| `nssm remove <服务名>` | 需确认卸载 |
| `nssm remove <服务名> confirm` | 直接卸载不询问 |

#### 12.3 GUI 界面详解（nssm edit）

| 标签页 | 说明 |
| --- | --- |
| **Application** | 程序路径、启动目录、参数 |
| **Details** | 服务显示名称、描述 |
| **Log on** | 运行账户权限设置 |
| **Dependencies** | 依赖的其他服务 |
| **Process** | 进程优先级、CPU 亲和性 |
| **Shutdown** | 停止服务时的行为 |
| **Exit actions** | 异常退出后的重启策略 |
| **I/O** | 标准输入输出日志路径 |
| **Environment** | 环境变量设置 |

#### 12.4 日志配置

| 命令 | 说明 |
| --- | --- |
| `nssm set <服务名> AppStdout "C:\logs\myservice_out.log"` | 设置标准输出日志 |
| `nssm set <服务名> AppStderr "C:\logs\myservice_err.log"` | 设置错误输出日志 |

#### 12.5 异常重启策略

| 命令 | 说明 |
| --- | --- |
| `nssm set <服务名> AppRestartDelay 3000` | 服务崩溃后自动重启，延迟 3000ms |
| `nssm set <服务名> AppExit Default Restart` | 退出动作：程序退出后自动重启 |

#### 12.6 开机自启设置

| 命令 | 说明 |
| --- | --- |
| `nssm get <服务名> Start` | 查看启动类型 |
| `nssm set <服务名> Start SERVICE_AUTO_START` | 设置为自动启动（开机自启） |
| `nssm set <服务名> Start SERVICE_DEMAND_START` | 设置为手动启动 |
| `nssm set <服务名> Start SERVICE_DISABLED` | 禁用 |

#### 12.7 注意事项

| 注意点 | 说明 |
| --- | --- |
| **管理员权限** | 安装/卸载服务必须用管理员身份运行终端 |
| **路径空格** | 所有含空格的路径必须加双引号 |
| **python 路径** | 建议用 `where python` 确认后填写完整路径 |
| **工作目录** | 脚本有相对路径时需设置 `AppDirectory` |
| **环境变量** | 服务运行环境与用户环境不同，需手动配置 |

#### 12.8 完整使用示例

```bash
# 1. 查找 python 路径
where python

# 2. 注册服务
nssm install wifi_auto "C:\Python312\python.exe" "E:\scripts\scan_wifi.py"

# 3. 配置日志
nssm set wifi_auto AppStdout "E:\logs\wifi_out.log"
nssm set wifi_auto AppStderr "E:\logs\wifi_err.log"

# 4. 配置崩溃自动重启
nssm set wifi_auto AppExit Default Restart
nssm set wifi_auto AppRestartDelay 3000

# 5. 启动服务
nssm start wifi_auto

# 6. 查看状态
nssm status wifi_auto
```

---

### 十三、开发者日常高频组合

| 场景 | 命令 | 说明 |
| --- | --- | --- |
| 新建项目并初始化 | `mkdir demo-api`<br>`cd demo-api`<br>`ni README.md, .gitignore`<br>`git init` | 新建项目的最小起手式 |
| 快速检查工具链 | `whereis git`<br>`whereis node`<br>`whereis npm`<br>`whereis claude`<br>`whereis rg`<br>`whereis fd` | 检查关键命令来源 |
| 查项目关键词 | `rg "TODO"`<br>`rg "axios"`<br>`rg "process.env"` | 搜代码特别高频 |
| 查配置文件位置 | `fd package.json`<br>`fd tsconfig`<br>`fd vite.config` | 快速定位配置文件 |
| 看日志最后几行 | `Get-Content .\app.log -Tail 30` | 查看最新日志 |
| 持续看日志 | `Get-Content .\app.log -Wait` | 持续追踪日志变化 |
| 删除构建目录并重打包 | `rm .\dist -Recurse -Force`<br>`npm run build` | 清缓存重建 |
| 查端口并杀进程 | `netstat -ano | findstr :3000`<br>`Stop-Process -Id 12345 -Force` | 排查端口占用 |
| 打开并重载配置 | `notepad $PROFILE`<br>`. $PROFILE` | 修改终端体验 |
| 检查 Git 来源和配置位置 | `Get-Command git`<br>`git config --global --list --show-origin` | 同时看程序路径和配置路径 |

---

### 十四、PROFILE 增强配置推荐

| 模块 / 配置                    | 作用                |
| -------------------------- | ----------------- |
| `PSReadLine`               | 历史命令预测、方向键匹配历史    |
| `Terminal-Icons`           | 文件和目录图标显示         |
| `z`                        | 快速跳目录             |
| `gsudoModule`              | 提权命令支持            |
| `$env:GIT_PAGER = "delta"` | Git diff 使用 delta |
| `whereis` 函数               | 快速查命令来源           |


#### 完整配置代码

```powershell
Import-Module PSReadLine
Set-PSReadLineOption -PredictionSource History
Set-PSReadLineOption -PredictionViewStyle Inline
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

Import-Module Terminal-Icons
Import-Module z
Import-Module gsudoModule

$env:GIT_PAGER = "delta"

# ========== 别名设置 ==========
Set-Alias -Name whereis -Value Get-Command
Set-Alias -Name cat -Value Get-Content
Set-Alias -Name rm -Value Remove-Item
Set-Alias -Name cp -Value Copy-Item
Set-Alias -Name mv -Value Move-Item
Set-Alias -Name grep -Value Select-String
Set-Alias -Name curl -Value Invoke-RestMethod

# ========== 自定义函数 ==========
function whereis($name) {
    Get-Command $name -ErrorAction SilentlyContinue |
    Select-Object Name, Source, Version | Format-Table -AutoSize
}
```

#### 配置效果一览

| 效果 | 说明 |
| --- | --- |
| 历史命令预测 | 输入命令时自动补全历史 |
| 方向键快速匹配历史 | 上下方向键更顺手 |
| 文件图标显示 | 目录更直观 |
| `z` 快速跳目录 | 常去目录跳转更快 |
| `whereis` 快速查来源 | 适合查 Git / Node / Claude |
| Git diff 默认走 delta | 看 diff 更舒服 |

---

### 十五、建议优先记住的命令清单

#### 基础命令（必须熟练）

| 命令 | 简写 | 作用 |
| --- | --- | --- |
| `Get-Location` | `pwd` | 查看当前目录 |
| `Get-ChildItem` | `ls` | 列出目录文件 |
| `Set-Location` | `cd` | 切换目录 |
| `New-Item` | `ni` | 新建文件/目录 |
| `Get-Content` | `cat` | 查看文件内容 |
| `Copy-Item` | `cp` | 复制文件 |
| `Move-Item` | `mv` | 移动文件 |
| `Remove-Item` | `rm` | 删除文件 |

#### 查询命令（开发必备）

| 命令 | 作用 |
| --- | --- |
| `Get-Command` / `whereis` | 查看命令来源 |
| `Get-Help` | 查看命令帮助 |
| `Select-String` / `grep` | 搜索文本内容 |
| `Get-Process` | 查看进程 |
| `Stop-Process` | 结束进程 |

#### 环境与配置

| 命令           | 作用        |
| ------------ | --------- |
| `$env:`      | 查看/设置环境变量 |
| `$PROFILE`   | 查看配置文件路径  |
| `. $PROFILE` | 重载配置      |

#### 工具链命令

| 命令 | 作用 |
| --- | --- |
| `scoop install` | 安装软件 |
| `scoop update *` | 更新所有软件 |
| `rg` | 全文搜索 |
| `fd` | 按名查找文件 |
| `bat` | 查看文件（高亮） |

---

### 十六、日常开发操作流

| 步骤 | 命令 | 作用 |
| --- | --- | --- |
| 1 | `cd E:\Code` | 进入代码目录 |
| 2 | `fd package.json` | 找项目 |
| 3 | `cd .\my-project` | 进入项目 |
| 4 | `ls` | 看目录结构 |
| 5 | `git status` | 看 Git 状态 |
| 6 | `rg "TODO"` | 搜索待办 |
| 7 | `npm install` | 安装依赖 |
| 8 | `npm run dev` | 启动开发服务 |
| 9 | `Get-Content .\logs\app.log -Tail 20` | 看日志 |

---

### 十七、总结：PowerShell 使用三层架构

| 层级 | 重点命令 | 说明 |
| --- | --- | --- |
| **基础操作** | `pwd`、`ls`、`cd`、`mkdir`、`ni`、`cat`、`cp`、`mv`、`rm` | 日常文件操作 |
| **开发必备** | `Get-Command`、`Select-String`、`Get-Process`、`Stop-Process`、`$env:`、`$PROFILE`、`. $PROFILE` | 系统与脚本操作 |
| **工具链增强** | `scoop`、`rg`、`fd`、`bat`、`fzf`、`delta`、`jq` | 开发体验提升 |

> **记住一句就够了：PowerShell 本体负责系统和脚本，Scoop 负责工具管理，rg / fd / bat / delta 负责把开发体验拉满。**

---

### 十八、Scoop + PowerShell 开发环境一键迁移指南

> 目标：在全新 Windows 电脑上，用 Scoop 统一管理所有开发工具和 AI 工具，全部装在 E 盘。

#### 一、安装 Scoop（安装到 E 盘）

Scoop 默认装在 C 盘用户目录下，通过设置环境变量让它装到 E 盘。

打开 PowerShell，**安装前**先设好路径：

```powershell
# 设置 Scoop 安装目录到 E 盘
[Environment]::SetEnvironmentVariable('SCOOP', 'E:\Scoop', 'User')
$env:SCOOP = 'E:\Scoop'

# 设置全局安装目录（需要管理员装的软件）
[Environment]::SetEnvironmentVariable('SCOOP_GLOBAL', 'E:\Scoop\GlobalApps', 'Machine')
$env:SCOOP_GLOBAL = 'E:\Scoop\GlobalApps'

# 开始安装
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

验证：

```powershell
scoop --version
scoop config
# 确认 root_path 是 E:\Scoop
```

安装完成后目录结构：

```
E:\Scoop\
├── apps\          ← 所有软件都装这里
├── buckets\       ← bucket 仓库
├── cache\         ← 下载缓存
├── persist\       ← 持久化配置
└── shims\         ← 快捷命令（已自动加入 PATH）
```

#### 二、添加 Bucket

```powershell
scoop bucket add main
scoop bucket add extras
scoop bucket add java
scoop bucket add nerd-fonts
```

#### 三、Windows Terminal + 终端美化

##### 3.1 安装

```powershell
scoop install windows-terminal
scoop install oh-my-posh
scoop install nerd-fonts/JetBrainsMono-NF
```

##### 3.2 配置 Oh My Posh

```powershell
notepad $PROFILE
```

文件不存在会提示创建，选"是"，写入：

```powershell
# Oh My Posh 主题
oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\jandedobbeleer.omp.json" | Invoke-Expression

# 中文编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

保存后重启终端即可。

##### 3.3 Windows Terminal 外观设置

Settings → Defaults → Appearance：

- Font face：**JetBrainsMono Nerd Font**
- Font size：**14**
- Color scheme：**One Half Dark** 或 **Dracula**

#### 四、基础工具

```powershell
scoop install git curl wget 7zip sudo
```

Git 配置：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global core.autocrlf input
```

#### 五、开发语言环境

##### 5.1 Node.js

```powershell
scoop install nodejs
```

npm 镜像：

```powershell
npm config set registry https://registry.npmmirror.com
```

##### 5.2 Python（Miniconda）

```powershell
scoop install miniconda3
conda init powershell
```

重启终端后设置镜像：

```powershell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --set show_channel_urls yes
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

##### 5.3 Java（多版本管理）

```powershell
scoop install temurin8-jdk       # Java 8
scoop install temurin17-jdk      # Java 17
scoop install temurin21-jdk      # Java 21
```

切换版本：

```powershell
scoop reset temurin17-jdk        # 切到 Java 17
java -version

scoop reset temurin8-jdk         # 切回 Java 8
java -version
```

Scoop 自动管理 `JAVA_HOME` 和 `PATH`，不用手动改。

##### 5.4 Maven / Gradle

```powershell
scoop install maven gradle
```

Maven 镜像（创建 `%USERPROFILE%\.m2\settings.xml`）：

```xml
<settings>
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <mirrorOf>central</mirrorOf>
      <url>https://maven.aliyun.com/repository/central</url>
    </mirror>
  </mirrors>
</settings>
```

##### 5.5 .NET

```powershell
scoop install dotnet-sdk
dotnet --version
```

#### 六、环境变量（内存统一 8GB）

管理员 PowerShell 执行：

```powershell
[System.Environment]::SetEnvironmentVariable("JAVA_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("_JAVA_OPTIONS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("MAVEN_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("GRADLE_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("NODE_OPTIONS", "--max-old-space-size=8192", "User")
```

#### 七、AI 工具链

##### 7.1 Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
claude --version
```

首次运行 `claude` 会弹浏览器登录。

配置文件：`%USERPROFILE%\.claude\settings.json`

```jsonc
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "85"
  },
  "statusLine": {
    "type": "command",
    "command": "oh-my-posh claude"
  }
}
```

##### 7.2 深度学习环境

```powershell
conda create -n dl python=3.11 -y
conda activate dl

# PyTorch（去 pytorch.org 查你的 CUDA 版本对应命令）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 常用工具
pip install jupyter numpy pandas matplotlib scikit-learn
```

#### 八、WSL2 安装到 E 盘

WSL 默认装在 C 盘，通过 export/import 方式安装到 E 盘。

##### 8.1 方案一：全新安装直接到 E 盘

```powershell
# 1. 启用 WSL（管理员 PowerShell），不装默认发行版
wsl --install --no-distribution

# 2. 重启电脑

# 3. 先装到 C 盘（临时）
wsl --install -d Ubuntu-22.04

# 4. 装完设好用户名密码后，关闭 WSL
wsl --shutdown

# 5. 导出
wsl --export Ubuntu-22.04 E:\ubuntu-22.04.tar

# 6. 注销 C 盘的
wsl --unregister Ubuntu-22.04

# 7. 导入到 E 盘
mkdir E:\WSL\Ubuntu-22.04
wsl --import Ubuntu-22.04 E:\WSL\Ubuntu-22.04 E:\ubuntu-22.04.tar --version 2

# 8. 删除临时文件
del E:\ubuntu-22.04.tar

# 9. 验证
wsl -l -v
```

##### 8.2 方案二：已装在 C 盘，迁移到 E 盘

```powershell
wsl --shutdown
wsl --export Ubuntu-22.04 E:\ubuntu-22.04-backup.tar
wsl --unregister Ubuntu-22.04
mkdir E:\WSL\Ubuntu-22.04
wsl --import Ubuntu-22.04 E:\WSL\Ubuntu-22.04 E:\ubuntu-22.04-backup.tar --version 2
del E:\ubuntu-22.04-backup.tar
```

##### 8.3 设置默认用户

导入后默认用户变成 root，需要改回来。进入 WSL：

```powershell
wsl -d Ubuntu-22.04 -u root
```

在 WSL 中执行：

```bash
# 设置默认登录用户（换成你的用户名）
cat > /etc/wsl.conf << 'EOF'
[user]
default=fifine
EOF

exit
```

回到 PowerShell 重启 WSL：

```powershell
wsl --shutdown
wsl -d Ubuntu-22.04
whoami   # 应该显示 fifine
```

##### 8.4 设为默认发行版

```powershell
wsl --set-default Ubuntu-22.04
```

之后直接输入 `wsl` 就进入 E 盘的 Ubuntu 了。

#### 九、编辑器（可选）

```powershell
scoop install vscode
# 或
scoop install zed
```

#### 十、一键安装脚本

保存为 `setup.ps1`，新电脑上管理员 PowerShell 执行：

```powershell
# ===== Scoop 开发环境一键安装（E盘）=====

# Scoop 安装到 E 盘
[Environment]::SetEnvironmentVariable('SCOOP', 'E:\Scoop', 'User')
$env:SCOOP = 'E:\Scoop'
[Environment]::SetEnvironmentVariable('SCOOP_GLOBAL', 'E:\Scoop\GlobalApps', 'Machine')
$env:SCOOP_GLOBAL = 'E:\Scoop\GlobalApps'

if (!(Get-Command scoop -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
}

# Bucket
scoop bucket add main
scoop bucket add extras
scoop bucket add java
scoop bucket add nerd-fonts

# 基础工具
scoop install git curl wget 7zip sudo

# 终端美化
scoop install windows-terminal oh-my-posh
scoop install nerd-fonts/JetBrainsMono-NF

# 开发语言
scoop install nodejs miniconda3
scoop install temurin17-jdk maven gradle
scoop install dotnet-sdk

# 编辑器
scoop install vscode

# npm 镜像 + Claude Code
npm config set registry https://registry.npmmirror.com
npm install -g @anthropic-ai/claude-code

# conda 初始化 + 镜像
conda init powershell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --set show_channel_urls yes
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 环境变量
[System.Environment]::SetEnvironmentVariable("JAVA_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("_JAVA_OPTIONS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("MAVEN_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("GRADLE_OPTS", "-Xmx8g", "User")
[System.Environment]::SetEnvironmentVariable("NODE_OPTIONS", "--max-old-space-size=8192", "User")

Write-Host ""
Write-Host "===== 安装完成！重启终端后生效 =====" -ForegroundColor Green
Write-Host "  后续步骤：" -ForegroundColor Yellow
Write-Host "  1. 重启终端"
Write-Host "  2. notepad `$PROFILE → 配置 Oh My Posh"
Write-Host "  3. claude → 登录 Anthropic"
Write-Host "  4. git config --global user.name / user.email"
Write-Host "  5. WSL：参见文档第八节安装到 E 盘"
```

#### 十一、日常命令速查

```powershell
scoop search 关键词            # 搜索软件
scoop install 软件名           # 安装
scoop uninstall 软件名         # 卸载
scoop update                   # 更新 Scoop 自身
scoop update *                 # 更新所有软件
scoop reset temurin17-jdk      # 切换 Java 版本
scoop list                     # 查看已安装
scoop cleanup *                # 清理旧版本
scoop cache rm *               # 清理下载缓存
scoop export > scoopfile.json  # 导出软件清单（迁移用）
scoop import scoopfile.json    # 从清单恢复（新电脑）
```

#### 十二、目录结构总览

```
E:\
├── Scoop\                     ← Scoop 及所有软件
│   ├── apps\                  ← nodejs, python, java, maven...
│   ├── buckets\
│   ├── cache\
│   ├── persist\               ← 软件持久化配置
│   └── shims\                 ← 命令快捷方式
│
└── WSL\
    └── Ubuntu-22.04\          ← WSL2 虚拟磁盘
        └── ext4.vhdx
```

---

### 附录：常见问题排查

| 问题 | 解决方案 |
| --- | --- |
| 执行策略被禁用 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| 找不到命令 | `whereis <命令名>` 检查是否安装 |
| 端口被占用 | `netstat -ano | findstr :端口号` 查找进程 |
| 环境变量不生效 | 重启终端或执行 `. $PROFILE` |
| Scoop 安装失败 | 检查是否有中文路径，尝试自定义安装路径 |
