# Windows Toast Notification for Claude Code
# This script displays a Windows 10/11 toast notification when a task is completed

param(
    [string]$Title = "Claude Code",
    [string]$Message = "Task completed successfully",
    [string]$Type = "success"
)

# Load required assemblies for Windows notifications
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
$null = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]

# Create the toast template
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

# Create XML document
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)

# Create the toast notification
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)

# Display the notification
$appId = "ClaudeCode.Notification"
try {
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
    Write-Host "[OK] Notification displayed: $Title - $Message"
    exit 0
} catch {
    Write-Host "[WARNING] Could not display notification: $_"
    exit 1
}
