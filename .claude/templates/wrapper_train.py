# wrapper_train.py
# Python 训练包装器 - 用于集成现有训练脚本
# 自动处理状态更新和指标记录

"""
使用方法:
1. 复制此文件到实验目录
2. 修改 TRAIN_SCRIPT 和参数
3. 通过 run_experiment.ps1 调用
"""

import json
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path


class ExperimentWrapper:
    """实验包装器"""

    def __init__(self, experiment_dir: str = None):
        # 获取实验目录
        if experiment_dir:
            self.exp_dir = Path(experiment_dir)
        else:
            self.exp_dir = Path(__file__).parent

        # 路径
        self.status_file = self.exp_dir / "experiment_status.json"
        self.log_file = self.exp_dir / "logs" / "train.log"
        self.metrics_file = self.exp_dir / "outputs" / "metrics.json"
        self.output_dir = self.exp_dir / "outputs"

        # 确保目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO") -> None:
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f"[{timestamp}] [{level}] {message}"

        # 写入文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        # 输出到控制台
        if level == "ERROR":
            print(line, file=sys.stderr)
        else:
            print(line)

    def update_status(self, status: str, **kwargs) -> None:
        """更新状态文件"""
        # 读取现有状态
        if self.status_file.exists():
            with open(self.status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        # 更新字段
        data["status"] = status
        data["last_update_time"] = datetime.now().isoformat()

        # 特殊处理
        if status == "running" and not data.get("start_time"):
            data["start_time"] = datetime.now().isoformat()

        if status in ("completed", "failed"):
            data["end_time"] = datetime.now().isoformat()

        # 更新额外字段
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value

        # 保存
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_metrics(self, metrics: dict) -> None:
        """保存指标"""
        metrics["saved_at"] = datetime.now().isoformat()
        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        self.log(f"指标已保存: {self.metrics_file}")

    def run_training(self, command: list, env: dict = None) -> int:
        """
        执行训练命令

        Args:
            command: 命令列表，如 ["python", "train.py", "--epochs", "100"]
            env: 额外环境变量

        Returns:
            退出码
        """
        # 合并环境变量
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        # 设置输出目录
        full_env["OUTPUT_DIR"] = str(self.output_dir)

        self.log(f"执行命令: {' '.join(command)}")
        self.update_status("running")

        try:
            # 启动进程
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                env=full_env,
                cwd=self.exp_dir
            )

            # 实时输出日志
            for line in process.stdout:
                line = line.rstrip()
                self.log(line)

                # 尝试解析进度（可自定义）
                self._parse_progress(line)

            # 等待完成
            exit_code = process.wait()

            if exit_code == 0:
                self.update_status("completed")
                self.log("训练完成")
            else:
                self.update_status("failed", error=f"退出码: {exit_code}")
                self.log(f"训练失败: 退出码 {exit_code}", level="ERROR")

            return exit_code

        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            self.update_status("failed", error=error_msg, traceback=tb)
            self.log(f"训练异常: {error_msg}", level="ERROR")
            self.log(tb, level="ERROR")
            return 1

    def _parse_progress(self, line: str) -> None:
        """
        从日志行解析进度
        子类可重写此方法以适配不同训练框架

        示例格式:
        - "Epoch 10/100" -> progress=10%
        - "epoch: 10, loss: 0.5" -> current_epoch=10
        """
        import re

        # 匹配 "Epoch X/Y" 或 "epoch: X"
        match = re.search(r"[Ee]poch[:\s]+(\d+)(?:/(\d+))?", line)
        if match:
            current = int(match.group(1))
            total = int(match.group(2)) if match.group(2) else None

            if total:
                progress = (current / total) * 100
                self.update_status("running",
                                   current_epoch=current,
                                   total_epochs=total,
                                   progress=progress)
            else:
                self.update_status("running", current_epoch=current)

        # 匹配 "loss: X.XXX"
        match = re.search(r"loss[:\s]+([\d.]+)", line, re.IGNORECASE)
        if match:
            loss = float(match.group(1))
            # 可选：更新最佳指标


def main():
    """主函数"""
    # ========================================
    # 配置区域 - 根据实际任务修改
    # ========================================

    # 训练脚本路径（相对于项目根目录或绝对路径）
    TRAIN_SCRIPT = "train.py"

    # 训练参数
    TRAIN_ARGS = [
        "--epochs", "100",
        "--batch-size", "32",
        "--lr", "0.001"
    ]

    # 额外环境变量
    EXTRA_ENV = {
        # "CUDA_VISIBLE_DEVICES": "0"
    }

    # ========================================
    # 执行训练
    # ========================================

    # 获取实验目录（从参数或脚本位置）
    exp_dir = sys.argv[1] if len(sys.argv) > 1 else None

    # 创建包装器
    wrapper = ExperimentWrapper(exp_dir)

    # 构建命令
    command = [sys.executable, TRAIN_SCRIPT] + TRAIN_ARGS

    # 执行
    exit_code = wrapper.run_training(command, EXTRA_ENV)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())