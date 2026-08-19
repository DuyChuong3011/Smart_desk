from ultralytics import YOLO
import os

def main():
    print("========================================")
    print("🔄 TRÌNH CHUYỂN ĐỔI MÔ HÌNH (EXPORT TO ONNX)")
    print("========================================")
    
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'best.pt')
    
    if not os.path.exists(model_path):
        print(f"LỖI: Không tìm thấy file {model_path}")
        print("Hãy chắc chắn bạn đã train xong và copy file best.pt vào thư mục models/ nhé.")
        return

    print(f"Đang tải mô hình Pytorch từ: {model_path}...")
    model = YOLO(model_path)
    
    print("\nĐang tiến hành nén và chuyển đổi sang định dạng ONNX...")
    print("Quá trình này có thể tốn vài chục giây, vui lòng chờ...")
    
    # Export model sang định dạng ONNX
    # imgsz=320: Ép cứng kích thước đầu vào để tối ưu tốc độ tối đa
    # dynamic=False: Tắt tính năng kích thước động (Giúp model chạy nhanh hơn nữa)
    exported_path = model.export(format="onnx", imgsz=320, dynamic=False)
    
    print("\n✅ CHUYỂN ĐỔI THÀNH CÔNG!")
    print(f"File siêu nhẹ (.onnx) đã được lưu tại: {exported_path}")
    print("Bây giờ bạn hãy vào config.yaml và đổi model_path thành 'models/best.onnx' nhé!")

if __name__ == "__main__":
    main()
