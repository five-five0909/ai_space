# 关闭显示器，电脑后台继续运行
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class MonitorPower {
    [DllImport("user32.dll")]
    public static extern int SendMessage(
        int hWnd,
        int hMsg,
        int wParam,
        int lParam
    );
}
"@

# 参数说明：
# hWnd = -1        广播给所有窗口
# hMsg = 0x0112   WM_SYSCOMMAND
# wParam = 0xF170 SC_MONITORPOWER
# lParam = 2      关闭显示器
[MonitorPower]::SendMessage(-1, 0x0112, 0xF170, 2)