#!/usr/bin/env python3
"""
test_30s.py - 30秒测试脚本 (Python版本)
用于验证实验系统
"""

import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path


def get_experiment_dir() -> Path:
    """获取实验目录"""
    # 优先使用参数
    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    # 否则使用脚本所在目录
    return Path(__file__).parent


def ensure_dir(path: Path) -> None:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def write_log(log_file: Path, message: str) -> None:
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def update_status(status_file: Path, status: str, progress: float = 0,
                  error: str = None) -> None:
    """更新状态文件"""
    with open(status_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["status"] = status
    data["progress"] = round(progress, 2)
    data["last_update_time"] = datetime.now().isoformat()

    if status == "running" and not data.get("start_time"):
        data["start_time"] = datetime.now().isoformat()

    if status in ("completed", "failed"):
        data["end_time"] = datetime.now().isoformat()

    if error:
        data["error"] = error

    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_metrics(metrics_file: Path, metrics: dict) -> None:
    """保存指标"""
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    # 路径设置
    exp_dir = get_experiment_dir()
    log_file = exp_dir / "logs" / "train.log"
    metrics_file = exp_dir / "outputs" / "metrics.json"
    status_file = exp_dir / "experiment_status.json"

    # 确保目录存在
    ensure_dir(log_file.parent)
    ensure_dir(metrics_file.parent)

    try:
        write_log(log_file, "30秒测试开始 (Python)")
        update_status(status_file, "running")

        # 模拟 30 秒训练
        total_seconds = 30
        best_value = float("inf")

        for i in range(1, total_seconds + 1):
            time.sleep(1)

            # 模拟指标变化
            value = 1.0 / i + random.random() * 0.01
            best_value = min(best_value, value)

            progress = (i / total_seconds) * 100
            update_status(status_file, "running", progress)

            write_log(
                log_file,
                f"秒 {i}/{total_seconds} - "
                f"值: {value:.4f} - 最佳: {best_value:.4f}"
            )

        # 保存结果
        metrics = {
            "test_name": "30s_test_python",
            "duration_seconds": total_seconds,
            "final_value": round(value, 4),
            "best_value": round(best_value, 4),
            "completed_at": datetime.now().isoformat()
        }
        save_metrics(metrics_file, metrics)

        update_status(status_file, "completed")
        write_log(log_file, "测试完成")
        return 0

    except Exception as e:
        error_msg = str(e)
        update_status(status_file, "failed", error=error_msg)
        write_log(log_file, f"测试失败: {error_msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())