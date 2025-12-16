"""
Screen Automation Module
Tích hợp các chức năng: phát hiện ảnh, click, paste dữ liệu.
"""

import pyautogui
import time
import sys
from typing import Optional, Tuple
import logging
from image_detector import ImageDetector

# Thử import win32api cho Windows
try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenAutomation:
    """Class chính để tự động hóa các tác vụ trên màn hình."""
    
    def __init__(self, detection_threshold: float = 0.8, click_delay: float = 0.5):
        """
        Khởi tạo ScreenAutomation.
        
        Args:
            detection_threshold: Ngưỡng confidence cho template matching (0.0 - 1.0)
            click_delay: Thời gian chờ sau mỗi lần click (giây)
        """
        self.detector = ImageDetector(threshold=detection_threshold)
        self.click_delay = click_delay
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Pause ngắn giữa các action
    
    def click_at_image(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None, 
                      button: str = 'left', clicks: int = 1, interval: float = 0.0,
                      window_title: Optional[str] = None) -> bool:
        """
        Tìm ảnh mẫu trên màn hình và click vào vị trí đó.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
            button: 'left', 'right', hoặc 'middle'
            clicks: Số lần click
            interval: Khoảng thời gian giữa các lần click (giây)
            window_title: Tiêu đề cửa sổ cần focus trước khi click (cho game)
        
        Returns:
            True nếu tìm thấy và click thành công, False nếu không tìm thấy.
        """
        try:
            result = self.detector.find_template(template_path, region)
            
            if result:
                x, y, confidence = result
                logger.info(f"Click vào vị trí ({x}, {y}) với confidence: {confidence:.2f}")
                
                # Focus cửa sổ nếu có window_title (quan trọng cho game)
                if window_title and sys.platform == 'win32' and WIN32_AVAILABLE:
                    try:
                        hwnd = win32gui.FindWindow(None, window_title)
                        if hwnd == 0:
                            # Thử tìm theo partial match
                            def callback(hwnd, windows):
                                if win32gui.IsWindowVisible(hwnd):
                                    title = win32gui.GetWindowText(hwnd)
                                    if window_title.lower() in title.lower():
                                        windows.append(hwnd)
                                return True
                            windows = []
                            win32gui.EnumWindows(callback, windows)
                            if windows:
                                hwnd = windows[0]
                        
                        if hwnd != 0:
                            # Focus cửa sổ
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(hwnd)
                            win32gui.BringWindowToTop(hwnd)
                            time.sleep(0.2)  # Chờ cửa sổ focus
                            logger.info(f"Đã focus cửa sổ: {window_title}")
                    except Exception as e:
                        logger.warning(f"Không thể focus cửa sổ {window_title}: {e}")
                
                # Sử dụng win32api trên Windows nếu có (ổn định hơn)
                if sys.platform == 'win32' and WIN32_AVAILABLE:
                    try:
                        # Nếu có window_title, thử dùng PostMessage (mạnh nhất cho game)
                        if window_title:
                            hwnd = win32gui.FindWindow(None, window_title)
                            if hwnd == 0:
                                def callback(hwnd, windows):
                                    if win32gui.IsWindowVisible(hwnd):
                                        title = win32gui.GetWindowText(hwnd)
                                        if window_title.lower() in title.lower():
                                            windows.append(hwnd)
                                    return True
                                windows = []
                                win32gui.EnumWindows(callback, windows)
                                if windows:
                                    hwnd = windows[0]
                            
                            if hwnd != 0:
                                try:
                                    # Lấy vị trí cửa sổ
                                    rect = win32gui.GetWindowRect(hwnd)
                                    left, top, right, bottom = rect
                                    
                                    # Chuyển đổi tọa độ màn hình sang tọa độ cửa sổ
                                    rel_x = x - left
                                    rel_y = y - top
                                    
                                    # Tạo lparam
                                    lparam = win32api.MAKELONG(rel_x, rel_y)
                                    
                                    # Click bằng PostMessage (trực tiếp vào cửa sổ)
                                    for i in range(clicks):
                                        if button == 'left':
                                            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
                                            time.sleep(0.05)
                                            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
                                        elif button == 'right':
                                            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
                                            time.sleep(0.05)
                                            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
                                        
                                        if interval > 0 and i < clicks - 1:
                                            time.sleep(interval)
                                    
                                    time.sleep(self.click_delay)
                                    logger.info("Đã click bằng PostMessage (trực tiếp vào cửa sổ)")
                                    return True
                                except Exception as e:
                                    logger.warning(f"PostMessage không hoạt động, thử SendInput: {e}")
                        
                        # Thử SendInput (mạnh hơn mouse_event)
                        try:
                            import ctypes
                            from ctypes import wintypes
                            
                            # Cấu trúc cho SendInput
                            class MOUSEINPUT(ctypes.Structure):
                                _fields_ = [
                                    ("dx", wintypes.LONG),
                                    ("dy", wintypes.LONG),
                                    ("mouseData", wintypes.DWORD),
                                    ("dwFlags", wintypes.DWORD),
                                    ("time", wintypes.DWORD),
                                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
                                ]
                            
                            class INPUT(ctypes.Structure):
                                class _INPUT(ctypes.Union):
                                    _fields_ = [("mi", MOUSEINPUT)]
                                _anonymous_ = ("_input",)
                                _fields_ = [
                                    ("type", wintypes.DWORD),
                                    ("_input", _INPUT)
                                ]
                            
                            user32 = ctypes.windll.user32
                            screen_width = win32api.GetSystemMetrics(0)
                            screen_height = win32api.GetSystemMetrics(1)
                            
                            # Chuyển đổi tọa độ
                            abs_x = int((x * 65535) / screen_width)
                            abs_y = int((y * 65535) / screen_height)
                            
                            MOUSEEVENTF_ABSOLUTE = 0x8000
                            MOUSEEVENTF_MOVE = 0x0001
                            MOUSEEVENTF_LEFTDOWN = 0x0002
                            MOUSEEVENTF_LEFTUP = 0x0004
                            MOUSEEVENTF_RIGHTDOWN = 0x0008
                            MOUSEEVENTF_RIGHTUP = 0x0010
                            
                            # Di chuyển chuột
                            move_input = INPUT()
                            move_input.type = 0  # INPUT_MOUSE
                            move_input.mi.dx = abs_x
                            move_input.mi.dy = abs_y
                            move_input.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
                            user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
                            time.sleep(0.05)
                            
                            # Click
                            for i in range(clicks):
                                if button == 'left':
                                    down_flag = MOUSEEVENTF_LEFTDOWN
                                    up_flag = MOUSEEVENTF_LEFTUP
                                elif button == 'right':
                                    down_flag = MOUSEEVENTF_RIGHTDOWN
                                    up_flag = MOUSEEVENTF_RIGHTUP
                                else:
                                    down_flag = MOUSEEVENTF_LEFTDOWN
                                    up_flag = MOUSEEVENTF_LEFTUP
                                
                                # Mouse down
                                down_input = INPUT()
                                down_input.type = 0
                                down_input.mi.dx = abs_x
                                down_input.mi.dy = abs_y
                                down_input.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | down_flag
                                user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
                                time.sleep(0.05)
                                
                                # Mouse up
                                up_input = INPUT()
                                up_input.type = 0
                                up_input.mi.dx = abs_x
                                up_input.mi.dy = abs_y
                                up_input.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | up_flag
                                user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
                                
                                if interval > 0 and i < clicks - 1:
                                    time.sleep(interval)
                            
                            time.sleep(self.click_delay)
                            logger.info("Đã click bằng SendInput")
                            return True
                        except Exception as e:
                            logger.warning(f"SendInput không hoạt động, thử mouse_event: {e}")
                        
                        # Fallback: mouse_event (phương pháp cũ)
                        win32api.SetCursorPos((x, y))
                        time.sleep(0.05)
                        
                        if button == 'left':
                            down_code = win32con.MOUSEEVENTF_LEFTDOWN
                            up_code = win32con.MOUSEEVENTF_LEFTUP
                        elif button == 'right':
                            down_code = win32con.MOUSEEVENTF_RIGHTDOWN
                            up_code = win32con.MOUSEEVENTF_RIGHTUP
                        elif button == 'middle':
                            down_code = win32con.MOUSEEVENTF_MIDDLEDOWN
                            up_code = win32con.MOUSEEVENTF_MIDDLEUP
                        else:
                            down_code = win32con.MOUSEEVENTF_LEFTDOWN
                            up_code = win32con.MOUSEEVENTF_LEFTUP
                        
                        for i in range(clicks):
                            win32api.mouse_event(down_code, x, y, 0, 0)
                            time.sleep(0.05)
                            win32api.mouse_event(up_code, x, y, 0, 0)
                            if interval > 0 and i < clicks - 1:
                                time.sleep(interval)
                        
                        time.sleep(self.click_delay)
                        logger.info("Đã click bằng mouse_event")
                        return True
                    except Exception as e:
                        logger.warning(f"Lỗi khi dùng win32api, thử PyAutoGUI: {e}")
                        # Fallback về PyAutoGUI
                
                # Fallback: Sử dụng PyAutoGUI
                pyautogui.moveTo(x, y, duration=0.1)
                time.sleep(0.05)
                
                # Click bằng mouseDown/mouseUp
                for i in range(clicks):
                    pyautogui.mouseDown(button=button)
                    time.sleep(0.05)
                    pyautogui.mouseUp(button=button)
                    # Chờ interval giữa các lần click (nếu có nhiều clicks)
                    if interval > 0 and i < clicks - 1:
                        time.sleep(interval)
                
                time.sleep(self.click_delay)
                
                return True
            else:
                logger.warning(f"Không tìm thấy template: {template_path}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi click tại image: {str(e)}")
            return False
    
    def paste_data(self, text: str, clear_first: bool = False) -> bool:
        """
        Paste dữ liệu vào vị trí hiện tại của con trỏ.
        
        Args:
            text: Nội dung text cần paste
            clear_first: Nếu True, sẽ xóa nội dung hiện tại trước khi paste (Ctrl+A, Delete)
        
        Returns:
            True nếu paste thành công.
        """
        try:
            if clear_first:
                # Xóa nội dung hiện tại
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
                time.sleep(0.1)
            
            # Paste dữ liệu
            pyautogui.write(text, interval=0.01)
            logger.info(f"Đã paste dữ liệu: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi paste dữ liệu: {str(e)}")
            return False
    
    def paste_data_clipboard(self, text: str, clear_first: bool = False) -> bool:
        """
        Paste dữ liệu sử dụng clipboard (Ctrl+V).
        
        Args:
            text: Nội dung text cần paste
            clear_first: Nếu True, sẽ xóa nội dung hiện tại trước khi paste
        
        Returns:
            True nếu paste thành công.
        """
        try:
            import pyperclip
            
            if clear_first:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
                time.sleep(0.1)
            
            # Copy vào clipboard
            pyperclip.copy(text)
            time.sleep(0.1)
            
            # Paste
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            
            logger.info(f"Đã paste dữ liệu từ clipboard: {text[:50]}...")
            return True
            
        except ImportError:
            logger.warning("pyperclip không được cài đặt. Sử dụng phương thức write() thay thế.")
            return self.paste_data(text, clear_first)
        except Exception as e:
            logger.error(f"Lỗi khi paste dữ liệu từ clipboard: {str(e)}")
            return False
    
    def click_and_paste(self, template_path: str, text: str, 
                       region: Optional[Tuple[int, int, int, int]] = None,
                       clear_first: bool = False, use_clipboard: bool = False) -> bool:
        """
        Tìm ảnh mẫu, click vào đó, và paste dữ liệu.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            text: Nội dung text cần paste
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
            clear_first: Nếu True, sẽ xóa nội dung hiện tại trước khi paste
            use_clipboard: Nếu True, sử dụng clipboard để paste (nhanh hơn cho text dài)
        
        Returns:
            True nếu thực hiện thành công tất cả các bước.
        """
        try:
            # Tìm và click
            if not self.click_at_image(template_path, region):
                return False
            
            time.sleep(0.2)  # Chờ một chút sau khi click
            
            # Paste dữ liệu
            if use_clipboard:
                return self.paste_data_clipboard(text, clear_first)
            else:
                return self.paste_data(text, clear_first)
                
        except Exception as e:
            logger.error(f"Lỗi trong click_and_paste: {str(e)}")
            return False
    
    def wait_for_image(self, template_path: str, timeout: float = 10.0, 
                      check_interval: float = 0.5,
                      region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int, float]]:
        """
        Đợi cho đến khi ảnh mẫu xuất hiện trên màn hình.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            timeout: Thời gian tối đa để đợi (giây)
            check_interval: Khoảng thời gian giữa các lần kiểm tra (giây)
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
        
        Returns:
            Tuple (x, y, confidence) nếu tìm thấy, None nếu timeout.
        """
        start_time = time.time()
        logger.info(f"Đang đợi template xuất hiện: {template_path} (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            result = self.detector.find_template(template_path, region)
            if result:
                x, y, confidence = result
                elapsed = time.time() - start_time
                logger.info(f"Tìm thấy template sau {elapsed:.2f}s tại ({x}, {y})")
                return result
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout: Không tìm thấy template sau {timeout}s")
        return None
    
    def double_click_at_image(self, template_path: str, 
                             region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Tìm ảnh mẫu và double-click vào vị trí đó.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
        
        Returns:
            True nếu tìm thấy và double-click thành công.
        """
        return self.click_at_image(template_path, region, clicks=2, interval=0.1)
    
    def right_click_at_image(self, template_path: str, 
                            region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Tìm ảnh mẫu và right-click vào vị trí đó.
        
        Args:
            template_path: Đường dẫn đến file ảnh mẫu
            region: (x, y, width, height) - Khu vực tìm kiếm. None = toàn màn hình.
        
        Returns:
            True nếu tìm thấy và right-click thành công.
        """
        return self.click_at_image(template_path, region, button='right')
    
    def set_detection_threshold(self, threshold: float):
        """Thay đổi threshold cho template matching."""
        self.detector.set_threshold(threshold)
    
    def set_click_delay(self, delay: float):
        """Thay đổi thời gian chờ sau mỗi lần click."""
        self.click_delay = delay
        logger.info(f"Đã đặt click delay: {delay}s")
    
    def press_key(self, key: str, times: int = 1, interval: float = 0.0, window_title: Optional[str] = None) -> bool:
        """
        Nhấn phím một hoặc nhiều lần.
        
        Args:
            key: Tên phím cần nhấn (ví dụ: 'r', 'enter', 'space', 'ctrl', etc.)
            times: Số lần nhấn phím
            interval: Khoảng thời gian giữa các lần nhấn (giây)
            window_title: Tiêu đề cửa sổ cần focus trước khi nhấn phím
        
        Returns:
            True nếu thành công
        """
        try:
            # Focus cửa sổ nếu có window_title
            if window_title and sys.platform == 'win32' and WIN32_AVAILABLE:
                try:
                    hwnd = win32gui.FindWindow(None, window_title)
                    if hwnd == 0:
                        def callback(hwnd, windows):
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                if window_title.lower() in title.lower():
                                    windows.append(hwnd)
                            return True
                        windows = []
                        win32gui.EnumWindows(callback, windows)
                        if windows:
                            hwnd = windows[0]
                    
                    if hwnd != 0:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.BringWindowToTop(hwnd)
                        time.sleep(0.2)
                        logger.info(f"Đã focus cửa sổ: {window_title}")
                except Exception as e:
                    logger.warning(f"Không thể focus cửa sổ {window_title}: {e}")
            
            # Nhấn phím
            for i in range(times):
                pyautogui.press(key)
                logger.info(f"Đã nhấn phím '{key}' (lần {i+1}/{times})")
                
                if interval > 0 and i < times - 1:
                    time.sleep(interval)
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi nhấn phím '{key}': {str(e)}")
            return False

