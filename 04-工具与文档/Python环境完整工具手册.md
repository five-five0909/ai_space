# Python 环境完整工具手册

> 覆盖范围：Scoop（Windows包管理）→ Conda（环境与包管理）→ 将Conda设为系统默认Python → PyCharm（IDE与环境连接）
>
> 适用平台：Windows 10/11、Ubuntu 20.04/22.04

---

## 目录

1. [Scoop —— Windows 命令行包管理器](#一scoop--windows-命令行包管理器)
2. [Conda —— Python 环境与包管理](#二conda--python-环境与包管理)
3. [将 Conda 环境设为 Windows 默认 Python](#三将-conda-环境设为-windows-默认-python)
4. [PyCharm —— IDE 与 Conda 环境连接](#四pycharm--ide-与-conda-环境连接)

---

## 一、Scoop —— Windows 命令行包管理器

### 1.1 Scoop 是什么

Scoop 是 Windows 上的命令行软件包管理器，类似 Linux 的 `apt` 或 macOS 的 `brew`。

```
# 手动安装 Chrome
打开浏览器 → 搜索 → 进官网 → 点下载 → 双击安装包 → 下一步...

# Scoop 安装 Chrome
scoop install googlechrome
```

**核心优势**

- 安装到用户目录，**不需要管理员权限**
- 卸载干净，不污染注册表
- 自动管理环境变量
- 支持多版本并存与一键切换

**与其他包管理器对比**

| 特性 | Scoop | winget | Chocolatey | 手动安装 |
|------|-------|--------|------------|---------|
| 需要管理员 | 不需要 | 需要 | 需要 | 需要 |
| 便携式 | ✓ | ✗ | ✗ | 看情况 |
| 环境变量 | 自动 | 自动 | 自动 | 手动 |
| 版本切换 | ✓ | ✗ | ✗ | ✗ |
| 卸载干净 | ✓ | 有时残留 | 有时残留 | 经常残留 |
| 命令风格 | Linux-like | 类似 apt | 类似 apt | 无 |

> 三者可以共存，建议分工：Scoop 装开发工具，winget 装桌面应用，Chocolatey 装系统级工具。

---

### 1.2 安装 Scoop

**前置条件**

- Windows 10 / 11
- PowerShell 5.1+（系统自带）或 PowerShell 7+

```powershell
# 查看 PowerShell 版本
$PSVersionTable.PSVersion

# 查看当前执行策略
Get-ExecutionPolicy
```

**步骤一：设置脚本执行权限**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**步骤二：安装 Scoop**

```powershell
# 方法一：默认安装（装到 C:\Users\你的用户名\scoop）
irm get.scoop.sh | iex

# 方法二：指定路径安装（推荐，避免路径过深）
$env:SCOOP = 'D:\scoop'
[Environment]::SetEnvironmentVariable('SCOOP', $env:SCOOP, 'User')
irm get.scoop.sh | iex
```

**步骤三：验证安装**

```powershell
scoop --version
# 0.5.x 或更高即可
```

安装后目录结构：

```
D:\scoop\
├── apps\       # 所有已安装软件
├── buckets\    # 软件仓库（类似 apt 的 sources.list）
├── cache\      # 下载缓存
└── shims\      # 可执行文件的代理（自动加入 PATH）
```

**步骤四：添加常用 Bucket（软件仓库）**

```powershell
scoop bucket add extras    # 大量常用软件
scoop bucket add versions  # 软件历史版本
scoop bucket add nerd-fonts # 编程字体
scoop bucket add java      # JDK 各版本

# 查看所有可用的 bucket
scoop bucket known

# 查看已添加的 bucket
scoop bucket list
```

---

### 1.3 日常使用命令

#### 安装与卸载

```powershell
scoop install git                    # 安装
scoop install git curl wget 7zip     # 安装多个
scoop install versions/python312     # 安装特定版本
scoop install --force git            # 强制重装
scoop uninstall firefox              # 卸载
scoop uninstall firefox vlc discord  # 卸载多个
```

#### 搜索与查询

```powershell
scoop search firefox     # 搜索软件
scoop info firefox       # 查看软件详情
scoop list               # 列出已安装软件
scoop status             # 查看哪些软件可以更新
scoop prefix git         # 查看安装路径
```

#### 更新

```powershell
scoop update             # 更新 scoop 自身
scoop update git         # 更新单个软件
scoop update *           # 更新所有软件（最常用）
scoop cleanup *          # 清理旧版本
```

#### 版本切换

```powershell
# 安装多个版本
scoop install versions/python310
scoop install versions/python311
scoop install python

# 切换版本
scoop reset python310
scoop reset python    # 切回最新版

# 验证
python --version
```

---

### 1.4 常用软件安装速查

#### 开发工具

```powershell
scoop install git curl wget 7zip sudo aria2
scoop install vscode
scoop install versions/python312
scoop install nodejs
scoop install go
scoop install rustup
scoop install uv           # 超快的 Python 包管理器
```

#### 终端美化工具

```powershell
scoop install windows-terminal
scoop install nerd-fonts/FiraCode-NF    # 编程字体
scoop install starship                   # 终端提示符美化
scoop install eza                        # 现代 ls 替代
scoop install bat                        # 现代 cat 替代
scoop install fd                         # 现代 find 替代
scoop install ripgrep                    # 现代 grep 替代
scoop install fzf                        # 模糊搜索
scoop install jq                         # JSON 处理
scoop install zoxide                     # 智能 cd
```

#### 日常软件

```powershell
scoop install extras/googlechrome
scoop install extras/firefox
scoop install extras/vlc
scoop install extras/obsidian
scoop install extras/notepadplusplus
scoop install extras/obs-studio
```

#### Java 开发

```powershell
scoop bucket add java

scoop install java/temurin21-jdk    # Eclipse Temurin JDK 21（LTS，推荐）
scoop install java/temurin17-jdk    # JDK 17（LTS）
scoop install maven
scoop install gradle
scoop install extras/intellij-idea-community
```

> **校验说明**：原文档列出了 `corretto-17-jdk`，Amazon Corretto 确实在 java bucket 中，名称为 `corretto17-jdk`（无横线），实际安装前建议先用 `scoop search corretto` 确认当前可用名称。

---

### 1.5 高级配置

#### 配置代理

```powershell
# 通过 scoop 配置
scoop config proxy 127.0.0.1:7890

# 取消代理
scoop config proxy none
```

#### 使用 aria2 加速下载

```powershell
scoop install aria2

# scoop 检测到 aria2 后会自动使用多线程下载
scoop config aria2-max-connection-per-server 16
scoop config aria2-split 16
scoop config aria2-min-split-size 4M

# 临时禁用 aria2（某些情况下 aria2 会导致下载失败）
scoop install --no-use-download-cache some-app
```

> **校验说明**：原文档写的是 `--disable aria2`，该参数在 Scoop 0.4+ 版本中已不存在，正确的做法是 `scoop config aria2-enabled false` 来全局禁用，或删除 aria2 来临时停用。

#### 导出与恢复软件列表

```powershell
# 导出（备份）
scoop export > scoopfile.json

# 在新机器上恢复（先装好 scoop，再执行）
scoop import scoopfile.json
```

#### 版本锁定

```powershell
scoop hold git       # 锁定版本，update * 时不会更新
scoop unhold git     # 解除锁定
```

---

### 1.6 维护与排错

#### 日常维护

```powershell
scoop checkup           # 健康检查，给出修复建议
scoop cleanup *         # 清理所有旧版本
scoop cache rm *        # 清理下载缓存
scoop cache show        # 查看缓存大小
scoop reset APP         # 重置软件（修复 shim 和环境变量）
```

#### 常见问题

**Q：安装时报 hash 校验失败**

```powershell
# 软件已更新但 bucket 元数据还没同步，临时跳过
scoop install --skip-hash-check APP
# 隔天 scoop update 后再正常安装
```

**Q：软件安装后命令找不到**

```powershell
scoop reset APP    # 重建 shim

# 检查 shim 目录是否在 PATH 中
$env:PATH -split ';' | Select-String 'scoop\\shims'

# 如果没有，手动添加
[Environment]::SetEnvironmentVariable(
    'PATH',
    "D:\scoop\shims;$([Environment]::GetEnvironmentVariable('PATH', 'User'))",
    'User'
)
# 重启终端
```

**Q：下载太慢**

```powershell
# 方案一：配置代理
scoop config proxy 127.0.0.1:7890

# 方案二：安装 aria2
scoop install aria2
scoop config aria2-max-connection-per-server 16
```

---

### 1.7 一键装机脚本

保存为 `setup_windows.ps1`，新机器执行一次：

```powershell
# setup_windows.ps1

Write-Host "===== 1. 安装 Scoop =====" -ForegroundColor Cyan
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
$env:SCOOP = 'D:\scoop'
[Environment]::SetEnvironmentVariable('SCOOP', $env:SCOOP, 'User')
irm get.scoop.sh | iex

Write-Host "===== 2. 添加 Bucket =====" -ForegroundColor Cyan
scoop bucket add extras
scoop bucket add versions
scoop bucket add nerd-fonts
scoop bucket add java

Write-Host "===== 3. 配置 aria2 加速 =====" -ForegroundColor Cyan
scoop install aria2
scoop config aria2-max-connection-per-server 16
scoop config aria2-split 16

Write-Host "===== 4. 基础工具 =====" -ForegroundColor Cyan
scoop install git curl wget 7zip sudo

Write-Host "===== 5. 开发工具 =====" -ForegroundColor Cyan
scoop install vscode
scoop install versions/python312
scoop install nodejs

Write-Host "===== 6. 终端工具 =====" -ForegroundColor Cyan
scoop install windows-terminal
scoop install nerd-fonts/FiraCode-NF
scoop install starship eza bat fd ripgrep fzf jq zoxide

Write-Host "===== 7. 日常软件 =====" -ForegroundColor Cyan
scoop install extras/googlechrome extras/firefox
scoop install extras/notepadplusplus extras/obsidian extras/vlc

Write-Host "===== 8. 清理 =====" -ForegroundColor Cyan
scoop cleanup *

Write-Host "===== 完成！=====" -ForegroundColor Green
scoop list
```

---

## 二、Conda —— Python 环境与包管理

### 2.1 发行版选择

```
Miniforge   推荐。轻量，默认使用 conda-forge 频道，社区维护包最全。
Miniconda   官方出品，默认使用 defaults 频道，包偏少但稳定。
Anaconda    预装 250+ 包，体积约 5GB，过于臃肿，不推荐。
```

> **校验说明**：三者核心的 `conda` 命令完全相同，区别仅在于默认频道和预装包数量。Miniforge 同时预装了 `mamba`（更快的求解器），在网络条件相同时安装速度优于 Miniconda。

---

### 2.2 安装

#### Windows

```powershell
# 下载 Miniforge3-Windows-x86_64.exe
# https://github.com/conda-forge/miniforge/releases/latest

# 双击安装，建议：
# - 安装路径不含空格和中文，如 D:\miniforge3
# - 不勾选 "Add to PATH"（让 conda init 来管理）

# 安装后在开始菜单找到 Miniforge Prompt，执行：
conda init powershell
conda init cmd.exe
```

#### Ubuntu

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
# 按提示操作，最后询问是否 conda init → 选 yes

source ~/.bashrc
```

#### 安装后必做配置

```bash
# 关闭每次打开终端自动进入 base 环境（推荐）
conda config --set auto_activate_base false

# 使用更快的依赖求解器（conda 23.10+ 已默认启用 libmamba）
conda config --set solver libmamba
```

---

### 2.3 配置镜像源（国内加速）

```bash
# 清华源（推荐）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes

# 查看当前配置
conda config --show channels

# 恢复默认源
conda config --remove-key channels
```

`~/.condarc` 完整参考：

```yaml
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
  - defaults
show_channel_urls: true
auto_activate_base: false
channel_priority: strict
solver: libmamba
```

---

### 2.4 环境管理

#### 创建环境

```bash
# 基本创建（指定 Python 版本）
conda create -n myenv python=3.12

# 创建时一并安装包
conda create -n datascience python=3.12 numpy pandas scikit-learn matplotlib

# 从指定频道创建
conda create -n pytorch_env python=3.12 pytorch torchvision -c pytorch

# 在指定路径创建（不放到默认 envs 目录）
conda create --prefix ./myenv python=3.12

# 从 yml 文件创建
conda env create -f environment.yml

# 克隆已有环境
conda create --name new_env --clone existing_env
```

#### 激活与退出

```bash
conda activate myenv
conda deactivate
```

#### 查看环境

```bash
conda env list
# 或
conda info --envs

# 查看当前激活的环境名
echo $CONDA_DEFAULT_ENV

# 查看当前环境路径
echo $CONDA_PREFIX
```

#### 删除环境

```bash
conda env remove -n myenv
# 或
conda remove -n myenv --all
```

#### 导出与导入

```bash
# 推荐：只导出手动安装的包，跨平台兼容性好
conda env export --from-history > environment.yml

# 完整导出（含子依赖和构建号，精确但跨平台可能失败）
conda env export > environment-full.yml

# 从 yml 创建
conda env create -f environment.yml

# 更新已有环境（--prune 删除 yml 中没有的包）
conda env update -f environment.yml --prune
```

`environment.yml` 格式参考：

```yaml
name: datascience
channels:
  - conda-forge
  - pytorch
  - defaults
dependencies:
  - python=3.12
  - numpy>=1.26
  - pandas>=2.0
  - scikit-learn
  - pip:
      - transformers==4.40.0
      - datasets
      - wandb
```

---

### 2.5 包管理

#### 安装包

```bash
# 基本安装
conda install numpy

# 安装多个
conda install numpy pandas matplotlib seaborn

# 安装指定版本
conda install numpy=1.26.4

# 安装版本范围
conda install "numpy>=1.25,<2.0"

# 从指定频道安装
conda install -c conda-forge jupyterlab
conda install -c pytorch pytorch torchvision

# 安装到指定环境（无需激活）
conda install -n myenv numpy pandas

# 安装 pip 包（在 conda 环境中）
pip install transformers datasets
```

> **⚠️ conda 与 pip 的正确协作顺序**
>
> 先用 `conda install` 装能装的，再用 `pip install` 补充 conda 仓库里没有的。顺序反过来（先 pip 后 conda）可能导致依赖冲突，因为 conda 会重新覆盖 pip 安装的包。

#### 卸载包

```bash
conda remove numpy
conda remove numpy pandas matplotlib
conda remove -n myenv numpy  # 从指定环境卸载
```

#### 更新包

```bash
conda update numpy          # 更新单个包
conda update --all          # 更新当前环境所有包
conda update conda          # 更新 conda 自身
conda update --all --dry-run  # 预览更新（不实际执行）
```

#### 查询包

```bash
conda list                        # 当前环境已安装的包
conda list -n myenv               # 查看指定环境
conda list --show-channel-urls    # 显示包来源频道
conda search numpy                # 搜索包
conda search "numpy>=1.25"        # 按版本范围搜索
conda search -c conda-forge tensorflow  # 在指定频道搜索
```

---

### 2.6 频道管理

```bash
conda config --add channels conda-forge      # 添加频道
conda config --remove channels conda-forge   # 移除频道
conda config --set channel_priority strict   # 严格优先级（推荐）
conda config --show channels                 # 查看所有频道
```

常用频道说明：

| 频道 | 说明 |
|------|------|
| defaults | Anaconda 官方频道 |
| conda-forge | 社区维护，包最全，推荐优先使用 |
| pytorch | PyTorch 官方，含 CUDA 版本 |
| nvidia | CUDA toolkit 相关 |
| bioconda | 生物信息学专用 |

---

### 2.7 清理与维护

```bash
# 预览清理内容（不实际删除）
conda clean --dry-run --all

# 清理所有缓存
conda clean --all

# 分项清理
conda clean --tarballs       # 清理 .tar.bz2 缓存
conda clean --packages       # 清理未使用的包缓存
conda clean --index-cache    # 清理频道索引缓存

# 查看操作历史
conda list --revisions

# 回滚到指定版本（N 从 conda list --revisions 中获取）
conda install --rev N
```

---

### 2.8 平台差异与常见坑

#### Windows 专属问题

```
坑1：路径超过 260 字符
  症状：安装包时报 "Path too long"
  解决：
    方法一：注册表开启长路径支持
      reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
    方法二：安装到短路径
      conda create --prefix C:\ce\myenv python=3.12

坑2：中文用户名
  症状：各种奇怪编码错误
  解决：安装 conda 时指定纯英文路径，如 D:\miniforge3

坑3：杀毒软件拦截
  症状：conda install 极慢或失败
  解决：将 conda 安装目录加入 Windows Defender 排除项

坑4：需要 C++ 编译的包安装失败
  症状：pip install 某包时报 "Microsoft Visual C++ 14.0 or greater is required"
  解决：用 conda install 代替，conda 提供预编译的二进制包
    conda install -c conda-forge 包名

坑5：多进程 DataLoader 报错（PyTorch）
  解决：设置 num_workers=0
    DataLoader(dataset, num_workers=0)
```

#### Ubuntu 专属问题

```
坑1：系统 Python 被污染
  症状：sudo pip install 破坏 apt 管理的 Python 包
  解决：永远不要 sudo pip install；
        需要系统级包用 sudo apt install python3-xxx

坑2：import cv2 报错 "libGL.so.1: cannot open shared object file"
  解决：
    sudo apt install libgl1-mesa-glx
    # 或用 conda 安装的 opencv（自带该库）
    conda install -c conda-forge opencv

坑3：GPU 驱动未装但 conda 安装了 PyTorch
  症状：torch.cuda.is_available() 返回 False
  解决：先安装 NVIDIA 驱动
    nvidia-smi   # 检查驱动，看到 CUDA Version 说明驱动正常
    sudo apt install nvidia-driver-535   # 按实际 GPU 选版本
    sudo reboot
```

---

### 2.9 实战场景

#### 场景一：数据科学项目

```bash
conda create -n datascience python=3.12
conda activate datascience

conda install -c conda-forge \
    numpy pandas matplotlib seaborn \
    scikit-learn xgboost lightgbm \
    jupyterlab notebook ipywidgets \
    openpyxl sqlalchemy psycopg2

jupyter lab

# 导出给队友
conda env export --from-history > environment.yml
```

#### 场景二：深度学习（PyTorch + CUDA）

```bash
# 先确认显卡驱动（Ubuntu/Windows 均适用）
nvidia-smi
# 看到 "CUDA Version: 12.x" 说明驱动已就绪

conda create -n dl python=3.12
conda activate dl

# 从 PyTorch 官网获取对应版本命令
# https://pytorch.org/get-started/locally/
# 示例（CUDA 12.1）：
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 验证
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
"

pip install transformers datasets accelerate wandb lightning
conda install -c conda-forge pandas scikit-learn
```

> **校验说明**：原文档建议用 `conda install pytorch -c pytorch -c nvidia`，这在 conda 环境中可行，但 PyTorch 官方文档 2024 年起更推荐用 pip 方式安装，因为 pip 版本更新更及时且 CUDA 版本选择更灵活。两种方式都正确，pip 方式更推荐。

#### 场景三：Web 后端开发

```bash
conda create -n webapp python=3.12
conda activate webapp

# 需要 C 库的包用 conda 装（省去系统依赖配置）
conda install -c conda-forge psycopg2-binary pillow

# 框架用 pip 装
pip install fastapi uvicorn sqlalchemy alembic redis pydantic

# 开发工具
pip install pytest black ruff mypy
```

#### 场景四：复现论文环境

```bash
# 有 environment.yml
conda env create -f environment.yml
conda activate paper_env

# 只有 requirements.txt
conda create -n paper python=3.10
conda activate paper
pip install -r requirements.txt
```

#### 场景五：GIS / 地理信息处理

```bash
# 这是 conda 的杀手级场景：GDAL 手动编译极其繁琐，conda 一条命令搞定
conda create -n gis python=3.12
conda activate gis

conda install -c conda-forge \
    gdal geos proj \
    pyproj shapely fiona geopandas \
    rasterio folium

python -c "from osgeo import gdal; print(gdal.__version__)"
```

#### 场景六：共享服务器（无 sudo 权限）

```bash
# 在用户目录下安装 miniforge
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
~/miniforge3/bin/conda init bash
source ~/.bashrc

# 如果 home 空间不足，自定义路径
conda config --add envs_dirs /data/$USER/conda-envs
conda config --add pkgs_dirs /data/$USER/conda-pkgs
```

---

### 2.10 conda / mamba / micromamba 对比

```bash
# mamba 是 conda 的完全兼容替代，命令相同，依赖求解更快
# conda 23.10+ 已内置 libmamba solver，两者差距已大幅缩小

# 如需安装 mamba
conda install -n base mamba

# 用法与 conda 完全相同
mamba create -n myenv python=3.12
mamba install numpy pandas

# micromamba：完全独立，不需要 base 环境，适合 CI/Docker
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
micromamba create -n myenv python=3.12
micromamba activate myenv
```

| 工具 | 大小 | 速度 | 需要 base | 适合场景 |
|------|------|------|-----------|---------|
| conda | ~400MB | 中→快 | 是 | 日常开发 |
| mamba | ~400MB | 快 | 是 | conda 加速替代 |
| micromamba | ~10MB | 极快 | 否 | CI/Docker/轻量场景 |

---

### 2.11 命令速查表

```
# 环境管理
conda create -n NAME python=3.12       创建环境
conda create -n NAME --clone OLD       克隆环境
conda activate NAME                    激活环境
conda deactivate                       退出环境
conda env list                         列出所有环境
conda env remove -n NAME               删除环境
conda env export --from-history > e.yml  导出环境（跨平台）
conda env export > environment.yml     完整导出
conda env create -f env.yml            从文件创建
conda env update -f env.yml --prune    更新环境

# 包管理
conda install PKG                      安装包
conda install PKG=1.2.3               安装指定版本
conda install PKG -c CHANNEL          从指定频道安装
conda install -n ENV PKG              安装到指定环境
conda remove PKG                       卸载包
conda update PKG                       更新单个包
conda update --all                     更新所有包
conda update conda                     更新 conda 自身
conda list                             列出已安装包
conda search PKG                       搜索包

# 配置管理
conda config --add channels URL        添加频道
conda config --set channel_priority strict  严格频道优先级
conda config --set auto_activate_base false 关闭 base 自动激活
conda config --set solver libmamba    使用更快的求解器
conda config --show                    查看所有配置

# 清理维护
conda clean --all                      清理所有缓存
conda list --revisions                 查看操作历史
conda install --rev N                  回滚到第 N 次操作
```

---

## 三、将 Conda 环境设为 Windows 默认 Python

### 3.1 核心思路

```
Windows 上输入 python 时，系统按 PATH 顺序查找可执行文件。

常见问题原因：
  PATH 顺序：Windows Store 别名 → 系统 Python → conda
  导致 python 指向的不是 conda 环境

目标：
  PATH 顺序：conda 环境路径排最前
  + 关闭 Windows Store Python 别名
```

---

### 3.2 方法一：最简单（推荐普通用户）

PowerShell 启动时自动激活指定 conda 环境，不改动系统配置。

```powershell
# 步骤一：确认 conda init 已执行
conda init powershell
conda init cmd.exe
conda config --set auto_activate_base false

# 步骤二：创建你的默认环境（已有则跳过）
conda create -n default python=3.12 -y

# 步骤三：配置 PowerShell 自动激活
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value "`nconda activate default"

# 步骤四：配置 CMD 自动激活
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "conda activate default" /f

# 重启终端后验证
python -c "import sys; print(sys.executable)"
# 应输出：D:\miniforge3\envs\default\python.exe
```

---

### 3.3 方法二：彻底修改 PATH（推荐开发者）

让所有程序（IDE、脚本、第三方工具）都能找到 conda Python。

**步骤一：关闭 Windows Store Python 别名**

```
设置 → 应用 → 高级应用设置 → 应用执行别名
→ 关闭：
   ☐ python.exe → App Installer
   ☐ python3.exe → App Installer
```

或通过 PowerShell：

```powershell
$aliasPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Execution Aliases"
Remove-ItemProperty -Path $aliasPath -Name "python.exe" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $aliasPath -Name "python3.exe" -ErrorAction SilentlyContinue
```

**步骤二：将 conda 环境路径加到 PATH 最前面**

```powershell
# 修改为你自己的 conda 安装路径和环境名
$CondaRoot = "D:\miniforge3"
$EnvName = "default"
$envPath = "$CondaRoot\envs\$EnvName"

$condaPaths = @(
    $envPath,
    "$envPath\Scripts",
    "$CondaRoot\condabin",
    $CondaRoot
)

$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')

# 移除已有的 conda 路径，避免重复
$cleanPath = ($userPath -split ';' | Where-Object {
    $_ -and $_ -notmatch [regex]::Escape($CondaRoot)
}) -join ';'

# conda 路径加在最前
$newPath = ($condaPaths -join ';') + ';' + $cleanPath
$newPath = $newPath -replace ';;', ';'

[Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
Write-Host "PATH 已更新，请重新打开终端验证。" -ForegroundColor Green
```

**步骤三：验证**

```powershell
# 重新打开终端后执行
where python
# 第一行应为：D:\miniforge3\envs\default\python.exe

python --version
python -c "import sys; print(sys.executable)"
pip --version
```

---

### 3.4 一键配置脚本

保存为 `setup_default_conda.ps1`：

```powershell
param(
    [string]$EnvName = "default",
    [string]$CondaRoot = "D:\miniforge3"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  将 Conda 环境 '$EnvName' 设为默认" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 1. 检查 conda 是否存在
$condaExe = "$CondaRoot\Scripts\conda.exe"
if (!(Test-Path $condaExe)) {
    Write-Host "错误：找不到 conda: $condaExe" -ForegroundColor Red
    exit 1
}

# 2. 创建环境（不存在则创建）
$envPath = "$CondaRoot\envs\$EnvName"
if (!(Test-Path $envPath)) {
    Write-Host "环境不存在，正在创建..." -ForegroundColor Yellow
    & $condaExe create -n $EnvName python=3.12 -y
}

$pythonExe = "$envPath\python.exe"
$pipExe = "$envPath\Scripts\pip.exe"

# 3. 关闭 Windows Store Python 别名
Write-Host "`n[1/4] 关闭 Windows Store Python 别名..." -ForegroundColor Green
$aliasPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Execution Aliases"
if (Test-Path $aliasPath) {
    Remove-ItemProperty -Path $aliasPath -Name "python.exe" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $aliasPath -Name "python3.exe" -ErrorAction SilentlyContinue
}

# 4. 修改 PATH
Write-Host "[2/4] 修改 PATH..." -ForegroundColor Green
$condaPaths = @($envPath, "$envPath\Scripts", "$CondaRoot\condabin", $CondaRoot)
$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
$cleanPath = ($userPath -split ';' | Where-Object {
    $_ -and $_ -notmatch [regex]::Escape($CondaRoot)
}) -join ';'
$newPath = ($condaPaths -join ';') + ';' + $cleanPath
[Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')

# 5. 配置自动激活
Write-Host "[3/4] 配置自动激活..." -ForegroundColor Green
& $condaExe config --set auto_activate_base false
& $condaExe init powershell | Out-Null
& $condaExe init cmd.exe | Out-Null

$profileDir = Split-Path $PROFILE -Parent
if (!(Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force | Out-Null }
$activateLine = "conda activate $EnvName"
if (!(Test-Path $PROFILE) -or ((Get-Content $PROFILE -Raw) -notmatch [regex]::Escape($activateLine))) {
    Add-Content -Path $PROFILE -Value "`n$activateLine"
}
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d $activateLine /f | Out-Null

# 6. 验证
Write-Host "[4/4] 验证..." -ForegroundColor Green
$ver = & $pythonExe --version 2>&1
Write-Host "  Python: $ver" -ForegroundColor White
Write-Host "  路径:   $pythonExe" -ForegroundColor White

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "  完成！请关闭所有终端后重新打开验证" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
```

```powershell
# 使用方法
.\setup_default_conda.ps1                              # 默认：环境名 default，路径 D:\miniforge3
.\setup_default_conda.ps1 -EnvName myenv              # 指定环境名
.\setup_default_conda.ps1 -EnvName myenv -CondaRoot "C:\Users\你\miniforge3"  # 完整指定
```

---

### 3.5 还原默认设置

```powershell
# restore_python.ps1

Write-Host "还原 Python 默认设置..." -ForegroundColor Yellow

# 移除 PATH 中的 conda 路径
$CondaRoot = "D:\miniforge3"   # 修改为你的路径
$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
$newPath = ($userPath -split ';' | Where-Object {
    $_ -and $_ -notmatch [regex]::Escape($CondaRoot)
}) -join ';'
[Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')

# 移除 CMD AutoRun
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f 2>$null

# 移除 PowerShell 自动激活
if (Test-Path $PROFILE) {
    $content = Get-Content $PROFILE -Raw
    $content = $content -replace '(?m)^conda activate .*\r?\n?', ''
    Set-Content $PROFILE $content
}

Write-Host "已还原，请重启终端后验证。" -ForegroundColor Green
```

---

## 四、PyCharm —— IDE 与 Conda 环境连接

### 4.1 版本选择与安装

| 版本 | 价格 | 功能 |
|------|------|------|
| Community | 免费 | 纯 Python 开发 |
| Professional | 付费 | + Web开发 + 远程连接 + 数据库管理 |

> **校验说明**：学生和教师可申请 JetBrains 教育许可，Professional 版完全免费。申请地址：https://www.jetbrains.com/community/education/

```powershell
# Windows：通过 Scoop 安装
scoop install extras/pycharm-community

# 推荐通过 JetBrains Toolbox 安装（方便统一管理和更新）
scoop install extras/jetbrains-toolbox
```

Ubuntu 直接从 https://www.jetbrains.com/pycharm/download/ 下载 `.tar.gz` 包解压运行。

---

### 4.2 首次启动配置

进入 `File → Settings`（快捷键 `Ctrl+Alt+S`）做以下设置：

```
字体：Editor → Font
  推荐字体：JetBrains Mono（自带）
  字号：16（按屏幕调整）
  行高：1.4

显示行号：Editor → General → Appearance
  ☑ Show line numbers
  ☑ Show method separators

文件编码（防中文乱码）：Editor → File Encodings
  Global Encoding: UTF-8
  Project Encoding: UTF-8
  Default encoding for properties files: UTF-8

自动导入：Editor → General → Auto Import
  ☑ Optimize imports on the fly
  ☑ Add unambiguous imports on the fly
```

---

### 4.3 连接 Python 解释器（核心）

**这是使用 PyCharm 最重要的步骤。** PyCharm 本身不包含 Python，需要指定使用哪个 Python 环境。

#### 连接已有 Conda 环境

```
File → Settings → Project: xxx → Python Interpreter
→ 点右上角 ⚙ 齿轮 → Add Interpreter → Conda Environment
  → ○ Use existing environment
  → Conda executable（手动填写路径）：
      Windows: D:\miniforge3\Scripts\conda.exe
      Ubuntu:  ~/miniforge3/bin/conda
  → Interpreter 下拉框：选择目标环境
  → OK → Apply
```

完成后，右下角会显示：`Python 3.12 (myenv) (Conda)`

#### 连接 venv / uv 环境

```
File → Settings → Project → Python Interpreter
→ ⚙ → Add Interpreter → Virtualenv Environment
  → ○ Existing environment
  → Interpreter:
      Windows: D:\projects\myproject\.venv\Scripts\python.exe
      Ubuntu:  /home/你/projects/myproject/.venv/bin/python
  → OK
```

#### 切换解释器（快捷方式）

直接点击 **PyCharm 右下角的解释器名称**，即可快速切换。

---

### 4.4 在 PyCharm 中安装包

```
方法一：图形界面
  Settings → Project → Python Interpreter → 点 + 号
  → 搜索包名 → Install Package

方法二：内置终端（推荐）
  Alt+F12 打开终端
  conda install numpy
  pip install requests
```

**终端没有自动激活 conda 环境的解决方法：**

```
Settings → Tools → Terminal → Shell path:
  Windows: powershell.exe
  Ubuntu:  /bin/bash --login   （--login 会加载 .bashrc）

重启终端标签页后生效。
```

---

### 4.5 运行与调试

#### 配置运行参数

```
Run → Edit Configurations → + → Python

Name: 训练模型
Script path: D:\projects\myproject\train.py
Parameters: --epochs 100 --batch-size 32
Python interpreter: Python 3.12 (dl) (Conda)
Working directory: D:\projects\myproject
Environment variables: CUDA_VISIBLE_DEVICES=0
```

多个配置在顶部工具栏下拉菜单中一键切换。

#### 调试操作

```
设置断点：点击行号左侧空白处（出现红色圆点）
         或快捷键 Ctrl+F8

启动调试：Shift+F9（或点击虫子图标 🐛）

调试过程中：
  F8          Step Over：执行当前行，跳到下一行
  F7          Step Into：进入函数内部
  Shift+F8    Step Out：从函数跳出
  F9          继续运行到下一个断点
  Alt+F9      Run to Cursor：运行到光标处
  Alt+F8      Evaluate Expression：实时计算任意表达式
  Ctrl+F8     切换断点开关

条件断点：右键红色圆点 → Condition → 输入条件表达式
         （如：item > 3，只在满足条件时暂停）
```

---

### 4.6 常用快捷键速查

```
# 通用
Ctrl+Alt+S          打开设置
Ctrl+Shift+A        查找所有操作（万能命令面板）
双击 Shift           Search Everywhere（万能搜索）
Ctrl+E              最近打开的文件
Alt+F12             打开/关闭终端
Ctrl+Shift+F10      运行当前文件
Shift+F9            调试当前文件

# 编辑
Ctrl+D              复制当前行
Ctrl+Y              删除当前行
Ctrl+/              注释 / 取消注释
Ctrl+Shift+↑/↓      移动当前行
Ctrl+Alt+L          格式化代码
Ctrl+Alt+O          优化 import（删除无用 import）
Alt+Enter           快速修复 / 意图动作（最常用！）
Ctrl+Space          基本代码补全

# 导航
Ctrl+B / Ctrl+Click  跳转到定义
Ctrl+F12            文件结构大纲
Ctrl+N              搜索类名
Ctrl+Shift+N        搜索文件名
Ctrl+G              跳转到指定行号
Alt+← / Alt+→       前进 / 后退

# 重构
Shift+F6            重命名（所有引用自动更新）
Ctrl+Alt+M          提取方法
Ctrl+Alt+V          提取变量

# 版本控制
Ctrl+K              Commit（提交）
Ctrl+Shift+K        Push（推送）
Ctrl+T              Pull（拉取）
Alt+`               VCS 快速操作菜单
```

---

### 4.7 推荐插件

```
必装：
  Rainbow Brackets      彩色括号，嵌套层次清晰
  .env files support    .env 文件语法高亮
  Key Promoter X        提醒鼠标操作对应的快捷键

推荐：
  GitHub Copilot        AI 代码补全
  CodeGlance Pro        右侧缩略图导航
  CSV Editor            CSV 文件可视化编辑
  String Manipulation   字符串大小写、驼峰格式快速转换
```

安装路径：`Settings → Plugins → Marketplace`

---

### 4.8 常见问题排查

**Q：包已安装，但 PyCharm 报 "No module named xxx"**

```
原因：PyCharm 用的解释器与你安装包的环境不同。

检查：
  Settings → Python Interpreter → 查看包列表里有没有该包
  确认右下角的解释器名称是否正确

解决：切换到包含该包的正确解释器。
```

**Q：PyCharm 找不到 conda.exe**

```
Windows 路径参考：
  D:\miniforge3\Scripts\conda.exe
  C:\Users\你的用户名\miniforge3\Scripts\conda.exe

Ubuntu 路径参考：
  ~/miniforge3/bin/conda
  /opt/miniforge3/bin/conda

手动浏览填写路径即可。
```

**Q：代码在终端能跑，PyCharm 里报错**

```
排查方向：
1. 解释器不一致 → 统一解释器
2. 工作目录不同 → Run Configurations → Working directory 设为项目根目录
3. 环境变量缺失 → Run Configurations → Environment variables 补上
```

**Q：PyCharm 运行很卡**

```
Help → Edit Custom VM Options，调大内存：
  -Xms512m
  -Xmx4096m
  -XX:ReservedCodeCacheSize=512m

同时排除大文件夹（不让 PyCharm 索引）：
  右键 data/、.venv/、__pycache__/ 等目录
  → Mark Directory as → Excluded
```

**Q：.idea 目录怎么处理（多人协作）**

```gitignore
# .gitignore 中添加：
.idea/
*.iml

# 如果需要共享代码风格和运行配置，可以例外保留：
!.idea/codeStyles/
!.idea/runConfigurations/
```

---

### 4.9 完整工作流示例

```bash
# 1. 终端：创建 conda 环境并安装依赖
conda create -n myproject python=3.12
conda activate myproject
conda install numpy pandas scikit-learn
pip install fastapi uvicorn pytest

# 2. PyCharm：打开项目
File → Open → 选择项目文件夹

# 3. PyCharm：连接解释器
Settings → Python Interpreter → Add → Conda → 选 myproject 环境

# 4. 编写代码（自动补全、类型检查、快速修复）

# 5. 调试
打断点 → Shift+F9 → 查看变量 → F8 单步

# 6. 提交代码
Ctrl+K → 写 commit message → Commit
Ctrl+Shift+K → Push

# 7. 需要新包时
Alt+F12 打开终端 → pip install 新包
Settings → Python Interpreter 刷新确认包已出现
```

---

*文档整理自：Conda完整命令手册、Conda平台场景手册、Scoop完整教程、PyCharm使用教程、将Conda设为Windows默认Python，已去重、校验并按使用顺序重新组织。*
