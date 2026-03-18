#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桂林理工大学 Dr.COM 自动登录脚本 (Python版)
功能: 自动获取参数、断线重连、完整日志
"""

import os
import sys
import time
import signal
import logging
import subprocess
import re
import requests
from datetime import datetime

# ==================== 用户配置 ====================
USER_ACCOUNT = "2120251297"
USER_PASS    = "Ycc15736431766"
HOST_IP      = "172.16.2.2"
CHECK_INTERVAL = 5       # 网络检测间隔（秒）
LOCK_FILE    = "/tmp/drcom_auto.lock"
MAX_RETRY    = 3
# ==================================================

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)
# ==================================================


def check_lock():
    """检查是否已有实例在运行"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            # 检查进程是否存活
            os.kill(old_pid, 0)
            log.error(f"脚本已在运行 (PID: {old_pid})，退出。")
            sys.exit(1)
        except (ValueError, ProcessLookupError, PermissionError):
            pass  # 旧锁文件无效，继续

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def cleanup(signum=None, frame=None):
    """退出时清理锁文件"""
    log.info("脚本已停止。")
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    sys.exit(0)


def check_network() -> bool:
    """通过 ping 检测网络连通性"""
    dns_servers = ["223.5.5.5", "119.29.29.29"]
    for dns in dns_servers:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", dns],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            # Windows 环境下 ping 参数不同
            try:
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "2000", dns],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    return True
            except Exception:
                pass
    return False


def get_params() -> dict:
    """从登录页面抓取动态参数，失败则使用默认值"""
    defaults = {"rcn": "PvX6ucDM", "v": "3504", "is_page_new": "6018"}
    try:
        resp = requests.get(
            f"http://{HOST_IP}/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
            verify=False,
        )
        page = resp.text

        def extract(key):
            m = re.search(rf'{key}=([^&"]+)', page)
            return m.group(1) if m else None

        params = {
            "rcn":         extract("rcn")         or defaults["rcn"],
            "v":           extract("v")           or defaults["v"],
            "is_page_new": extract("is_page_new") or defaults["is_page_new"],
        }
    except Exception:
        params = defaults

    return params


def do_login(params: dict) -> bool:
    """
    发送登录请求。
    返回 True 表示 HTTP 200 且网络已恢复，False 表示失败。
    """
    url = (
        f"http://{HOST_IP}/drcom/login"
        f"?callback=dr1006"
        f"&DDDDD={USER_ACCOUNT}"
        f"&upass={USER_PASS}"
        f"&0MKKey=123456&R1=0&R2=&R3=1&R6=0&para=00&v6ip=&R7=0"
        f"&login_t=0&js_status=0&is_page=1"
        f"&is_page_new={params['is_page_new']}"
        f"&terminal_type=1&lang=zh-cn"
        f"&rcn={params['rcn']}"
        f"&jsVersion=4.2.1"
        f"&v={params['v']}"
        f"&lang=zh"
    )
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Referer": f"http://{HOST_IP}/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
        ),
    }

    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = requests.get(
                url, headers=headers, timeout=8, verify=False, allow_redirects=True
            )
            if resp.status_code == 200:
                log.info(f"登录请求已发送 (HTTP 200)，等待验证... (尝试 {attempt}/{MAX_RETRY})")
                time.sleep(2)
                if check_network():
                    log.info("✅ 网络连接已恢复！")
                    return True
                else:
                    log.warning(f"服务器返回200但网络仍未通，重试 ({attempt}/{MAX_RETRY})...")
            else:
                log.error(f"请求失败，HTTP 状态码: {resp.status_code} (尝试 {attempt}/{MAX_RETRY})")
        except requests.RequestException as e:
            log.error(f"请求异常: {e} (尝试 {attempt}/{MAX_RETRY})")

        if attempt < MAX_RETRY:
            time.sleep(3)

    return False


def main():
    # 抑制 InsecureRequestWarning
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    check_lock()
    signal.signal(signal.SIGINT,  cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    log.info(f"自动登录脚本已启动 (PID: {os.getpid()})")

    while True:
        if check_network():
            log.info("网络正常，无需操作。")
        else:
            log.warning("检测到网络断开，正在尝试重新连接...")
            params = get_params()
            log.info(f"获取到参数: rcn={params['rcn']}, v={params['v']}, is_page_new={params['is_page_new']}")

            if not do_login(params):
                log.error(f"❌ 重连失败，已重试 {MAX_RETRY} 次，等待 {CHECK_INTERVAL}s 后再试...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()