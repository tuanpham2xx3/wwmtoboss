"""
Image Detector Module
Sử dụng OpenCV để phát hiện ảnh mẫu trên màn hình bằng template matching.
"""

import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageDetector:
    """Class để phát hiện ảnh mẫu trên màn hình sử dụng template matching."""
    
    def __init__(self, threshold: float = 0.8):
        """
        Khởi tạo ImageDetector.
        
        Args:
            threshold: Ngưỡng confidence (0.0 - 1.0) để chấp nhận kết quả matching.
                      Giá trị cao hơn = chính xác hơn nhưng khó tìm thấy hơn.
        """
        self.threshold = threshold
        pyautogui.FAILSAFE = True  # Bật failsafe để dừng khi di chuột vào góc màn hình
    
    def find_template(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int, float]]:
        """
        Tìm ảnh mẫu trên màn hình hiện tại.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu (template)
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
        
        Returns:
            Tuple (x, y, confidence) nếu tìm thấy, None nếu không tìm thấy.
            x, y là tọa độ trung tâm của ảnh mẫu trên màn hình.
        """
        try:
            # Đọc template image
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"Không thể đọc file template: {template_path}")
                return None
            
            # Chụp màn hình
            if region:
                x, y, width, height = region
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()
            
            # Chuyển đổi sang numpy array và OpenCV format
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Kiểm tra confidence
            if max_val >= self.threshold:
                # Tính tọa độ trung tâm của template
                template_h, template_w = template.shape[:2]
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                
                # Điều chỉnh tọa độ nếu có region
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                logger.info(f"Tìm thấy template tại ({center_x}, {center_y}) với confidence: {max_val:.2f}")
                return (center_x, center_y, max_val)
            else:
                logger.debug(f"Không tìm thấy template. Confidence cao nhất: {max_val:.2f} < {self.threshold}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi tìm template: {str(e)}")
            return None
    
    def find_all_templates(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None) -> list:
        """
        Tìm tất cả các vị trí khớp với template trên màn hình.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
        
        Returns:
            List các tuple (x, y, confidence) của tất cả các vị trí tìm thấy.
        """
        try:
            # Đọc template image
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"Không thể đọc file template: {template_path}")
                return []
            
            # Chụp màn hình
            if region:
                x, y, width, height = region
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()
            
            # Chuyển đổi sang numpy array và OpenCV format
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Tìm tất cả các vị trí có confidence >= threshold
            locations = np.where(result >= self.threshold)
            matches = []
            
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch x and y coordinates
                confidence = result[pt[1], pt[0]]
                center_x = pt[0] + template_w // 2
                center_y = pt[1] + template_h // 2
                
                # Điều chỉnh tọa độ nếu có region
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                matches.append((center_x, center_y, float(confidence)))
            
            # Loại bỏ các match quá gần nhau (non-maximum suppression đơn giản)
            filtered_matches = self._filter_nearby_matches(matches, template_w, template_h)
            
            logger.info(f"Tìm thấy {len(filtered_matches)} vị trí khớp với template")
            return filtered_matches
                
        except Exception as e:
            logger.error(f"Lỗi khi tìm template: {str(e)}")
            return []
    
    def _filter_nearby_matches(self, matches: list, template_w: int, template_h: int, min_distance: int = 10) -> list:
        """
        Lọc bỏ các match quá gần nhau, giữ lại match có confidence cao nhất.
        
        Args:
            matches: List các tuple (x, y, confidence)
            template_w: Chiều rộng template
            template_h: Chiều cao template
            min_distance: Khoảng cách tối thiểu giữa các match (pixels)
        
        Returns:
            List các match đã được lọc.
        """
        if not matches:
            return []
        
        # Sắp xếp theo confidence giảm dần
        sorted_matches = sorted(matches, key=lambda x: x[2], reverse=True)
        filtered = []
        
        for match in sorted_matches:
            x, y, conf = match
            is_far_enough = True
            
            for existing in filtered:
                ex, ey, _ = existing
                distance = np.sqrt((x - ex)**2 + (y - ey)**2)
                if distance < min_distance:
                    is_far_enough = False
                    break
            
            if is_far_enough:
                filtered.append(match)
        
        return filtered
    
    def set_threshold(self, threshold: float):
        """Thay đổi threshold cho template matching."""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            logger.info(f"Đã đặt threshold mới: {threshold}")
        else:
            logger.warning(f"Threshold phải trong khoảng [0.0, 1.0]. Giữ nguyên: {self.threshold}")

