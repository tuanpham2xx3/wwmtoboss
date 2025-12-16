"""
Script nhanh để kill process wwm.exe
"""

from process_utils import kill_wwm

if __name__ == "__main__":
    print("Đang kill process wwm.exe...")
    success = kill_wwm()
    if success:
        print("✓ Đã kill wwm.exe thành công!")
    else:
        print("✗ Không tìm thấy hoặc không thể kill wwm.exe")

