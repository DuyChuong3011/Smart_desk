from ultralytics import YOLO
import os

def main():
    # Khởi tạo mô hình cơ sở (Sử dụng yolov8n.pt làm pretrained weights)
    print("Đang tải mô hình YOLOv8 Nano cơ sở...")
    model = YOLO("yolov8n.pt")
    
    # Lấy đường dẫn tuyệt đối tới file cấu hình dataset
    dataset_yaml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset', 'smartdesk_dataset.yaml')
    
    if not os.path.exists(dataset_yaml_path):
        print(f"LỖI: Không tìm thấy file cấu hình dataset tại {dataset_yaml_path}")
        return
        
    print("========================================")
    print("🚀 BẮT ĐẦU HUẤN LUYỆN (TRAINING)")
    print("========================================")
    
    # Bắt đầu huấn luyện
    # epochs=50: Số vòng lặp huấn luyện toàn bộ dataset. (Có thể tăng lên 100 nếu ảnh nhiều và cần độ chính xác cao)
    # imgsz=320: Kích thước ảnh đầu vào. Khớp với kích thước thực tế hệ thống đang chạy.
    # batch=16: Số lượng ảnh đưa vào RAM mỗi lần (Giảm xuống 8 nếu bị lỗi Out of Memory).
    results = model.train(
        data=dataset_yaml_path,
        epochs=50,
        imgsz=320,
        batch=16,
        name='smartdesk_custom',
        device='cpu',
        # --- DATA AUGMENTATION MẠNH MẼ CHO DATASET NHỎ ---
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, # Thay đổi màu sắc/độ sáng ngẫu nhiên
        degrees=15.0,     # Xoay ảnh ngẫu nhiên tối đa 15 độ
        translate=0.1,    # Dịch chuyển ảnh 10%
        scale=0.5,        # Phóng to/thu nhỏ 50%
        shear=0.0,        # Độ biến dạng
        perspective=0.0,  # Phối cảnh
        flipud=0.5,       # Tỷ lệ 50% sẽ lật ngược ảnh (hữu ích cho mặt bàn)
        fliplr=0.5,       # Tỷ lệ 50% sẽ lật ngang ảnh
        mosaic=1.0,       # Bật tính năng cắt ghép 4 ảnh thành 1
        mixup=0.2,        # Trộn 2 ảnh đè lên nhau (giúp chống nhiễu)
    )
    
    print("\n✅ HUẤN LUYỆN HOÀN TẤT!")
    print(f"Mô hình tốt nhất (best.pt) đã được lưu tại: runs/detect/smartdesk_custom/weights/best.pt")
    print("Hãy vào config.yaml và đổi dòng 'model_path: yolov8n.pt' thành đường dẫn tới best.pt!")

if __name__ == "__main__":
    main()
