"""
Debug Tool - Test từng bước
Hiển thị menu để chọn bước và test detect/click cho từng bước
"""

from image_detector import ImageDetector
from screen_automation import ScreenAutomation
import os
import time
import glob
import re
import csv


class StepDebugger:
    """Class để debug từng bước"""
    
    def __init__(self, window_title=None, threshold=0.8):
        """
        Khởi tạo debugger.
        
        Args:
            window_title: Tên cửa sổ cần focus (cho game)
            threshold: Ngưỡng confidence cho template matching
        """
        self.window_title = window_title
        self.threshold = threshold
        self.detector = ImageDetector(threshold=threshold)
        self.automation = ScreenAutomation(detection_threshold=threshold)
        self.steps = self._discover_steps()
        self.account_data = self._load_account_data()
    
    def _discover_steps(self):
        """Tự động phát hiện các file step*.png trong thư mục templates"""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            return []
        
        # Tìm tất cả file step*.png
        step_files = glob.glob(os.path.join(templates_dir, "step*.png"))
        step_files.extend(glob.glob(os.path.join(templates_dir, "step*.jpg")))
        
        # Sắp xếp theo số thứ tự
        def get_step_number(filename):
            match = re.search(r'step(\d+)', filename, re.IGNORECASE)
            return int(match.group(1)) if match else 999
        
        step_files.sort(key=get_step_number)
        
        # Trả về danh sách (số bước, tên file, đường dẫn đầy đủ)
        steps = []
        for filepath in step_files:
            filename = os.path.basename(filepath)
            match = re.search(r'step(\d+)', filename, re.IGNORECASE)
            if match:
                step_num = int(match.group(1))
                steps.append((step_num, filename, filepath))
        
        return steps
    
    def _load_account_data(self):
        """Đọc dữ liệu từ account.csv, chỉ lấy dòng có state trống"""
        account_file = "data/account.csv"
        if not os.path.exists(account_file):
            print(f"⚠ Không tìm thấy file: {account_file}")
            return None
        
        try:
            with open(account_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Chỉ lấy dòng có state trống
                    if not row.get('state', '').strip():
                        return {
                            'id': row.get('id', ''),
                            'user': row.get('user', ''),
                            'pass': row.get('pass', '')
                        }
            print("⚠ Không tìm thấy dòng nào có state trống trong account.csv")
            return None
        except Exception as e:
            print(f"✗ Lỗi khi đọc account.csv: {e}")
            return None
    
    def list_steps(self):
        """Hiển thị danh sách các bước có sẵn"""
        if not self.steps:
            print("\n✗ Không tìm thấy file step*.png trong thư mục templates/")
            return
        
        print("\n" + "=" * 60)
        print("DANH SÁCH CÁC BƯỚC")
        print("=" * 60)
        for step_num, filename, filepath in self.steps:
            exists = "✓" if os.path.exists(filepath) else "✗"
            print(f"{exists} Bước {step_num}: {filename}")
        print("=" * 60)
    
    def test_step_detect(self, step_num):
        """Test phát hiện ảnh cho một bước cụ thể"""
        step_info = self._get_step_info(step_num)
        if not step_info:
            return None
        
        step_num, filename, filepath = step_info
        
        print("\n" + "=" * 60)
        print(f"BƯỚC {step_num}: PHÁT HIỆN VỊ TRÍ")
        print("=" * 60)
        print(f"Template: {filename}")
        print(f"Đường dẫn: {filepath}")
        print(f"Threshold: {self.threshold}")
        
        if not os.path.exists(filepath):
            print(f"\n✗ File không tồn tại: {filepath}")
            return None
        
        result = self.detector.find_template(filepath)
        
        if result:
            x, y, confidence = result
            print(f"\n✓ THÀNH CÔNG!")
            print(f"  Tọa độ X: {x}")
            print(f"  Tọa độ Y: {y}")
            print(f"  Confidence: {confidence:.2%}")
            return (x, y, confidence)
        else:
            print("\n✗ KHÔNG TÌM THẤY")
            print("  - Kiểm tra ảnh mẫu có đang hiển thị trên màn hình không")
            print("  - Thử giảm threshold xuống 0.7 hoặc 0.6")
            return None
    
    def test_step_click(self, step_num):
        """Test click cho một bước cụ thể"""
        step_info = self._get_step_info(step_num)
        if not step_info:
            return False
        
        step_num, filename, filepath = step_info
        
        print("\n" + "=" * 60)
        print(f"BƯỚC {step_num}: CLICK")
        print("=" * 60)
        print(f"Template: {filename}")
        if self.window_title:
            print(f"Window: {self.window_title} (sẽ focus trước khi click)")
        print("\n(Bạn có 3 giây để chuẩn bị...)")
        time.sleep(3)
        
        success = self.automation.click_at_image(
            filepath,
            window_title=self.window_title
        )
        
        if success:
            print(f"\n✓ THÀNH CÔNG! Đã click vào bước {step_num}")
            return True
        else:
            print(f"\n✗ KHÔNG THÀNH CÔNG")
            print("  - Không tìm thấy ảnh mẫu để click")
            print("  - Kiểm tra lại template và màn hình")
            return False
    
    def test_step_both(self, step_num):
        """Test cả detect và click cho một bước"""
        step_info = self._get_step_info(step_num)
        if not step_info:
            return False
        
        step_num, filename, filepath = step_info
        
        print("\n" + "=" * 60)
        print(f"BƯỚC {step_num}: PHÁT HIỆN VÀ CLICK")
        print("=" * 60)
        print(f"Template: {filename}")
        if self.window_title:
            print(f"Window: {self.window_title}")
        
        # Bước 1: Detect
        result = self.test_step_detect(step_num)
        
        if result:
            x, y, confidence = result
            print(f"\n→ Đã phát hiện tại ({x}, {y})")
            
            # Bước 2: Click
            print("\n(Bạn có 3 giây trước khi click...)")
            time.sleep(3)
            
            success = self.automation.click_at_image(
                filepath,
                window_title=self.window_title
            )
            
            if success:
                print(f"\n✓ Đã click vào bước {step_num} tại ({x}, {y})")
                
                # Bước 3: Paste dữ liệu cho step3 và step4
                if step_num == 3:
                    # Step3: Paste user
                    if self.account_data and self.account_data.get('user'):
                        user = self.account_data['user']
                        print(f"\n→ Đang paste user: {user}")
                        time.sleep(0.3)  # Chờ một chút sau khi click
                        paste_success = self.automation.paste_data(user, clear_first=True)
                        if paste_success:
                            print(f"✓ Đã paste user thành công")
                        else:
                            print(f"✗ Không thể paste user")
                    else:
                        print(f"\n⚠ Không có dữ liệu user để paste")
                
                elif step_num == 4:
                    # Step4: Paste pass
                    if self.account_data and self.account_data.get('pass'):
                        password = self.account_data['pass']
                        print(f"\n→ Đang paste password: {'*' * len(password)}")
                        time.sleep(0.3)  # Chờ một chút sau khi click
                        paste_success = self.automation.paste_data(password, clear_first=True)
                        if paste_success:
                            print(f"✓ Đã paste password thành công")
                        else:
                            print(f"✗ Không thể paste password")
                    else:
                        print(f"\n⚠ Không có dữ liệu password để paste")
                
                print(f"\n✓ HOÀN TẤT! Bước {step_num}")
                return True
            else:
                print(f"\n✗ Phát hiện được nhưng không click được")
                return False
        else:
            print(f"\n✗ Không thể test click vì không tìm thấy ảnh mẫu")
            return False
    
    def test_all_steps(self):
        """Test tất cả các bước liên tiếp"""
        if not self.steps:
            print("\n✗ Không có bước nào để test")
            return
        
        # Kiểm tra dữ liệu account
        if self.account_data:
            print(f"\n✓ Đã tải dữ liệu account:")
            print(f"  ID: {self.account_data.get('id', 'N/A')}")
            print(f"  User: {self.account_data.get('user', 'N/A')}")
            print(f"  Pass: {'*' * len(self.account_data.get('pass', '')) if self.account_data.get('pass') else 'N/A'}")
        else:
            print(f"\n⚠ Không có dữ liệu account (step3 và step4 sẽ không paste được)")
        
        print("\n" + "=" * 60)
        print("TEST TẤT CẢ CÁC BƯỚC")
        print("=" * 60)
        print(f"Số bước: {len(self.steps)}")
        if self.window_title:
            print(f"Window: {self.window_title}")
        print("\n(Bạn có 5 giây để chuẩn bị...)")
        time.sleep(5)
        
        results = []
        for step_num, filename, filepath in self.steps:
            print(f"\n{'='*60}")
            print(f"Đang test BƯỚC {step_num}: {filename}")
            print(f"{'='*60}")
            
            success = self.test_step_both(step_num)
            results.append((step_num, success))
            
            if not success:
                print(f"\n⚠ Dừng lại ở bước {step_num}")
                break
            
            # Chờ một chút giữa các bước
            time.sleep(1)
        
        # Tóm tắt kết quả
        print("\n" + "=" * 60)
        print("TÓM TẮT KẾT QUẢ")
        print("=" * 60)
        for step_num, success in results:
            status = "✓" if success else "✗"
            print(f"{status} Bước {step_num}")
        print("=" * 60)
    
    def _get_step_info(self, step_num):
        """Lấy thông tin của một bước"""
        for step_info in self.steps:
            if step_info[0] == step_num:
                return step_info
        print(f"\n✗ Không tìm thấy bước {step_num}")
        return None


def main():
    """Menu chính"""
    print("\n" + "=" * 60)
    print("DEBUG TOOL - TEST TỪNG BƯỚC")
    print("=" * 60)
    
    # Cấu hình
    window_title = input("\nTên cửa sổ cần focus (Enter để bỏ qua): ").strip() or None
    threshold_input = input("Threshold (0.0-1.0, mặc định 0.8): ").strip()
    threshold = float(threshold_input) if threshold_input else 0.8
    
    debugger = StepDebugger(window_title=window_title, threshold=threshold)
    
    # Hiển thị danh sách bước
    debugger.list_steps()
    
    if not debugger.steps:
        print("\nKhông có bước nào để test. Đặt file step1.png, step2.png, ... vào thư mục templates/")
        return
    
    while True:
        print("\n" + "=" * 60)
        print("MENU")
        print("=" * 60)
        print("1. Xem danh sách bước")
        print("2. Test phát hiện vị trí (một bước)")
        print("3. Test click (một bước)")
        print("4. Test cả 2: Phát hiện + Click (một bước)")
        print("5. Test tất cả các bước liên tiếp")
        print("0. Thoát")
        print("=" * 60)
        
        choice = input("\nChọn (0-5): ").strip()
        
        if choice == "0":
            print("Tạm biệt!")
            break
        elif choice == "1":
            debugger.list_steps()
        elif choice == "2":
            step_input = input("Nhập số bước: ").strip()
            try:
                step_num = int(step_input)
                debugger.test_step_detect(step_num)
            except ValueError:
                print("Số bước không hợp lệ!")
        elif choice == "3":
            step_input = input("Nhập số bước: ").strip()
            try:
                step_num = int(step_input)
                debugger.test_step_click(step_num)
            except ValueError:
                print("Số bước không hợp lệ!")
        elif choice == "4":
            step_input = input("Nhập số bước: ").strip()
            try:
                step_num = int(step_input)
                debugger.test_step_both(step_num)
            except ValueError:
                print("Số bước không hợp lệ!")
        elif choice == "5":
            confirm = input("Test tất cả các bước? (y/n): ").strip().lower()
            if confirm == 'y':
                debugger.test_all_steps()
        else:
            print("Lựa chọn không hợp lệ!")
        
        input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()

