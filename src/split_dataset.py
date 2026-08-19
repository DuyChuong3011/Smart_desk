import os
import shutil
import random

def create_dirs(base_path):
    dirs = [
        os.path.join(base_path, 'train', 'images'),
        os.path.join(base_path, 'train', 'labels'),
        os.path.join(base_path, 'val', 'images'),
        os.path.join(base_path, 'val', 'labels')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs

def main():
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset')
    source_dir = os.path.join(dataset_path, 'images') # Nơi chứa cả ảnh và txt
    
    if not os.path.exists(source_dir):
        print(f"Không tìm thấy thư mục {source_dir}. Hãy thu thập dữ liệu trước!")
        return

    # Lấy danh sách tất cả file ảnh
    all_files = os.listdir(source_dir)
    image_files = [f for f in all_files if f.endswith('.jpg') or f.endswith('.png')]
    
    if not image_files:
        print("Không có ảnh nào trong thư mục!")
        return

    # Lọc ra các ảnh ĐÃ CÓ NHÃN (.txt)
    valid_pairs = []
    for img in image_files:
        base_name = os.path.splitext(img)[0]
        txt_file = base_name + '.txt'
        
        # Bắt buộc phải có file txt đi kèm mới đem đi train
        if os.path.exists(os.path.join(source_dir, txt_file)):
            valid_pairs.append((img, txt_file))
            
    if not valid_pairs:
        print("Không tìm thấy file nhãn (.txt) nào. Hãy chắc chắn bạn đã gán nhãn trên MakeSense.ai và bỏ file .txt vào chung thư mục ảnh!")
        return

    print(f"Đã tìm thấy {len(valid_pairs)} cặp (Ảnh + Nhãn). Đang xáo trộn...")
    
    # Tạo thư mục
    train_img_dir, train_lbl_dir, val_img_dir, val_lbl_dir = create_dirs(dataset_path)
    
    # Xáo trộn ngẫu nhiên
    random.seed(42)
    random.shuffle(valid_pairs)
    
    # Chia 80/20
    split_index = int(len(valid_pairs) * 0.8)
    train_set = valid_pairs[:split_index]
    val_set = valid_pairs[split_index:]
    
    print(f"Sẽ chuyển {len(train_set)} ảnh vào tập TRAIN.")
    print(f"Sẽ chuyển {len(val_set)} ảnh vào tập VAL.")
    
    # Chuyển file cho tập Train
    for img, txt in train_set:
        shutil.move(os.path.join(source_dir, img), os.path.join(train_img_dir, img))
        shutil.move(os.path.join(source_dir, txt), os.path.join(train_lbl_dir, txt))
        
    # Chuyển file cho tập Val
    for img, txt in val_set:
        shutil.move(os.path.join(source_dir, img), os.path.join(val_img_dir, img))
        shutil.move(os.path.join(source_dir, txt), os.path.join(val_lbl_dir, txt))
        
    print("========================================")
    print("✅ ĐÃ CHIA DATASET XONG!")
    print("========================================")

if __name__ == "__main__":
    main()
