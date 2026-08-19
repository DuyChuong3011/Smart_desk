import cv2
import os
import yaml
from datetime import datetime

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    cam_index = config['camera'].get('index', 0)
    width = config['camera'].get('width', 1280)
    height = config['camera'].get('height', 720)
    
    # Tạo thư mục lưu ảnh
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset', 'images')
    os.makedirs(dataset_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    if not cap.isOpened():
        print(f"Không thể mở camera số {cam_index}!")
        return

    print("=========================================")
    print("TRÌNH THU THẬP DỮ LIỆU (DATA COLLECTOR)")
    print("=========================================")
    print("- Đặt AirPods hoặc các đồ vật lên bàn.")
    print("- Nhấn phím 'S' để lưu một bức ảnh.")
    print("- Hãy di chuyển/xoay đồ vật và nhấn 'S' liên tục.")
    print("- Nhấn phím 'Q' để thoát.")
    print(f"- Ảnh được lưu tại: {dataset_dir}")
    print("=========================================")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Lỗi khi đọc khung hình từ camera.")
            break
            
        # Hiển thị HUD hướng dẫn
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Da chup: {count} anh", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, "Nhan 'S' de chup | Nhan 'Q' de thoat", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Data Collector", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Lưu frame GỐC (không có chữ HUD)
            filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{count}.jpg"
            filepath = os.path.join(dataset_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f" Đã lưu: {filename}")
            count += 1
            
            # Hiệu ứng nháy màn hình (phản hồi thị giác)
            flash = display_frame.copy()
            flash[:] = (255, 255, 255)
            cv2.imshow("Data Collector", flash)
            cv2.waitKey(50)

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nThu thập hoàn tất! Tổng cộng {count} ảnh.")

if __name__ == "__main__":
    main()
