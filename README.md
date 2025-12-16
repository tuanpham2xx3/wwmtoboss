# Python Screen Automation Tool

Tool Python để tự động hóa các tác vụ trên màn hình: phát hiện ảnh mẫu, click, paste dữ liệu, và chụp khu vực màn hình.

## Tính năng

- **Phát hiện ảnh mẫu**: Sử dụng template matching với OpenCV để tìm ảnh trên màn hình
- **Click tự động**: Tự động click vào vị trí tìm thấy
- **Paste dữ liệu**: Tự động paste text vào vị trí hiện tại
- **Chụp màn hình**: Chụp toàn màn hình hoặc khu vực cụ thể và lưu ảnh
- **Đợi ảnh xuất hiện**: Đợi cho đến khi ảnh mẫu xuất hiện trên màn hình

## Yêu cầu

- Python 3.7 trở lên
- Windows, macOS, hoặc Linux

## Cài đặt

1. Clone hoặc tải project về máy

2. Cài đặt các dependencies:

```bash
pip install -r requirements.txt
```

**Lưu ý**: Nếu gặp lỗi khi cài đặt `opencv-python`, bạn có thể thử:
```bash
pip install opencv-python-headless
```

## Cấu trúc dự án

```
MAKE ID/
├── requirements.txt          # Dependencies
├── README.md                 # File này
├── main.py                   # Entry point với demo
├── screen_automation.py      # Core automation class
├── image_detector.py         # Template matching logic
├── screen_capture.py         # Screen capture utilities
├── templates/                # Thư mục chứa ảnh mẫu
│   └── sample_template.png
└── screenshots/              # Thư mục lưu ảnh chụp
```

## Sử dụng

### Chạy Demo

Chạy menu tương tác:
```bash
python main.py
```

Hoặc chạy demo cụ thể:
```bash
python main.py detect      # Demo phát hiện ảnh
python main.py capture     # Demo chụp màn hình
python main.py click       # Demo click tự động
python main.py paste       # Demo paste dữ liệu
python main.py wait        # Demo đợi ảnh xuất hiện
python main.py workflow    # Demo workflow đầy đủ
```

### Sử dụng trong code

#### 1. Phát hiện ảnh mẫu

```python
from image_detector import ImageDetector

detector = ImageDetector(threshold=0.8)
result = detector.find_template("templates/my_template.png")

if result:
    x, y, confidence = result
    print(f"Tìm thấy tại ({x}, {y}) với confidence: {confidence}")
```

#### 2. Chụp màn hình

```python
from screen_capture import ScreenCapture

capture = ScreenCapture()

# Chụp toàn màn hình
screenshot_path = capture.capture_and_save()

# Chụp khu vực cụ thể
region_path = capture.capture_and_save(region=(0, 0, 800, 600))
```

#### 3. Tự động hóa (Click + Paste)

```python
from screen_automation import ScreenAutomation

automation = ScreenAutomation()

# Click vào ảnh mẫu
automation.click_at_image("templates/button.png")

# Click và paste dữ liệu
automation.click_and_paste("templates/input_field.png", "Hello World!")

# Đợi ảnh xuất hiện rồi click
result = automation.wait_for_image("templates/loading.png", timeout=10.0)
if result:
    automation.click_at_image("templates/button.png")
```

#### 4. Workflow đầy đủ

```python
from screen_automation import ScreenAutomation

automation = ScreenAutomation()

# 1. Tìm và click vào nút
automation.click_at_image("templates/submit_button.png")

# 2. Đợi form xuất hiện
automation.wait_for_image("templates/form.png", timeout=5.0)

# 3. Click vào ô input và paste dữ liệu
automation.click_and_paste("templates/name_input.png", "Nguyễn Văn A", clear_first=True)

# 4. Chụp màn hình để lưu lại
automation.capture.capture_and_save()
```

## Tạo ảnh mẫu (Template)

1. Chụp màn hình khu vực bạn muốn tìm (ví dụ: một nút bấm)
2. Cắt ảnh để chỉ giữ lại phần cần thiết (không cần quá lớn, chỉ cần đủ để nhận diện)
3. Lưu vào thư mục `templates/` với tên dễ nhớ (ví dụ: `submit_button.png`)

**Lưu ý**:
- Ảnh mẫu nên có độ phân giải phù hợp (không quá nhỏ, không quá lớn)
- Nên chụp ảnh mẫu ở cùng điều kiện ánh sáng/màu sắc với lúc sử dụng
- Template matching nhạy cảm với màu sắc và kích thước, nếu màn hình có scale khác nhau có thể cần điều chỉnh

## Cấu hình

### Điều chỉnh threshold

Threshold cao hơn = chính xác hơn nhưng khó tìm thấy hơn:

```python
automation = ScreenAutomation(detection_threshold=0.9)  # Rất chính xác
automation = ScreenAutomation(detection_threshold=0.7)  # Dễ tìm thấy hơn
```

### Điều chỉnh tốc độ

```python
automation.set_click_delay(1.0)  # Chờ 1 giây sau mỗi lần click
```

## Troubleshooting

### Không tìm thấy template

1. Kiểm tra đường dẫn đến file template có đúng không
2. Giảm threshold xuống (ví dụ: 0.7 hoặc 0.6)
3. Đảm bảo template hiển thị trên màn hình khi chạy
4. Kiểm tra kích thước màn hình/scale có thay đổi không

### Lỗi khi cài đặt OpenCV

Thử cài đặt phiên bản headless:
```bash
pip install opencv-python-headless
```

### PyAutoGUI failsafe

Nếu bạn di chuột vào góc trên bên trái màn hình, PyAutoGUI sẽ dừng lại để tránh lỗi. Đây là tính năng bảo vệ mặc định.

## API Reference

### ImageDetector

- `find_template(template_path, region=None)`: Tìm ảnh mẫu, trả về (x, y, confidence) hoặc None
- `find_all_templates(template_path, region=None)`: Tìm tất cả các vị trí khớp
- `set_threshold(threshold)`: Thay đổi threshold

### ScreenCapture

- `capture_full_screen()`: Chụp toàn màn hình
- `capture_region(x, y, width, height)`: Chụp khu vực cụ thể
- `capture_and_save(region=None, output_path=None)`: Chụp và lưu ngay

### ScreenAutomation

- `click_at_image(template_path, region=None, button='left', clicks=1)`: Click vào ảnh mẫu
- `paste_data(text, clear_first=False)`: Paste dữ liệu
- `click_and_paste(template_path, text, region=None, clear_first=False)`: Click và paste
- `wait_for_image(template_path, timeout=10.0, region=None)`: Đợi ảnh xuất hiện
- `double_click_at_image(template_path, region=None)`: Double-click
- `right_click_at_image(template_path, region=None)`: Right-click

## License

MIT License

## Tác giả

Tool được phát triển để tự động hóa các tác vụ lặp đi lặp lại trên màn hình.

