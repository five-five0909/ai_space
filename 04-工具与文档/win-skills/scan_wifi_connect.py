import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import subprocess
import re
import time
import random
from datetime import datetime

def log(message):
    """Log output with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def generate_random_mac():
    """Generate a random MAC address"""
    mac = [0x02, 0x00, 0x00,
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return '-'.join(map(lambda x: "%02x" % x, mac)).upper()

def change_mac_address(interface_name, new_mac=None):
    """Change NIC MAC address (Windows method)"""
    try:
        if new_mac is None:
            new_mac = generate_random_mac()

        log(f"[ACTION] Preparing to change MAC address to: {new_mac}")

        reg_query = subprocess.run(
            ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}', '/s', '/f', interface_name],
            capture_output=True,
            text=True,
            encoding='gbk'
        )

        lines = reg_query.stdout.split('\n')
        reg_path = None
        for i, line in enumerate(lines):
            if 'DriverDesc' in line and interface_name in line:
                for j in range(i, -1, -1):
                    if 'HKEY_LOCAL_MACHINE' in lines[j]:
                        reg_path = lines[j].strip()
                        break
                break

        if reg_path:
            subprocess.run(
                ['reg', 'add', reg_path, '/v', 'NetworkAddress', '/d', new_mac.replace('-', ''), '/f'],
                capture_output=True,
                encoding='gbk'
            )
            log("[OK] MAC address written to registry")
            return True
        else:
            log("[FAIL] NIC registry path not found, Trying fallback method...")
            subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'disabled'], capture_output=True, encoding='gbk')
            time.sleep(2)
            subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'], capture_output=True, encoding='gbk')
            time.sleep(3)
            log("[OK] NIC restarted (fallback method)")
            return True
    except Exception as e:
        log(f"[ERR] Error changing MAC address: {e}")
        return False

def get_wifi_interface_name():
    """Get wireless NIC name"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, encoding='gbk')
        for line in result.stdout.split('\n'):
            if 'Name' in line or '\u540d\u79f0' in line:
                match = re.search(r'[:]\s*(.+)', line)
                if match:
                    return match.group(1).strip()
        return None
    except:
        return None

def refresh_wifi_adapter():
    """Refresh wireless NIC"""
    try:
        log("[ACTION] Refreshing wireless NIC...")
        interface_name = get_wifi_interface_name()
        if interface_name:
            subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'disabled'], capture_output=True, encoding='gbk')
            time.sleep(2)
            subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'], capture_output=True, encoding='gbk')
            time.sleep(3)
            log("[OK] NIC refresh complete")
        else:
            subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True)
            time.sleep(1)

        subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], capture_output=True)
        time.sleep(2)
        return True
    except Exception as e:
        log(f"[ERR] Error refreshing NIC: {e}")
        return False

def scan_wifi():
    """Scan WiFi networks"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True, encoding='gbk')
        if result.returncode != 0: return []
        networks = []
        for line in result.stdout.split('\n'):
            if 'SSID' in line and 'BSSID' not in line:
                ssid_match = re.search(r'SSID \d+ : (.+)', line)
                if ssid_match and ssid_match.group(1).strip():
                    networks.append(ssid_match.group(1).strip())
        return networks
    except Exception as e:
        log(f"[ERR] Error scanning WiFi: {e}")
        return []

def is_connected_to_wifi(wifi_name):
    """Check if connected to specified WiFi"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, encoding='gbk')
        return wifi_name in result.stdout and ('\u5df2\u8fde\u63a5' in result.stdout or 'Connected' in result.stdout)
    except:
        return False

def connect_wifi(wifi_name):
    """Connect to specified WiFi"""
    try:
        log(f"[ACTION] Executing connect to [{wifi_name}]...")
        result = subprocess.run(['netsh', 'wlan', 'connect', f'name={wifi_name}'], capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0 or '\u8fde\u63a5\u8bf7\u6c42\u5df2\u6210\u529f\u5b8c\u6210' in result.stdout or 'successfully' in result.stdout.lower():
            time.sleep(4)
            if is_connected_to_wifi(wifi_name):
                log(f"[OK] Successfully connected to [{wifi_name}]")
                return True
            else:
                log("[WAIT] Connection command sent, waiting for OS...")
                return True
        else:
            log(f"[FAIL] Connection failed: {result.stdout.strip()}")
            return False
    except Exception as e:
        log(f"[ERR] Error during connection: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity"""
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', '2000', 'www.baidu.com'], capture_output=True, text=True, encoding='gbk')
        return result.returncode == 0 and 'TTL=' in result.stdout
    except:
        return False

def authenticate_network(username, password):
    """Authenticate campus network"""
    try:
        log("[ACTION] Sending Web Authentication Request...")
        auth_url = (
            f"http://172.16.2.2/drcom/login?callback=dr1006"
            f"&DDDDD={username}&upass={password}&0MKKey=123456"
            f"&R1=0&R2=&R3=1&R6=0&para=00&v6ip=&R7=0"
            f"&login_t=0&js_status=0&is_page=1&is_page_new=892"
            f"&terminal_type=1&lang=zh-cn&rcn=AihlrxCT"
            f"&jsVersion=4.2.1&v=5621&lang=zh"
        )
        curl_command = [
            'curl', auth_url, '-H', 'Accept: */*', '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
            '-H', 'Connection: keep-alive', '-H', 'Referer: http://172.16.2.2/',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--insecure', '--connect-timeout', '5'
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            response = result.stdout.lower()
            if any(keyword in response for keyword in ['success', 'login_ok', 'already']):
                log("[OK] Web Authentication successful")
                return True
            elif any(keyword in response for keyword in ['error', 'fail']):
                log("[FAIL] Web Authentication rejected")
                return False
            else:
                time.sleep(2)
                if test_network_connectivity():
                    log("[OK] Network online after auth attempt")
                    return True
                return False
        else:
            log("[FAIL] Auth HTTP request failed")
            return False
    except Exception as e:
        log(f"[ERR] Error during authentication: {e}")
        return False

def main_loop(target_wifi, username, password):
    log("=" * 60)
    log("GLUT Auto-Connect Service Started (Quiet Mode)")
    log("Logs will only output when disconnected or acting.")
    log("=" * 60)

    wifi_scan_counter = 0
    network_test_counter = 0

    wifi_connected = False
    network_authenticated = False
    failed_auth_count = 0

    while True:
        try:
            # 每 10 秒静默检查一次 WiFi 状态
            if wifi_scan_counter % 10 == 0:
                if is_connected_to_wifi(target_wifi):
                    if not wifi_connected:
                        log(f"[STATE] WiFi Connected to: {target_wifi}")
                        wifi_connected = True
                else:
                    if wifi_connected:
                        log(f"[WARN] WiFi Disconnected from {target_wifi}! Initiating recovery...")
                        wifi_connected = False
                        network_authenticated = False
                        failed_auth_count = 0

                    networks = scan_wifi()
                    if not networks:
                        refresh_wifi_adapter()
                        networks = scan_wifi()

                    if networks:
                        found_wifi = None
                        for network in networks:
                            if target_wifi.lower() == network.lower():
                                found_wifi = network
                                break
                        if found_wifi:
                            connect_wifi(found_wifi)

            # 每 20 秒静默检查一次互联网状态
            if network_test_counter % 20 == 0:
                if wifi_connected:
                    if test_network_connectivity():
                        if not network_authenticated:
                            log("[STATE] Internet is ONLINE.")
                            network_authenticated = True
                            failed_auth_count = 0
                        # 如果 network_authenticated 为 True，说明网络一直正常，这里不再输出废话日志
                    else:
                        if network_authenticated:
                            log("[WARN] Internet connection LOST! Attempting re-authentication...")
                        network_authenticated = False

                        if authenticate_network(username, password):
                            time.sleep(3)
                            if test_network_connectivity():
                                log("[STATE] Internet restored after Auth.")
                                network_authenticated = True
                                failed_auth_count = 0
                            else:
                                failed_auth_count += 1
                        else:
                            failed_auth_count += 1

                        # MAC修改机制
                        if failed_auth_count >= 3:
                            log("\n" + "!" * 50)
                            log("[CRITICAL] Auth failed 3 times. Executing MAC Reset!")
                            log("!" * 50)

                            interface_name = get_wifi_interface_name()
                            if interface_name:
                                subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True)
                                time.sleep(2)

                                if change_mac_address(interface_name):
                                    refresh_wifi_adapter()
                                    time.sleep(3)
                                    connect_wifi(target_wifi)
                                    time.sleep(5)

                                    if authenticate_network(username, password):
                                        time.sleep(3)
                                        if test_network_connectivity():
                                            log("[STATE] INTERNET RESTORED AFTER MAC RESET!")
                                            network_authenticated = True
                                            failed_auth_count = 0
                            else:
                                failed_auth_count = 0
                
            time.sleep(1)
            wifi_scan_counter += 1
            network_test_counter += 1

        except KeyboardInterrupt:
            log("Service stopping...")
            break
        except Exception as e:
            log(f"[ERR] Unexpected Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    target_wifi = "glut_Web"
    username = "2120251297"
    password = "Ycc15736431766"

    main_loop(target_wifi, username, password)