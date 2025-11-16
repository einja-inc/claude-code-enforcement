# Multi-Method Windows Notification
# 3つの方法で通知を送信して確実に届ける

param(
    [string]$Title = "Claude Code",
    [string]$Message = "Task completed successfully"
)

$success = $false

# Method 1: Toast Notification (Windows 10/11)
try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
    $null = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]

    $template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$Title</text>
            <text>$Message</text>
        </binding>
    </visual>
    <audio src="ms-winsoundevent:Notification.Default" />
</toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("ClaudeCode").Show($toast)

    Write-Host "[OK] Toast notification sent"
    $success = $true
} catch {
    Write-Host "[WARNING] Toast notification failed: $_"
}

# Method 2: Balloon Tip (System Tray)
try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $notification = New-Object System.Windows.Forms.NotifyIcon
    $notification.Icon = [System.Drawing.SystemIcons]::Information
    $notification.BalloonTipTitle = $Title
    $notification.BalloonTipText = $Message
    $notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
    $notification.Visible = $true
    $notification.ShowBalloonTip(5000)

    Write-Host "[OK] Balloon tip notification sent"
    $success = $true

    # Keep alive briefly
    Start-Sleep -Milliseconds 500
    $notification.Dispose()
} catch {
    Write-Host "[WARNING] Balloon tip failed: $_"
}

# Method 3: PowerShell BurntToast module (if available)
try {
    if (Get-Module -ListAvailable -Name BurntToast) {
        Import-Module BurntToast
        New-BurntToastNotification -Text $Title, $Message -Sound Default
        Write-Host "[OK] BurntToast notification sent"
        $success = $true
    }
} catch {
    # Silently fail if module not available
}

# Method 4: Windows Form Message Box (fallback - very visible)
if (-not $success) {
    try {
        Add-Type -AssemblyName System.Windows.Forms
        $result = [System.Windows.Forms.MessageBox]::Show(
            $Message,
            $Title,
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information,
            [System.Windows.Forms.MessageBoxDefaultButton]::Button1,
            [System.Windows.Forms.MessageBoxOptions]::DefaultDesktopOnly
        )
        Write-Host "[OK] Message box displayed"
        $success = $true
    } catch {
        Write-Host "[ERROR] All notification methods failed"
    }
}

if ($success) {
    exit 0
} else {
    exit 1
}
