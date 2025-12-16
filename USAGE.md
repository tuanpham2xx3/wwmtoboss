# Hướng dẫn sử dụng - 2 Chức năng chính

## Chức năng 1: Phát hiện vị trí và tọa độ ảnh mẫu

Phát hiện ảnh mẫu trên màn hình và trả về tọa độ (x, y) cùng độ tin cậy (confidence).

### Sử dụng trong code:

```python
from image_detector import ImageDetector

detector = ImageDetector(threshold=0.8)
result = detector.find_template("templates/entergame.png")

if result:
    x, y, confidence = result
    print(f"Tọa độ: ({x}, {y}), Confidence: {confidence:.2%}")
else:
    print("Không tìm thấy")
```

### Sử dụng script đơn giản:

```bash
python simple_automation.py detect templates/entergame.png 0.8
```

Hoặc chạy menu tương tác:
```bash
python simple_automation.py
# Chọn option 1
```

## Chức năng 2: Click vào tọa độ đã phát hiện

Tự động phát hiện ảnh mẫu và click vào vị trí đó.

### Sử dụng trong code:

```python
from screen_automation import ScreenAutomation

automation = ScreenAutomation(detection_threshold=0.8)
success = automation.click_at_image("templates/entergame.png")

if success:
    print("Đã click thành công!")
```

### Sử dụng script đơn giản:

```bash
python simple_automation.py click templates/entergame.png 0.8
```

Hoặc chạy menu tương tác:
```bash
python simple_automation.py
# Chọn option 2
```

## Kết hợp cả 2 chức năng

Phát hiện vị trí trước, sau đó click:

```python
from simple_automation import detect_and_click

result = detect_and_click("templates/entergame.png", threshold=0.8)
if result:
    x, y, confidence = result
    print(f"Đã click tại ({x}, {y})")
```

Hoặc dùng script:
```bash
python simple_automation.py both templates/entergame.png 0.8
```

## Ví dụ thực tế

### Ví dụ 1: Chỉ phát hiện vị trí

```python
from image_detector import ImageDetector

detector = ImageDetector(threshold=0.8)
result = detector.find_template("templates/entergame.png")

if result:
    x, y, confidence = result
    print(f"Tìm thấy nút 'Enter Game' tại ({x}, {y})")
    # Có thể lưu tọa độ này để dùng sau
    saved_position = (x, y)
```

### Ví dụ 2: Phát hiện và click ngay

```python
from screen_automation import ScreenAutomation

automation = ScreenAutomation(detection_threshold=0.8)

# Tìm và click vào nút "Enter Game"
if automation.click_at_image("templates/entergame.png"):
    print("Đã click vào nút Enter Game!")
```

### Ví dụ 3: Click nhiều lần hoặc right-click

```python
from screen_automation import ScreenAutomation

automation = ScreenAutomation()

# Double-click
automation.click_at_image("templates/entergame.png", clicks=2)

# Right-click
automation.click_at_image("templates/entergame.png", button='right')
```

## Điều chỉnh Threshold

Threshold quyết định độ chính xác khi tìm ảnh:
- **0.9-1.0**: Rất chính xác, chỉ khớp khi ảnh giống hệt
- **0.8**: Cân bằng tốt (khuyến nghị)
- **0.6-0.7**: Dễ tìm thấy hơn, nhưng có thể nhầm lẫn
- **< 0.6**: Rất dễ tìm thấy, nhưng dễ bị false positive

```python
# Tăng độ chính xác
detector = ImageDetector(threshold=0.9)

# Giảm để dễ tìm thấy hơn
detector = ImageDetector(threshold=0.7)
```

## Tìm kiếm trong khu vực cụ thể

Nếu bạn biết ảnh chỉ xuất hiện ở một khu vực nhất định, có thể giới hạn vùng tìm kiếm:

```python
from image_detector import ImageDetector

detector = ImageDetector()
# Tìm trong khu vực (x=100, y=100, width=800, height=600)
result = detector.find_template(
    "templates/entergame.png", 
    region=(100, 100, 800, 600)
)
```

## Lưu ý

1. **Ảnh mẫu**: Đặt file ảnh mẫu vào thư mục `templates/`
2. **Độ phân giải**: Ảnh mẫu nên có độ phân giải phù hợp (không quá nhỏ)
3. **Màu sắc**: Template matching nhạy cảm với màu sắc, nên chụp ảnh mẫu ở điều kiện tương tự
4. **Failsafe**: Di chuột vào góc trên bên trái màn hình để dừng PyAutoGUI nếu cần

