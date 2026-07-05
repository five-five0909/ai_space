# ===== 改成你的网卡名和 IP =====
$WLAN    = "WLAN"                
$HOTSPOT = "以太网 3"            
$NODEIP  = "104.224.154.99"      
# ==========================

route delete $NODEIP
Set-NetIPInterface -InterfaceAlias $WLAN -AutomaticMetric Enabled
Set-NetIPInterface -InterfaceAlias $HOTSPOT -AutomaticMetric Enabled
Enable-NetAdapterBinding -Name $HOTSPOT -ComponentID ms_tcpip6