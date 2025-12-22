"""
Auto Run Script - Chạy tự động các step 1-10 với retry logic
"""

from image_detector import ImageDetector
from screen_automation import ScreenAutomation
from process_utils import kill_process_by_name
import os
import time
import csv
import glob
import re


class AutoRunner:
    """Class để tự động chạy các step với retry logic"""
    
    def __init__(self, window_title=None, threshold=0.8, max_retries=10, retry_delay=2.0):
        """
        Khởi tạo AutoRunner.
        
        Args:
            window_title: Tên cửa sổ cần focus (cho game)
            threshold: Ngưỡng confidence cho template matching
            max_retries: Số lần retry tối đa cho mỗi step (0 = vô hạn)
            retry_delay: Thời gian chờ giữa các lần retry (giây)
        """
        self.window_title = window_title
        self.threshold = threshold
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.detector = ImageDetector(threshold=threshold)
        self.automation = ScreenAutomation(detection_threshold=threshold)
        self.steps = self._discover_steps()
        self.current_account = None
    
    def _discover_steps(self):
        """Tự động phát hiện các file step*.png trong thư mục templates"""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            return []
        
        step_files = glob.glob(os.path.join(templates_dir, "step*.png"))
        step_files.extend(glob.glob(os.path.join(templates_dir, "step*.jpg")))
        
        def get_step_number(filename):
            match = re.search(r'step(\d+)', filename, re.IGNORECASE)
            return int(match.group(1)) if match else 999
        
        step_files.sort(key=get_step_number)
        
        steps = []
        for filepath in step_files:
            filename = os.path.basename(filepath)
            match = re.search(r'step(\d+)', filename, re.IGNORECASE)
            if match:
                step_num = int(match.group(1))
                steps.append((step_num, filename, filepath))
        
        return steps
    
    def _load_next_account(self):
        """Đọc account tiếp theo có state trống từ account.csv"""
        account_file = "data/account.csv"
        if not os.path.exists(account_file):
            print(f"✗ Không tìm thấy file: {account_file}")
            return None
        
        try:
            # Đọc tất cả dòng
            accounts = []
            with open(account_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    accounts.append(row)
            
            # Tìm dòng có state trống
            for account in accounts:
                if not account.get('state', '').strip():
                    self.current_account = account
                    return account
            
            return None
        except Exception as e:
            print(f"✗ Lỗi khi đọc account.csv: {e}")
            return None
    
    def run_step(self, step_num, retry_count=0):
        """
        Chạy một step với retry logic.
        
        Args:
            step_num: Số thứ tự step
            retry_count: Số lần đã retry
        
        Returns:
            True nếu thành công, False nếu không
        """
        step_info = self._get_step_info(step_num)
        if not step_info:
            print(f"✗ Không tìm thấy step {step_num}")
            return False
        
        step_num, filename, filepath = step_info
        
        print(f"\n{'='*60}")
        print(f"BƯỚC {step_num}: {filename}")
        if retry_count > 0:
            print(f"(Retry lần {retry_count})")
        print(f"{'='*60}")
        
        # Detect
        result = self.detector.find_template(filepath)
        
        if not result:
            # Không phát hiện được, retry
            # Step 8: Nếu retry quá 10 lần thì chuyển sang step 9
            if step_num == 8 and retry_count >= 10:
                print(f"✗ Step 8 không phát hiện được sau 10 lần retry")
                print(f"→ Tự động chuyển sang step 9")
                return "skip"  # Trả về signal để skip và chuyển sang step 9
            
            if self.max_retries == 0 or retry_count < self.max_retries:
                print(f"✗ Không phát hiện được, đợi {self.retry_delay}s và retry...")
                time.sleep(self.retry_delay)
                return self.run_step(step_num, retry_count + 1)
            else:
                print(f"✗ Không phát hiện được sau {retry_count} lần retry")
                # Step 8: Bỏ qua nếu vượt quá retry (fallback, nhưng đã xử lý ở trên)
                if step_num == 8:
                    print(f"→ Step 8 vượt quá retry, sẽ bỏ qua và tiếp tục")
                    return "skip"  # Trả về signal để skip
                else:
                    print(f"→ Vượt quá số lần retry, sẽ kill wwm.exe và chạy lại từ step 1")
                    return "restart"  # Trả về signal để restart
        
        x, y, confidence = result
        print(f"✓ Phát hiện tại ({x}, {y}), confidence: {confidence:.2%}")
        
        # Click
        time.sleep(0.5)  # Chờ một chút trước khi click
        success = self.automation.click_at_image(
            filepath,
            window_title=self.window_title
        )
        
        if not success:
            # Click không thành công, retry
            # Step 8: Nếu retry quá 10 lần thì chuyển sang step 9
            if step_num == 8 and retry_count >= 10:
                print(f"✗ Step 8 click không thành công sau 10 lần retry")
                print(f"→ Tự động chuyển sang step 9")
                return "skip"  # Trả về signal để skip và chuyển sang step 9
            
            if self.max_retries == 0 or retry_count < self.max_retries:
                print(f"✗ Click không thành công, đợi {self.retry_delay}s và retry...")
                time.sleep(self.retry_delay)
                return self.run_step(step_num, retry_count + 1)
            else:
                print(f"✗ Click không thành công sau {retry_count} lần retry")
                # Step 8: Bỏ qua nếu vượt quá retry (fallback, nhưng đã xử lý ở trên)
                if step_num == 8:
                    print(f"→ Step 8 vượt quá retry, sẽ bỏ qua và tiếp tục")
                    return "skip"  # Trả về signal để skip
                else:
                    print(f"→ Vượt quá số lần retry, sẽ kill wwm.exe và chạy lại từ step 1")
                    return "restart"  # Trả về signal để restart
        
        print(f"✓ Đã click thành công")
        
        # Paste dữ liệu cho step4 và step6
        if step_num == 4 and self.current_account:
            # Step4: Paste user
            user = self.current_account.get('user', '')
            if user:
                print(f"→ Đang paste user: {user}")
                time.sleep(0.3)
                self.automation.paste_data(user, clear_first=True)
                print(f"✓ Đã paste user")
        
        elif step_num == 6 and self.current_account:
            # Step6: Paste pass
            password = self.current_account.get('pass', '')
            if password:
                print(f"→ Đang paste password: {'*' * len(password)}")
                time.sleep(0.3)
                self.automation.paste_data(password, clear_first=True)
                print(f"✓ Đã paste password")
        
        elif step_num == 9:
            # Step9: Đợi 20 giây rồi nhấn phím R 4 lần, mỗi lần cách nhau 1 giây
            print(f"\n{'='*60}")
            print("SAU STEP 9: ĐỢI 20 GIÂY RỒI NHẤN PHÍM R 4 LẦN")
            print(f"{'='*60}")
            print("→ Đang đợi 20 giây...")
            time.sleep(20.0)
            print("→ Đang nhấn phím R 4 lần (mỗi lần cách nhau 1 giây)...")
            self.automation.press_key('r', times=4, interval=1.0, window_title=self.window_title)
            print(f"✓ Đã nhấn phím R 4 lần")
        
        elif step_num == 10:
            # Step10: Bước mới (chỉ detect và click như các step thông thường)
            pass
        
        elif step_num == 11:
            # Step11: Sau khi click thành công, kill wwm.exe và kết thúc vòng lặp
            print(f"\n{'='*60}")
            print("SAU STEP 11: KẾT THÚC VÒNG LẶP")
            print(f"{'='*60}")
            print("→ Đang kill process wwm.exe...")
            kill_process_by_name("wwm.exe", force=True)
            time.sleep(2)  # Chờ sau khi kill
            print(f"✓ Đã kill wwm.exe")
            return "end_loop"  # Trả về signal để kết thúc vòng lặp
        
        return True
    
    def _get_step_info(self, step_num):
        """Lấy thông tin của một bước"""
        for step_info in self.steps:
            if step_info[0] == step_num:
                return step_info
        return None
    
    def run_all_steps(self):
        """Chạy tất cả các step từ 1 đến 11 liên tiếp, với restart logic nếu vượt quá retry"""
        if not self.steps:
            print("✗ Không tìm thấy step nào")
            return False
        
        # Sắp xếp steps theo số thứ tự
        sorted_steps = sorted(self.steps, key=lambda x: x[0])
        
        max_restart_attempts = 3  # Số lần restart tối đa
        restart_count = 0
        
        while restart_count <= max_restart_attempts:
            if restart_count > 0:
                print(f"\n{'='*60}")
                print(f"RESTART LẦN {restart_count} - CHẠY LẠI TỪ STEP 1")
                print(f"{'='*60}")
                time.sleep(2)  # Chờ một chút trước khi restart
            
            print(f"\n{'='*60}")
            print(f"BẮT ĐẦU CHẠY {len(sorted_steps)} BƯỚC")
            print(f"{'='*60}")
            
            all_steps_completed = True
            for step_num, filename, filepath in sorted_steps:
                result = self.run_step(step_num)
                
                if result == "restart":
                    # Vượt quá retry, kill wwm.exe và restart
                    print(f"\n{'='*60}")
                    print("KILL PROCESS wwm.exe (do vượt quá retry)")
                    print(f"{'='*60}")
                    kill_process_by_name("wwm.exe", force=True)
                    time.sleep(3)  # Chờ sau khi kill
                    restart_count += 1
                    all_steps_completed = False
                    break  # Break khỏi vòng lặp step, quay lại đầu vòng lặp restart
                
                elif result == "skip":
                    # Step 8: Bỏ qua và tiếp tục
                    print(f"\n→ Đã bỏ qua step {step_num}, tiếp tục với step tiếp theo")
                    time.sleep(0.5)
                    continue
                
                elif result == "end_loop":
                    # Step 11: Kết thúc vòng lặp
                    print(f"\n→ Step 11 đã hoàn thành, kết thúc vòng lặp")
                    return "end_loop"
                
                elif not result:
                    print(f"\n✗ Dừng lại ở step {step_num}")
                    return False
                
                # Chờ một chút giữa các step
                time.sleep(0.5)
            
            # Nếu đã hoàn thành tất cả step (không bị restart)
            if all_steps_completed:
                print(f"\n{'='*60}")
                print("✓ HOÀN TẤT TẤT CẢ CÁC BƯỚC")
                print(f"{'='*60}")
                return True
        
        # Nếu vượt quá số lần restart
        print(f"\n✗ Đã restart {restart_count} lần nhưng vẫn không thành công")
        return False
    
    def update_account_state(self, account_id, state="done"):
        """
        Cập nhật state trong account.csv.
        
        Args:
            account_id: ID của account cần cập nhật
            state: State mới (mặc định: "done")
        """
        account_file = "data/account.csv"
        if not os.path.exists(account_file):
            print(f"✗ Không tìm thấy file: {account_file}")
            return False
        
        try:
            # Đọc tất cả dòng
            accounts = []
            with open(account_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    accounts.append(row)
            
            # Cập nhật state cho account có ID tương ứng
            updated = False
            for account in accounts:
                if account.get('id', '') == str(account_id):
                    account['state'] = state
                    updated = True
                    break
            
            if not updated:
                print(f"✗ Không tìm thấy account với ID: {account_id}")
                return False
            
            # Ghi lại file
            with open(account_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(accounts)
            
            print(f"✓ Đã cập nhật state của account {account_id} thành '{state}'")
            return True
        except Exception as e:
            print(f"✗ Lỗi khi cập nhật account.csv: {e}")
            return False
    
    def run_loop(self, num_iterations):
        """
        Vòng lặp chính: chạy các step, cập nhật account, kill wwm.exe, lặp lại.
        
        Args:
            num_iterations: Số vòng lặp (0 = vô hạn cho đến khi hết account)
        """
        iteration = 0
        
        while True:
            iteration += 1
            
            if num_iterations > 0 and iteration > num_iterations:
                print(f"\n{'='*60}")
                print(f"ĐÃ HOÀN TẤT {num_iterations} VÒNG LẶP")
                print(f"{'='*60}")
                break
            
            # Clear màn hình trước mỗi vòng lặp
            os.system('cls')
            
            print(f"\n{'='*60}")
            print(f"VÒNG LẶP {iteration}")
            print(f"{'='*60}")
            
            # Tải account tiếp theo
            account = self._load_next_account()
            if not account:
                print("\n✗ Không còn account nào có state trống")
                break
            
            account_id = account.get('id', '')
            print(f"\n✓ Đã tải account ID: {account_id}")
            print(f"  User: {account.get('user', 'N/A')}")
            print(f"  Pass: {'*' * len(account.get('pass', '')) if account.get('pass') else 'N/A'}")
            
            # Chạy tất cả các step
            result = self.run_all_steps()
            
            if result == "end_loop":
                # Step 11 đã kill wwm.exe và kết thúc vòng lặp
                # Cập nhật state và kết thúc
                self.update_account_state(account_id, "done")
                print(f"\n✓ Hoàn tất vòng lặp {iteration} (đã kết thúc ở step 11)")
                break  # Kết thúc vòng lặp
            elif result:
                # Các step đã hoàn thành thành công (trường hợp này không xảy ra vì step 11 sẽ trả về "end_loop")
                # Nhưng để an toàn, vẫn cập nhật state
                self.update_account_state(account_id, "done")
                
                # Kill wwm.exe (phòng trường hợp không phải step 10)
                print(f"\n{'='*60}")
                print("KILL PROCESS wwm.exe")
                print(f"{'='*60}")
                kill_process_by_name("wwm.exe", force=True)
                time.sleep(2)  # Chờ một chút sau khi kill
                
                print(f"\n✓ Hoàn tất vòng lặp {iteration}")
            else:
                print(f"\n✗ Vòng lặp {iteration} không thành công, bỏ qua account này")
            
            # Chờ một chút trước vòng lặp tiếp theo
            time.sleep(1)


def main():
    """Hàm main"""
    print("\n" + "=" * 60)
    print("AUTO RUN SCRIPT - Tự động chạy các step")
    print("=" * 60)
    
    # Cấu hình
    window_title = input("\nTên cửa sổ cần focus (Enter để bỏ qua): ").strip() or None
    threshold_input = input("Threshold (0.0-1.0, mặc định 0.8): ").strip()
    threshold = float(threshold_input) if threshold_input else 0.8
    
    max_retries_input = input("Số lần retry tối đa cho mỗi step (0 = vô hạn, mặc định 10): ").strip()
    max_retries = int(max_retries_input) if max_retries_input else 10
    
    retry_delay_input = input("Thời gian chờ giữa các lần retry (giây, mặc định 2.0): ").strip()
    retry_delay = float(retry_delay_input) if retry_delay_input else 2.0
    
    num_iterations_input = input("Số vòng lặp (0 = vô hạn cho đến khi hết account, mặc định 1): ").strip()
    num_iterations = int(num_iterations_input) if num_iterations_input else 1
    
    # Tạo runner
    runner = AutoRunner(
        window_title=window_title,
        threshold=threshold,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    # Hiển thị thông tin
    print(f"\n{'='*60}")
    print("CẤU HÌNH")
    print(f"{'='*60}")
    print(f"Window: {window_title or 'Không có'}")
    print(f"Threshold: {threshold}")
    print(f"Max retries: {max_retries if max_retries > 0 else 'Vô hạn'}")
    print(f"Retry delay: {retry_delay}s")
    print(f"Số vòng lặp: {num_iterations if num_iterations > 0 else 'Vô hạn'}")
    print(f"Số step: {len(runner.steps)}")
    print(f"{'='*60}")
    
    confirm = input("\nBắt đầu chạy? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Đã hủy")
        return
    
    # Chạy vòng lặp
    runner.run_loop(num_iterations)


if __name__ == "__main__":
    main()

