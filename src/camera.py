import cv2
import logging
import threading
import time

class CameraManager:
    def __init__(self, config):
        self.config = config['camera']
        self.cap = None
        self.ret = False
        self.latest_frame = None
        self.running = False
        self.thread = None
        self.new_frame_event = threading.Event()

    def open(self):
        self.cap = cv2.VideoCapture(self.config['index'])
        if not self.cap.isOpened():
            logging.error(f"Cannot open camera with index {self.config['index']}")
            return False
        
        # Thiết lập các thông số camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['height'])
        self.cap.set(cv2.CAP_PROP_FPS, self.config['fps'])
        
        # Khởi chạy luồng chạy nền để đọc frame liên tục
        self.running = True
        self.ret, self.latest_frame = self.cap.read()
        self.new_frame_event.set()
        
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        
        logging.info("Camera opened successfully with background thread.")
        return True

    def _update(self):
        # Luôn đọc frame mới nhất để tránh tràn buffer gây lag
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.ret = ret
                    self.latest_frame = frame
                    self.new_frame_event.set()
            else:
                time.sleep(0.01)

    def read_frame(self):
        # Đợi cho đến khi có frame mới (tránh CPU spinning vòng lặp vô hạn)
        self.new_frame_event.wait(timeout=1.0)
        self.new_frame_event.clear()
        
        # Trả về bản sao của frame mới nhất
        if not self.ret or self.latest_frame is None:
            return False, None
        return self.ret, self.latest_frame.copy()

    def release(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logging.info("Camera released.")
