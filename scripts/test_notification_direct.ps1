# Direct Windows Notification Test - More Visible
# より目立つ通知をテスト

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create a notification balloon (always visible)
$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.BalloonTipTitle = "Claude Code - TEST"
$notification.BalloonTipText = "This is a test notification. Can you see this popup?"
$notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$notification.Visible = $true

# Show the notification
$notification.ShowBalloonTip(10000)  # Show for 10 seconds

Write-Host "[INFO] Notification displayed for 10 seconds"
Write-Host "      Check your system tray (bottom-right corner)"

# Keep the script alive for the notification to display
Start-Sleep -Seconds 10

# Cleanup
$notification.Dispose()
