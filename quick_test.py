"""
Quick Test Script
Script test nhanh 2 chức năng chính với template entergame.png
"""

from image_detector import ImageDetector
from screen_automation import ScreenAutomation
import time

def test_detect():
    """Test chức năng 1: Phát hiện vị trí"""
    print("=" * 60)
    print("TEST 1: Phát hiện vị trí và tọa độ ảnh mẫu")
    print("=" * 60)
    
    detector = ImageDetector(threshold=0.8)
    template_path = "templates/entergame.png"
    
    print(f"\nĐang tìm kiếm: {template_path}")
    result = detector.find_template(template_path)
    
    if result:
        x, y, confidence = result
        print(f"\n✓ THÀNH CÔNG!")
        print(f"  Tọa độ X: {x}")
        print(f"  Tọa độ Y: {y}")
        print(f"  Confidence: {confidence:.2%}")
        return (x, y, confidence)
    else:
        print("\n✗ KHÔNG TÌM THẤY")
        print("  - Kiểm tra file template có tồn tại không")
        print("  - Đảm bảo ảnh mẫu đang hiển thị trên màn hình")
        print("  - Thử giảm threshold xuống 0.7 hoặc 0.6")
        return None


def test_click(window_title=None):
    """Test chức năng 2: Click vào vị trí đã phát hiện"""
    print("\n" + "=" * 60)
    print("TEST 2: Click vào tọa độ đã phát hiện")
    print("=" * 60)
    
    automation = ScreenAutomation(detection_threshold=0.8)
    template_path = "templates/entergame.png"
    
    print(f"\nĐang tìm và click vào: {template_path}")
    if window_title:
        print(f"Window: {window_title} (sẽ focus trước khi click)")
    print("(Bạn có 3 giây để chuẩn bị...)")
    time.sleep(3)
    
    success = automation.click_at_image(template_path, window_title=window_title)
    
    if success:
        print("\n✓ THÀNH CÔNG! Đã click vào vị trí tìm thấy")
        return True
    else:
        print("\n✗ KHÔNG THÀNH CÔNG")
        print("  - Không tìm thấy ảnh mẫu để click")
        print("  - Kiểm tra lại template và màn hình")
        if window_title:
            print(f"  - Kiểm tra cửa sổ '{window_title}' có đang mở không")
        return False


def test_both(window_title=None):
    """Test cả 2 chức năng: Phát hiện rồi click"""
    print("\n" + "=" * 60)
    print("TEST 3: Phát hiện và Click (kết hợp)")
    print("=" * 60)
    
    if window_title:
        print(f"Window: {window_title} (sẽ focus trước khi click)")
    
    # Bước 1: Phát hiện
    result = test_detect()
    
    if result:
        x, y, confidence = result
        print(f"\n→ Đã phát hiện tại ({x}, {y})")
        
        # Bước 2: Click
        print("\n(Bạn có 3 giây trước khi click...)")
        time.sleep(3)
        
        automation = ScreenAutomation(detection_threshold=0.8)
        success = automation.click_at_image(
            "templates/entergame.png",
            window_title=window_title
        )
        
        if success:
            print(f"\n✓ HOÀN TẤT! Đã click vào ({x}, {y})")
            if window_title:
                print(f"   (Đã focus cửa sổ: {window_title})")
            return True
        else:
            print("\n✗ Phát hiện được nhưng không click được")
            if window_title:
                print(f"   - Kiểm tra cửa sổ '{window_title}' có đang mở không")
            return False
    else:
        print("\n✗ Không thể test click vì không tìm thấy ảnh mẫu")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        # Lấy window_title từ tham số thứ 2 (nếu có)
        window_title = sys.argv[2] if len(sys.argv) > 2 else None
        
        if test_name == "detect":
            test_detect()
        elif test_name == "click":
            test_click(window_title)
        elif test_name == "both":
            test_both(window_title)
        else:
            print("Các test: detect, click, both")
            print("\nCách sử dụng:")
            print("  python quick_test.py both")
            print("  python quick_test.py both \"launcher.exe Properties\"")
    else:
        print("\n" + "=" * 60)
        print("QUICK TEST - 2 Chức năng chính")
        print("=" * 60)
        print("\n1. Test phát hiện vị trí")
        print("2. Test click tự động")
        print("3. Test cả 2 (phát hiện + click)")
        print("0. Thoát")
        
        choice = input("\nChọn test (0-3): ").strip()
        
        window_title = None
        if choice in ["2", "3"]:
            window_title = input("Tên cửa sổ cần focus (Enter để bỏ qua): ").strip()
            if not window_title:
                window_title = None
        
        if choice == "1":
            test_detect()
        elif choice == "2":
            test_click(window_title)
        elif choice == "3":
            test_both(window_title)
        elif choice == "0":
            print("Tạm biệt!")
        else:
            print("Lựa chọn không hợp lệ!")

