# ===== 只需要改下面这 4 行 =====
$WLAN    = "WLAN"                # 你的宽带/校园网 Wi-Fi 名称
$HOTSPOT = "以太网 3"            # 你的手机热点网卡名称
$GW      = "192.168.0.1"         # 手机热点的网关 IP (看上面查出来的)
$NODEIP  = "104.224.154.99"      # 你要走热点的那个节点 IP
# ==========================

# 1. 固定优先级 (数字越小优先级越高)
Set-NetIPInterface -InterfaceAlias $WLAN -InterfaceMetric 10
Set-NetIPInterface -InterfaceAlias $HOTSPOT -InterfaceMetric 50

# 2. 关掉热点的 IPv6 防干扰
Disable-NetAdapterBinding -Name $HOTSPOT -ComponentID ms_tcpip6

# 3. 添加静态路由 (不指定 if，让系统自己根据网关 $GW 识别网卡)
route -p add $NODEIP mask 255.255.255.255 $GW metric 1

# ===== 验证 =====
Write-Host "===== 设置后核对 =====" -ForegroundColor Green
Get-NetIPInterface -InterfaceAlias $WLAN, $HOTSPOT | Format-Table InterfaceAlias, InterfaceMetric
route print | Select-String $NODEIP

Write-Host "===== tracert 验证：国内流量应第一跳走 WLAN 网关 =====" -ForegroundColor Green
tracert -h 3 www.bilibili.com

Write-Host "===== tracert 验证：节点 IP 应第一跳走热点网关 =====" -ForegroundColor Green
tracert -h 3 $NODEIP