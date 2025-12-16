"""
Main Demo Script
Ví dụ sử dụng các module tự động hóa màn hình.
"""

import time
import sys
from screen_automation import ScreenAutomation
from image_detector import ImageDetector


def demo_image_detection():
    """Demo: Phát hiện ảnh mẫu trên màn hình."""
    print("\n=== Demo: Phát hiện ảnh mẫu ===")
    
    detector = ImageDetector(threshold=0.8)
    
    # Thay đổi đường dẫn này thành đường dẫn đến ảnh mẫu của bạn
    template_path = "templates/sample_template.png"
    
    print(f"Đang tìm kiếm template: {template_path}")
    result = detector.find_template(template_path)
    
    if result:
        x, y, confidence = result
        print(f"✓ Tìm thấy tại vị trí: ({x}, {y})")
        print(f"  Confidence: {confidence:.2%}")
    else:
        print("✗ Không tìm thấy template trên màn hình")
        print("  Hãy đảm bảo ảnh mẫu tồn tại và hiển thị trên màn hình")


def demo_click_automation():
    """Demo: Click vào ảnh mẫu."""
    print("\n=== Demo: Click tự động ===")
    
    automation = ScreenAutomation()
    
    # Thay đổi đường dẫn này thành đường dẫn đến ảnh mẫu của bạn
    template_path = "templates/sample_template.png"
    
    print(f"Đang tìm và click vào: {template_path}")
    print("(Bạn có 3 giây để chuẩn bị...)")
    time.sleep(3)
    
    success = automation.click_at_image(template_path)
    if success:
        print("✓ Đã click thành công!")
    else:
        print("✗ Không tìm thấy template để click")


def demo_paste_automation():
    """Demo: Click và paste dữ liệu."""
    print("\n=== Demo: Click và Paste ===")
    
    automation = ScreenAutomation()
    
    # Thay đổi đường dẫn này thành đường dẫn đến ảnh mẫu của bạn
    template_path = "templates/sample_template.png"
    text_to_paste = "Hello, World! Đây là dữ liệu tự động paste."
    
    print(f"Đang tìm template, click và paste text...")
    print(f"Text sẽ paste: {text_to_paste}")
    print("(Bạn có 3 giây để chuẩn bị - hãy mở một text editor...)")
    time.sleep(3)
    
    success = automation.click_and_paste(template_path, text_to_paste, clear_first=True)
    if success:
        print("✓ Đã click và paste thành công!")
    else:
        print("✗ Không thể thực hiện click và paste")


def demo_wait_for_image():
    """Demo: Đợi ảnh xuất hiện."""
    print("\n=== Demo: Đợi ảnh xuất hiện ===")
    
    automation = ScreenAutomation()
    
    # Thay đổi đường dẫn này thành đường dẫn đến ảnh mẫu của bạn
    template_path = "templates/sample_template.png"
    
    print(f"Đang đợi template xuất hiện: {template_path}")
    print("(Timeout: 10 giây)")
    
    result = automation.wait_for_image(template_path, timeout=10.0)
    if result:
        x, y, confidence = result
        print(f"✓ Template đã xuất hiện tại ({x}, {y}) với confidence: {confidence:.2%}")
    else:
        print("✗ Timeout: Template không xuất hiện trong 10 giây")


def demo_full_workflow():
    """Demo: Workflow đầy đủ - detect → click → paste → capture."""
    print("\n=== Demo: Workflow đầy đủ ===")
    
    automation = ScreenAutomation()
    
    # Thay đổi đường dẫn này thành đường dẫn đến ảnh mẫu của bạn
    template_path = "templates/sample_template.png"
    text_to_paste = "Automated data entry"
    
    print("Workflow: Detect → Click → Paste → Capture")
    print("(Bạn có 5 giây để chuẩn bị...)")
    time.sleep(5)
    
    # Bước 1: Detect
    print("\n1. Đang phát hiện template...")
    result = automation.detector.find_template(template_path)
    if not result:
        print("✗ Không tìm thấy template. Dừng workflow.")
        return
    
    x, y, confidence = result
    print(f"   ✓ Tìm thấy tại ({x}, {y}), confidence: {confidence:.2%}")
    
    # Bước 2: Click
    print("\n2. Đang click vào template...")
    if automation.click_at_image(template_path):
        print("   ✓ Đã click thành công")
    else:
        print("   ✗ Không thể click")
        return
    
    time.sleep(0.5)
    
    # Bước 3: Paste
    print("\n3. Đang paste dữ liệu...")
    if automation.paste_data(text_to_paste, clear_first=True):
        print(f"   ✓ Đã paste: {text_to_paste}")
    else:
        print("   ✗ Không thể paste")
        return
    
    print("\n✓ Workflow hoàn tất!")


def interactive_menu():
    """Menu tương tác để chọn demo."""
    print("\n" + "="*50)
    print("Python Screen Automation Tool - Demo Menu")
    print("="*50)
    print("1. Phát hiện ảnh mẫu trên màn hình")
    print("2. Click tự động vào ảnh mẫu")
    print("3. Click và paste dữ liệu")
    print("4. Đợi ảnh xuất hiện")
    print("5. Workflow đầy đủ (detect → click → paste)")
    print("0. Thoát")
    print("="*50)
    
    choice = input("\nChọn chức năng (0-5): ").strip()
    
    return choice


def main():
    """Hàm main."""
    if len(sys.argv) > 1:
        # Chạy demo cụ thể từ command line
        demo_name = sys.argv[1]
        demos = {
            "detect": demo_image_detection,
            "click": demo_click_automation,
            "paste": demo_paste_automation,
            "wait": demo_wait_for_image,
            "workflow": demo_full_workflow
        }
        
        if demo_name in demos:
            demos[demo_name]()
        else:
            print(f"Demo không tồn tại: {demo_name}")
            print("Các demo có sẵn: detect, click, paste, wait, workflow")
    else:
        # Chạy menu tương tác
        while True:
            choice = interactive_menu()
            
            if choice == "0":
                print("\nTạm biệt!")
                break
            elif choice == "1":
                demo_image_detection()
            elif choice == "2":
                demo_click_automation()
            elif choice == "3":
                demo_paste_automation()
            elif choice == "4":
                demo_wait_for_image()
            elif choice == "5":
                demo_full_workflow()
            else:
                print("Lựa chọn không hợp lệ!")
            
            input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()

