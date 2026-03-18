import subprocess
import re
import time
import random
from datetime import datetime

def log(message):
    """带时间戳的日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def generate_random_mac():
    """生成随机MAC地址"""
    # 生成随机MAC地址，第一个字节设置为本地管理地址
    mac = [0x02, 0x00, 0x00,
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return '-'.join(map(lambda x: "%02x" % x, mac)).upper()

def change_mac_address(interface_name, new_mac=None):
    """更换网卡MAC地址（Windows方法）"""
    try:
        if new_mac is None:
            new_mac = generate_random_mac()
        
        log(f"准备更换MAC地址为: {new_mac}")
        
        # 方法1: 使用注册表修改（需要管理员权限）
        # 先获取网卡的注册表路径
        reg_query = subprocess.run(
            ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}', '/s', '/f', interface_name],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        # 查找网卡的注册表项
        lines = reg_query.stdout.split('\n')
        reg_path = None
        for i, line in enumerate(lines):
            if 'DriverDesc' in line and interface_name in line:
                # 往回找到注册表路径
                for j in range(i, -1, -1):
                    if 'HKEY_LOCAL_MACHINE' in lines[j]:
                        reg_path = lines[j].strip()
                        break
                break
        
        if reg_path:
            log(f"找到网卡注册表路径: {reg_path}")
            
            # 移除MAC地址中的连字符
            mac_no_dash = new_mac.replace('-', '')
            
            # 设置NetworkAddress值
            subprocess.run(
                ['reg', 'add', reg_path, '/v', 'NetworkAddress', '/d', mac_no_dash, '/f'],
                capture_output=True,
                encoding='gbk'
            )
            
            log("✓ MAC地址已写入注册表")
            return True
        else:
            log("✗ 未找到网卡注册表路径")
            
            # 方法2: 使用netsh命令（备用方法）
            log("尝试备用方法...")
            # 禁用网卡
            subprocess.run(
                ['netsh', 'interface', 'set', 'interface', interface_name, 'disabled'],
                capture_output=True,
                encoding='gbk'
            )
            time.sleep(2)
            
            # 启用网卡
            subprocess.run(
                ['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'],
                capture_output=True,
                encoding='gbk'
            )
            time.sleep(3)
            
            log("✓ 网卡已重启（备用方法）")
            return True
            
    except Exception as e:
        log(f"✗ 更换MAC地址时出错: {e}")
        return False

def get_wifi_interface_name():
    """获取无线网卡名称"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        for line in result.stdout.split('\n'):
            if '名称' in line or 'Name' in line:
                match = re.search(r'[:：]\s*(.+)', line)
                if match:
                    return match.group(1).strip()
        return None
    except:
        return None

def refresh_wifi_adapter():
    """刷新无线网卡"""
    try:
        log("刷新无线网卡...")
        
        interface_name = get_wifi_interface_name()
        
        if interface_name:
            subprocess.run(
                ['netsh', 'interface', 'set', 'interface', interface_name, 'disabled'],
                capture_output=True,
                encoding='gbk'
            )
            time.sleep(2)
            
            subprocess.run(
                ['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'],
                capture_output=True,
                encoding='gbk'
            )
            time.sleep(3)
            
            log("✓ 网卡刷新完成")
        else:
            subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True)
            time.sleep(1)
        
        subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True
        )
        time.sleep(2)
        
        return True
        
    except Exception as e:
        log(f"✗ 刷新网卡时出错: {e}")
        return False

def scan_wifi():
    """扫描WiFi网络"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode != 0:
            return []
        
        networks = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'SSID' in line and 'BSSID' not in line:
                ssid_match = re.search(r'SSID \d+ : (.+)', line)
                if ssid_match:
                    ssid = ssid_match.group(1).strip()
                    if ssid:
                        networks.append(ssid)
        
        return networks
        
    except Exception as e:
        log(f"✗ 扫描WiFi时出错: {e}")
        return []

def is_connected_to_wifi(wifi_name):
    """检查是否已连接到指定WiFi"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        return wifi_name in result.stdout and '已连接' in result.stdout
            
    except Exception as e:
        return False

def connect_wifi(wifi_name):
    """连接到指定的WiFi"""
    try:
        log(f"尝试连接到 [{wifi_name}]...")
        
        result = subprocess.run(
            ['netsh', 'wlan', 'connect', f'name={wifi_name}'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode == 0 or '连接请求已成功完成' in result.stdout:
            log("✓ 连接命令已发送")
            time.sleep(4)
            
            if is_connected_to_wifi(wifi_name):
                log(f"✓ 已成功连接到 [{wifi_name}]")
                return True
            else:
                log("⚠ 连接命令已发送，等待连接建立...")
                return True
        else:
            log(f"✗ 连接失败: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        log(f"✗ 连接时出错: {e}")
        return False

def test_network_connectivity():
    """测试网络连通性"""
    try:
        # ping百度测试
        result = subprocess.run(
            ['ping', '-n', '1', '-w', '2000', 'www.baidu.com'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode == 0 and 'TTL=' in result.stdout:
            return True
        
        return False
        
    except Exception as e:
        return False

def authenticate_network(username, password):
    """认证校园网络"""
    try:
        log("开始网络认证...")
        
        auth_url = (
            f"http://172.16.2.2/drcom/login?callback=dr1006"
            f"&DDDDD={username}"
            f"&upass={password}"
            f"&0MKKey=123456"
            f"&R1=0&R2=&R3=1&R6=0&para=00&v6ip=&R7=0"
            f"&login_t=0&js_status=0&is_page=1&is_page_new=892"
            f"&terminal_type=1&lang=zh-cn&rcn=AihlrxCT"
            f"&jsVersion=4.2.1&v=5621&lang=zh"
        )
        
        curl_command = [
            'curl', auth_url,
            '-H', 'Accept: */*',
            '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
            '-H', 'Connection: keep-alive',
            '-H', 'Referer: http://172.16.2.2/',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--insecure', '--connect-timeout', '5'
        ]
        
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = result.stdout.lower()
            
            if any(keyword in response for keyword in ['success', '成功', 'login_ok', 'already', '已经']):
                log("✓ 网络认证成功")
                return True
            elif any(keyword in response for keyword in ['error', '错误', 'fail']):
                log(f"✗ 认证失败")
                return False
            else:
                # 不确定的响应，通过测试网络来判断
                time.sleep(2)
                if test_network_connectivity():
                    log("✓ 认证后网络测试通过")
                    return True
                else:
                    return False
        else:
            log(f"✗ 认证请求失败")
            return False
            
    except Exception as e:
        log(f"✗ 认证时出错: {e}")
        return False

def main_loop(target_wifi, username, password):
    """主循环：持续监控和维护连接"""
    log("="*60)
    log("桂林理工大学校园网自动连接守护进程 v2.0")
    log("="*60)
    log(f"目标WiFi: {target_wifi}")
    log(f"认证账号: {username}")
    log("WiFi扫描间隔: 10秒")
    log("网络测试间隔: 20秒")
    log("支持自动更换MAC地址解决网络问题")
    log("按 Ctrl+C 停止运行")
    log("="*60)
    
    wifi_scan_counter = 0
    network_test_counter = 0
    
    wifi_connected = False
    network_authenticated = False
    failed_auth_count = 0  # 认证失败计数
    
    while True:
        try:
            # 每10秒扫描一次WiFi
            if wifi_scan_counter % 10 == 0:
                log("\n--- WiFi扫描周期 ---")
                
                if is_connected_to_wifi(target_wifi):
                    if not wifi_connected:
                        log(f"✓ 已连接到 {target_wifi}")
                        wifi_connected = True
                else:
                    if wifi_connected:
                        log(f"⚠ 与 {target_wifi} 断开连接")
                        wifi_connected = False
                        network_authenticated = False
                        failed_auth_count = 0
                    
                    log("未连接到目标WiFi，开始搜索...")
                    networks = scan_wifi()
                    
                    if not networks:
                        log("未找到任何WiFi，刷新网卡...")
                        refresh_wifi_adapter()
                        networks = scan_wifi()
                    
                    if networks:
                        log(f"找到 {len(networks)} 个WiFi")
                        
                        found_wifi = None
                        for network in networks:
                            if target_wifi.lower() == network.lower():
                                found_wifi = network
                                break
                        
                        if found_wifi:
                            log(f"✓ 找到目标WiFi: {found_wifi}")
                            connect_wifi(found_wifi)
                        else:
                            log(f"✗ 未找到 {target_wifi}")
                    else:
                        log("✗ 扫描失败")
            
            # 每20秒测试一次网络
            if network_test_counter % 20 == 0:
                log("\n--- 网络测试周期 ---")
                
                if wifi_connected:
                    log("测试网络连通性...")
                    
                    if test_network_connectivity():
                        if not network_authenticated:
                            log("✓ 网络已通，认证成功")
                            network_authenticated = True
                            failed_auth_count = 0  # 重置失败计数
                        else:
                            log("✓ 网络正常")
                    else:
                        log("✗ 网络不通，尝试认证...")
                        network_authenticated = False
                        
                        # 尝试认证
                        if authenticate_network(username, password):
                            time.sleep(3)
                            if test_network_connectivity():
                                log("✓ 认证后网络恢复")
                                network_authenticated = True
                                failed_auth_count = 0
                            else:
                                log("⚠ 认证完成但网络仍不通")
                                failed_auth_count += 1
                        else:
                            log("✗ 认证失败")
                            failed_auth_count += 1
                        
                        # 如果连续认证失败3次，尝试更换MAC地址
                        if failed_auth_count >= 3:
                            log("\n" + "!"*60)
                            log("⚠ 认证连续失败3次，尝试更换MAC地址解决")
                            log("!"*60)
                            
                            interface_name = get_wifi_interface_name()
                            if interface_name:
                                # 先断开WiFi
                                log("断开当前WiFi连接...")
                                subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True)
                                time.sleep(2)
                                
                                # 更换MAC地址
                                if change_mac_address(interface_name):
                                    log("✓ MAC地址已更换")
                                    
                                    # 刷新网卡使MAC地址生效
                                    log("刷新网卡使新MAC地址生效...")
                                    refresh_wifi_adapter()
                                    
                                    # 重新连接WiFi
                                    log("重新连接WiFi...")
                                    time.sleep(3)
                                    connect_wifi(target_wifi)
                                    time.sleep(5)
                                    
                                    # 重新认证
                                    log("使用新MAC地址进行认证...")
                                    if authenticate_network(username, password):
                                        time.sleep(3)
                                        if test_network_connectivity():
                                            log("✓✓✓ 更换MAC地址后网络恢复！")
                                            network_authenticated = True
                                            failed_auth_count = 0
                                        else:
                                            log("⚠ 更换MAC后仍无法上网")
                                            failed_auth_count = 0  # 重置计数，避免频繁更换
                                    else:
                                        log("✗ 更换MAC后认证仍失败")
                                        failed_auth_count = 0  # 重置计数
                                else:
                                    log("✗ MAC地址更换失败")
                                    failed_auth_count = 0  # 重置计数
                            else:
                                log("✗ 无法获取网卡名称")
                                failed_auth_count = 0
                else:
                    log("⚠ 未连接WiFi，跳过网络测试")
            
            # 等待1秒
            time.sleep(1)
            wifi_scan_counter += 1
            network_test_counter += 1
            
        except KeyboardInterrupt:
            log("\n收到停止信号，退出程序...")
            break
        except Exception as e:
            log(f"✗ 主循环出错: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("="*60)
    print("提示: 此脚本需要管理员权限")
    print("请右键点击命令提示符选择'以管理员身份运行'")
    print("="*60)
    print()
    
    # 配置信息
    target_wifi = "glut_Web"
    username = "2120251297"
    password = "Ycc15736431766"
    
    # 启动主循环
    main_loop(target_wifi, username, password)
