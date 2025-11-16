# Setup VS Code Hooks Directory

$settingsPath = "C:\Users\musta\AppData\Roaming\Code\User\settings.json"

Write-Host ""
Write-Host "================================================================"
Write-Host "  VS Code Hooks Configuration"
Write-Host "================================================================"
Write-Host ""

# Backup settings
$backupPath = "$settingsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $settingsPath $backupPath
Write-Host "[INFO] Backup created: $backupPath"
Write-Host ""

# Read current settings
$json = Get-Content $settingsPath | ConvertFrom-Json

# Add hooks directory
$json | Add-Member -NotePropertyName "claude.hooksDirectory" -NotePropertyValue "C:\Users\musta\.claude\hooks" -Force

# Save settings
$json | ConvertTo-Json -Depth 10 | Set-Content $settingsPath

Write-Host "[SUCCESS] VS Code settings updated!"
Write-Host ""
Write-Host "Added configuration:"
Write-Host "  claude.hooksDirectory: C:\Users\musta\.claude\hooks"
Write-Host ""
Write-Host "================================================================"
Write-Host "  Next Steps"
Write-Host "================================================================"
Write-Host ""
Write-Host "1. Restart VS Code (if open)"
Write-Host "2. Submit a test prompt"
Write-Host "3. Check for:"
Write-Host "   - ULTRA THINK MODE reminder (before response)"
Write-Host "   - Desktop notification (after response)"
Write-Host ""
