"""
Windowsタスクスケジューラにサービスを登録

このスクリプトは8-Layer Enforcement Systemを
Windowsタスクスケジューラに登録し、自動起動を設定します。

機能:
- Windows起動時の自動起動設定
- ログオン時のトリガー設定
- 失敗時の自動再起動設定
- タスクの削除機能

使用方法:
    # タスクスケジューラに登録（管理者権限推奨）
    python install_task_scheduler.py install

    # 削除
    python install_task_scheduler.py uninstall

    # 状態確認
    python install_task_scheduler.py status
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


def create_task_xml() -> str:
    """
    タスクスケジューラ用のXML設定を生成

    Returns:
        str: タスク定義XML
    """
    script_path = Path(__file__).parent / "service_manager.py"
    python_exe = sys.executable
    username = os.getenv('USERNAME', 'User')

    # パスのエスケープ処理
    script_path_str = str(script_path).replace('&', '&amp;')
    python_exe_str = str(python_exe).replace('&', '&amp;')

    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>8-Layer Enforcement System - Always-On Monitor</Description>
    <Author>{username}</Author>
  </RegistrationInfo>

  <Triggers>
    <!-- ログオン時に自動起動 -->
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>{os.getenv('USERDOMAIN', '')}\\{username}</UserId>
    </LogonTrigger>

    <!-- PC起動時に自動起動（オプション） -->
    <BootTrigger>
      <Enabled>false</Enabled>
    </BootTrigger>
  </Triggers>

  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>

  <Settings>
    <!-- 複数インスタンス起動を防止 -->
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>

    <!-- バッテリー動作時も実行 -->
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>

    <!-- タスク設定 -->
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>

    <!-- アイドル設定 -->
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>

    <!-- 手動実行許可 -->
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>

    <!-- 実行時間制限なし -->
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>

    <!-- 優先度：通常 -->
    <Priority>7</Priority>

    <!-- 失敗時の再起動設定 -->
    <RestartOnFailure>
      <Interval>PT5M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>

  <Actions>
    <Exec>
      <Command>{python_exe_str}</Command>
      <Arguments>"{script_path_str}" start</Arguments>
      <WorkingDirectory>{str(Path(__file__).parent).replace('&', '&amp;')}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    return xml


def install() -> bool:
    """
    タスクスケジューラにサービスを登録

    Returns:
        bool: 成功時True、失敗時False
    """
    print("=" * 60)
    print("  8-Layer Enforcement System")
    print("  タスクスケジューラ登録")
    print("=" * 60)
    print()

    # XMLファイル生成
    xml_content = create_task_xml()
    xml_file = Path(__file__).parent / "task_scheduler.xml"

    try:
        # XMLファイル保存
        with open(xml_file, 'w', encoding='utf-16') as f:
            f.write(xml_content)

        print(f"[INFO] XMLファイル生成完了: {xml_file}")

    except Exception as e:
        print(f"[ERROR] XMLファイル生成失敗: {e}")
        return False

    # schtasksコマンドで登録
    task_name = "8LayerEnforcementSystem"

    try:
        print(f"\n[INFO] タスク '{task_name}' を登録中...")

        result = subprocess.run([
            "schtasks",
            "/Create",
            "/TN", task_name,
            "/XML", str(xml_file),
            "/F"  # 既存タスクを上書き
        ], capture_output=True, text=True, encoding='cp932')

        if result.returncode == 0:
            print(f"\n[OK] タスク '{task_name}' の登録に成功しました")
            print(f"\n[INFO] 設定内容:")
            print(f"   - トリガー: ログオン時に自動起動")
            print(f"   - 失敗時: 5分後に自動再起動（最大3回）")
            print(f"   - バッテリー: 制限なし")
            print(f"\n[START] 次回ログオン時に自動起動します")
            print(f"\n[INFO] 今すぐ起動する場合:")
            print(f"     schtasks /Run /TN {task_name}")
            print(f"\n[INFO] タスクスケジューラで確認:")
            print(f"     taskschd.msc")

            # XMLファイルは保持（参照用）
            print(f"\n[INFO] XML設定ファイル: {xml_file}")

            return True
        else:
            print(f"\n[ERROR] タスクの登録に失敗しました")
            print(f"\nエラー内容:")
            print(f"{result.stderr}")
            print(f"\n[INFO] ヒント:")
            print(f"   - 管理者権限で実行してください")
            print(f"   - PowerShellの場合: Start-Process python -Verb RunAs")
            return False

    except FileNotFoundError:
        print(f"\n[ERROR] schtasksコマンドが見つかりません")
        print(f"   このスクリプトはWindows専用です")
        return False
    except Exception as e:
        print(f"\n[ERROR] 予期しないエラー: {e}")
        return False


def uninstall() -> bool:
    """
    タスクスケジューラからサービスを削除

    Returns:
        bool: 成功時True、失敗時False
    """
    print("=" * 60)
    print("  8-Layer Enforcement System")
    print("  タスクスケジューラ削除")
    print("=" * 60)
    print()

    task_name = "8LayerEnforcementSystem"

    try:
        print(f"[INFO]  タスク '{task_name}' を削除中...")

        result = subprocess.run([
            "schtasks",
            "/Delete",
            "/TN", task_name,
            "/F"
        ], capture_output=True, text=True, encoding='cp932')

        if result.returncode == 0:
            print(f"\n[OK] タスク '{task_name}' の削除に成功しました")

            # XMLファイルも削除
            xml_file = Path(__file__).parent / "task_scheduler.xml"
            if xml_file.exists():
                xml_file.unlink()
                print(f"[INFO] XMLファイルも削除しました: {xml_file}")

            return True
        else:
            print(f"\n[WARNING]  タスクが見つかりませんでした（すでに削除済み）")
            return True  # 既に削除済みなら成功扱い

    except FileNotFoundError:
        print(f"\n[ERROR] schtasksコマンドが見つかりません")
        return False
    except Exception as e:
        print(f"\n[ERROR] 予期しないエラー: {e}")
        return False


def status() -> Optional[dict]:
    """
    タスクスケジューラの登録状態を確認

    Returns:
        Optional[dict]: タスク情報、未登録の場合None
    """
    print("=" * 60)
    print("  8-Layer Enforcement System")
    print("  タスクスケジューラ状態確認")
    print("=" * 60)
    print()

    task_name = "8LayerEnforcementSystem"

    try:
        result = subprocess.run([
            "schtasks",
            "/Query",
            "/TN", task_name,
            "/FO", "LIST",
            "/V"
        ], capture_output=True, text=True, encoding='cp932')

        if result.returncode == 0:
            print(f"[OK] タスク '{task_name}' は登録されています")
            print(f"\n[INFO] 詳細情報:")
            print("-" * 60)

            # 結果をパース
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # 重要な情報のみ表示
                    if key in ['タスク名', 'TaskName', '状態', 'Status',
                              '次回の実行時刻', 'Next Run Time',
                              '前回の実行時刻', 'Last Run Time',
                              '前回の結果', 'Last Result']:
                        print(f"{key}: {value}")
                        info[key] = value

            print("-" * 60)
            print(f"\n[INFO] タスクスケジューラで詳細確認:")
            print(f"     taskschd.msc")

            return info
        else:
            print(f"[INFO]  タスク '{task_name}' は登録されていません")
            print(f"\n[INFO] 登録する場合:")
            print(f"     python {__file__} install")
            return None

    except FileNotFoundError:
        print(f"\n[ERROR] schtasksコマンドが見つかりません")
        return None
    except Exception as e:
        print(f"\n[ERROR] 予期しないエラー: {e}")
        return None


def main():
    """CLIエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description="8-Layer Enforcement System - タスクスケジューラ統合",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # タスクスケジューラに登録（管理者権限推奨）
  python install_task_scheduler.py install

  # 削除
  python install_task_scheduler.py uninstall

  # 状態確認
  python install_task_scheduler.py status

注意:
  - Windows専用のスクリプトです
  - 管理者権限での実行を推奨します
  - タスクはログオン時に自動起動されます
        """
    )

    parser.add_argument(
        'action',
        choices=['install', 'uninstall', 'status'],
        help="実行するアクション"
    )

    args = parser.parse_args()

    # Windows環境チェック
    if sys.platform != "win32":
        print("[ERROR] このスクリプトはWindows専用です")
        print(f"   現在のOS: {sys.platform}")
        sys.exit(1)

    # アクション実行
    success = False

    if args.action == 'install':
        success = install()
    elif args.action == 'uninstall':
        success = uninstall()
    elif args.action == 'status':
        result = status()
        success = True  # status は常に成功扱い

    # 終了コード設定
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
