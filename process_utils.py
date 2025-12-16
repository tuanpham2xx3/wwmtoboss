"""
Process Utilities - Quản lý process Windows
Các hàm để kill, tìm, và quản lý process
"""

import sys
import subprocess
import os

try:
    import win32api
    import win32con
    import win32process
    import psutil
    WIN32_AVAILABLE = True
    PSUTIL_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    PSUTIL_AVAILABLE = False
    try:
        import psutil
        PSUTIL_AVAILABLE = True
    except ImportError:
        PSUTIL_AVAILABLE = False


def kill_process_by_name(process_name: str, force: bool = False) -> bool:
    """
    Kill process theo tên.
    
    Args:
        process_name: Tên process (ví dụ: "wwm.exe")
        force: True để force kill, False để terminate bình thường
    
    Returns:
        True nếu thành công, False nếu không tìm thấy hoặc lỗi
    """
    if sys.platform != 'win32':
        print("Chức năng này chỉ hoạt động trên Windows")
        return False
    
    # Loại bỏ .exe nếu có
    if process_name.lower().endswith('.exe'):
        process_name = process_name[:-4]
    
    killed = False
    
    # Phương pháp 1: Sử dụng psutil (ưu tiên)
    if PSUTIL_AVAILABLE:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        pid = proc.info['pid']
                        p = psutil.Process(pid)
                        if force:
                            p.kill()
                            print(f"✓ Đã force kill process: {proc.info['name']} (PID: {pid})")
                        else:
                            p.terminate()
                            print(f"✓ Đã terminate process: {proc.info['name']} (PID: {pid})")
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            if killed:
                return True
        except Exception as e:
            print(f"Lỗi khi dùng psutil: {e}")
    
    # Phương pháp 2: Sử dụng taskkill (fallback)
    try:
        if force:
            result = subprocess.run(
                ['taskkill', '/F', '/IM', f'{process_name}.exe'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            result = subprocess.run(
                ['taskkill', '/IM', f'{process_name}.exe'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        
        if result.returncode == 0:
            print(f"✓ Đã kill process: {process_name}.exe")
            print(result.stdout)
            return True
        else:
            if "not found" in result.stdout.lower() or "không tìm thấy" in result.stdout.lower():
                print(f"✗ Không tìm thấy process: {process_name}.exe")
            else:
                print(f"✗ Lỗi khi kill process: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Lỗi khi dùng taskkill: {e}")
        return False


def find_process(process_name: str):
    """
    Tìm process theo tên.
    
    Args:
        process_name: Tên process (ví dụ: "wwm.exe")
    
    Returns:
        List các process tìm thấy [(pid, name, ...), ...]
    """
    if sys.platform != 'win32':
        return []
    
    # Loại bỏ .exe nếu có
    if process_name.lower().endswith('.exe'):
        process_name = process_name[:-4]
    
    processes = []
    
    # Sử dụng psutil nếu có
    if PSUTIL_AVAILABLE:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"Lỗi khi tìm process: {e}")
    
    # Fallback: Sử dụng tasklist
    if not processes:
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and process_name.lower() in result.stdout.lower():
                # Parse output
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Bỏ qua header
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 2:
                            processes.append({
                                'pid': parts[1].strip('"'),
                                'name': parts[0].strip('"')
                            })
        except Exception as e:
            print(f"Lỗi khi dùng tasklist: {e}")
    
    return processes


def kill_wwm():
    """Kill process wwm.exe"""
    return kill_process_by_name("wwm.exe", force=True)


def main():
    """Menu chính"""
    print("\n" + "=" * 60)
    print("PROCESS UTILITIES - Quản lý Process")
    print("=" * 60)
    print("\n1. Tìm process wwm.exe")
    print("2. Kill process wwm.exe (force)")
    print("3. Kill process wwm.exe (bình thường)")
    print("4. Tìm process khác")
    print("5. Kill process khác")
    print("0. Thoát")
    print("=" * 60)
    
    choice = input("\nChọn (0-5): ").strip()
    
    if choice == "1":
        processes = find_process("wwm.exe")
        if processes:
            print(f"\n✓ Tìm thấy {len(processes)} process:")
            for proc in processes:
                print(f"  - PID: {proc['pid']}, Name: {proc['name']}")
                if 'memory_mb' in proc:
                    print(f"    Memory: {proc['memory_mb']:.2f} MB")
        else:
            print("\n✗ Không tìm thấy process wwm.exe")
    
    elif choice == "2":
        print("\nĐang kill process wwm.exe (force)...")
        success = kill_process_by_name("wwm.exe", force=True)
        if success:
            print("✓ Hoàn tất!")
        else:
            print("✗ Không thành công")
    
    elif choice == "3":
        print("\nĐang terminate process wwm.exe...")
        success = kill_process_by_name("wwm.exe", force=False)
        if success:
            print("✓ Hoàn tất!")
        else:
            print("✗ Không thành công")
    
    elif choice == "4":
        process_name = input("Nhập tên process (ví dụ: chrome.exe): ").strip()
        if process_name:
            processes = find_process(process_name)
            if processes:
                print(f"\n✓ Tìm thấy {len(processes)} process:")
                for proc in processes:
                    print(f"  - PID: {proc['pid']}, Name: {proc['name']}")
            else:
                print(f"\n✗ Không tìm thấy process: {process_name}")
    
    elif choice == "5":
        process_name = input("Nhập tên process để kill (ví dụ: chrome.exe): ").strip()
        force_input = input("Force kill? (y/n, mặc định y): ").strip().lower()
        force = force_input != 'n'
        if process_name:
            success = kill_process_by_name(process_name, force=force)
            if success:
                print("✓ Hoàn tất!")
            else:
                print("✗ Không thành công")
    
    elif choice == "0":
        print("Tạm biệt!")
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()

