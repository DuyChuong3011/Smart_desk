# 🖥️ Smart Desk: Hệ thống Giám sát Bàn làm việc bằng AI

> Một hệ thống Computer Vision & IoT thông minh sử dụng camera để nhận diện, theo dõi các đồ vật cá nhân trên bàn làm việc và cảnh báo theo thời gian thực nếu có sự di chuyển bất thường.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)
![ONNX](https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=mqtt&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📌 Tổng quan (Overview)

**Smart Desk** là một giải pháp AI và IoT khép kín được thiết kế để theo dõi các vật dụng có giá trị (như AirPods, điện thoại, ví tiền, bàn phím) trên bàn làm việc vật lý của bạn. Sử dụng một webcam thông thường, hệ thống liên tục phân tích không gian làm việc, nhận diện các đồ vật mục tiêu và quản lý trạng thái của chúng thông qua thuật toán chống nhiễu (debouncing) tiên tiến.

Khi một đồ vật bị lấy đi hoặc di chuyển, hệ thống lập tức ghi nhận sự kiện, chụp lại một bức ảnh làm bằng chứng, đồng thời phát tín hiệu cảnh báo qua giao thức MQTT đến một module phần cứng ESP32 để kích hoạt đèn báo và còi hú. Một bảng điều khiển (Dashboard) trên nền web được tích hợp sẵn giúp bạn dễ dàng giám sát lịch sử của bàn làm việc từ xa.

Hệ thống cũng đi kèm với một bộ công cụ **Học liên tục (Continuous Learning)**, cho phép bạn tự thu thập dữ liệu, tự huấn luyện mô hình YOLO của riêng mình để nhận diện các đồ vật cá nhân, và ép nén sang định dạng siêu nhẹ ONNX.

---

## ✨ Tính năng nổi bật (Features)

- 🎥 **Nhận diện theo thời gian thực** — Phân tích khung hình từ camera để phát hiện các đồ vật mục tiêu nằm trong Khu vực làm việc (Desk ROI).
- 🧠 **Bộ công cụ Huấn luyện AI tùy chỉnh** — Tích hợp sẵn các script tự động thu thập ảnh, chia tập dữ liệu (Train/Val), huấn luyện YOLOv8 và xuất sang định dạng ONNX để chạy tối ưu trên CPU.
- 🛡️ **Quản lý Trạng thái Thông minh** — Sử dụng thuật toán debouncing để ngăn chặn cảnh báo giả/chớp nháy khi đồ vật tạm thời bị che khuất.
- 📡 **Tích hợp IoT (MQTT)** — Phát sóng các sự kiện theo thời gian thực (`XUẤT HIỆN`, `BIẾN MẤT`, `DI CHUYỂN`) đến broker Mosquitto nội bộ.
- 🚨 **Cảnh báo Phần cứng** — Một vi điều khiển ESP32 sẽ lắng nghe broker và kích hoạt đèn LED RGB (NeoPixel) cùng còi báo động dựa trên loại sự kiện.
- 💾 **Lưu trữ Bằng chứng** — Tự động chụp lại ảnh độ phân giải cao và ghi nhận sự kiện vào cơ sở dữ liệu SQLite mỗi khi có sự tương tác với đồ vật.
- 🌐 **Web Dashboard** — Bảng điều khiển giao diện đẹp mắt viết bằng Flask giúp theo dõi các sự kiện gần đây và xem ảnh bằng chứng từ xa.

---

## 🏗️ Kiến trúc Hệ thống (System Architecture)

```mermaid
flowchart TD
    subgraph Thiết bị Xử lý (PC/Laptop)
        Cam[Webcam] --> OD[YOLOv8 ONNX Detector]
        OD --> ROI[Lọc vùng Desk ROI]
        ROI --> SM[Quản lý Trạng thái & Chống nhiễu]
        SM --> EM[Quản lý Sự kiện]
        
        EM -- Ảnh chụp --> FileSys[(Local File System)]
        EM -- Lưu log --> SQLite[(Cơ sở dữ liệu SQLite)]
        
        SQLite -.-> Flask[Flask Web Dashboard]
        FileSys -.-> Flask
    end

    subgraph Mạng IoT
        EM -- Publish --> MQTT[Mosquitto Broker]
        MQTT -- Subscribe --> ESP[ESP32 / YOLO:bit]
        ESP --> LED[Đèn LED NeoPixel]
        ESP --> Buzzer[Còi báo động]
    end
    
    User((Người dùng)) --> Flask
```

---

## 🔄 Cách thức Hoạt động (How It Works)

1. **Giai đoạn Thị giác:** Camera chụp khung hình và truyền vào mô hình YOLO đã được tối ưu hóa bằng ONNX.
2. **Sàng lọc:** Các đồ vật được phát hiện sẽ được chọn lọc. Chỉ những đồ vật nằm trong `Desk ROI` và khớp với danh sách `target_classes` (VD: airpods, chuột) mới được theo dõi.
3. **Theo dõi Trạng thái:** `StateManager` theo dõi lịch sử của từng món đồ. Nếu một món đồ bị mất dạng trong số khung hình `MAX_MISSED_FRAMES` liên tiếp, trạng thái của nó chuyển từ `CÓ MẶT` (PRESENT) sang `BIẾN MẤT` (ABSENT).
4. **Kích hoạt Sự kiện:** `EventManager` nhận thấy sự thay đổi trạng thái và tạo ra sự kiện `REMOVED`. Nó lưu lại khung hình dưới dạng ảnh chụp (snapshot) và ghi dữ liệu vào SQLite.
5. **Phát sóng IoT:** `MQTTClient` gửi một cục dữ liệu JSON `{"event": "REMOVED", "object": "airpods_1"}` lên broker.
6. **Hành động Phần cứng:** ESP32 nhận dữ liệu qua WiFi, nháy đèn LED màu đỏ và phát tiếng còi cảnh báo.

---

## 🛠️ Công nghệ Sử dụng (Technology Stack)

### AI / Computer Vision
| Công nghệ | Mục đích |
|---|---|
| **Ultralytics YOLOv8** | Mô hình lõi để nhận diện vật thể. |
| **OpenCV (cv2)** | Đọc camera, xử lý hình ảnh, vẽ khung nhận diện. |
| **ONNX Runtime** | Động cơ chạy suy luận (inference) tốc độ cao cho mô hình đã ép nén. |

### Software & Backend
| Công nghệ | Mục đích |
|---|---|
| **Python 3.11** | Ngôn ngữ chạy logic cốt lõi. |
| **Flask** | Máy chủ web để tạo Dashboard giám sát từ xa. |
| **SQLite** | Cơ sở dữ liệu quan hệ gọn nhẹ để lưu log sự kiện siêu tốc. |

### Embedded / Hardware
| Linh kiện | Mục đích |
|---|---|
| **ESP32 (YOLO:bit)** | Vi điều khiển xử lý tín hiệu cảnh báo phần cứng. |
| **NeoPixel (WS2812)** | Đèn LED RGB hiển thị màu sắc cảnh báo. |
| **Buzzer** | Còi báo động. |

### Hạ tầng mạng (Infrastructure)
| Công nghệ | Mục đích |
|---|---|
| **Mosquitto MQTT** | Máy chủ trung gian (Broker) kết nối PC và ESP32. |

---

## 📂 Cấu trúc Thư mục (Project Structure)

```text
Smart_desk/
├── config/
│   └── config.yaml             # Cấu hình hệ thống (ROI, Ngưỡng nhiễu, IP Broker)
├── dashboard/
│   ├── app.py                  # Ứng dụng Web Flask
│   ├── static/                 # File CSS & JS
│   └── templates/              # File HTML
├── dataset/
│   └── smartdesk_dataset.yaml  # Cấu hình Dataset để train YOLO
├── esp32/
│   └── smart_desk_esp32/       # Source code C++ (Arduino) cho ESP32
├── models/
│   └── best.onnx               # Mô hình AI ONNX đã tối ưu tốc độ
├── outputs/
│   └── snapshots/              # Ảnh chụp bằng chứng các sự kiện
├── logs/
│   └── smart_desk.db           # Cơ sở dữ liệu SQLite
├── src/
│   ├── main.py                 # File chạy chính của ứng dụng
│   ├── detector.py             # Logic AI YOLO
│   ├── tracker.py              # Theo dõi & lọc đồ vật
│   ├── state_manager.py        # Logic chuyển đổi trạng thái & Chống nhiễu
│   ├── event_manager.py        # Tạo sự kiện & ghi log
│   ├── mqtt_client.py          # Kết nối đẩy dữ liệu MQTT
│   ├── storage.py              # Logic giao tiếp SQLite
│   ├── data_collector.py       # Công cụ: Chụp ảnh tạo dataset
│   ├── split_dataset.py        # Công cụ: Chia dataset thành Train/Val
│   ├── train.py                # Công cụ: Script tự động huấn luyện YOLO
│   └── export_onnx.py          # Công cụ: Ép nén PyTorch sang ONNX
├── requirements.txt
└── README.md
```

---

## 📋 Yêu cầu Cấu hình (Requirements)

- **Hệ điều hành:** Windows 10/11 hoặc Linux
- **Ngôn ngữ:** Python 3.10 hoặc 3.11
- **Phần cứng (PC):** CPU phổ thông (Intel i5/Ryzen 5 trở lên). Không bắt buộc phải có GPU (Card màn hình rời) nhờ sự tối ưu của ONNX.
- **Phần cứng (Camera):** Bất kỳ Webcam USB hoặc camera tích hợp của laptop.
- **Phần cứng (IoT):** Mạch phát triển ESP32 (Ví dụ: YOLO:bit).
- **Phần mềm:** Cài đặt sẵn dịch vụ Mosquitto MQTT Broker chạy trên máy.

---

## 🚀 Hướng dẫn Cài đặt (Installation)

1. **Clone mã nguồn:**
   ```bash
   git clone https://github.com/DuyChuong3011/Smart_desk.git
   cd Smart_desk
   ```

2. **Tạo môi trường ảo (Virtual Environment):**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1   # Trên Windows PowerShell
   # source .venv/bin/activate  # Trên Linux/Mac
   ```

3. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   pip install onnx onnxruntime  # Cài lõi chạy ONNX tốc độ cao
   ```

4. **Nạp code cho ESP32:**
   - Mở file `esp32/smart_desk_esp32/smart_desk_esp32.ino` bằng Arduino IDE.
   - Sửa lại Tên WiFi và Mật khẩu trong code cho đúng với mạng nhà bạn.
   - Compile và Upload code lên mạch ESP32.

---

## ⚙️ Cấu hình (Configuration)

Mọi thông số quan trọng đều nằm ở `config/config.yaml`.

```yaml
camera:
  index: 0
  width: 1280
  height: 720

detection:
  model_path: "models/best.onnx"
  imgsz: 320
  skip_frames: 15
  target_classes:
    - "mouse"
    - "keyboard"
    - "airpods"

mqtt:
  broker: "127.0.0.1" # Hãy đổi IP này thành IP của Broker nếu bạn chạy máy ảo/máy tính khác
  port: 1883
```

---

## ▶️ Cách Khởi chạy (Running the Project)

Để khởi động toàn bộ hệ thống, bạn cần bật 2 cửa sổ Terminal:

**Terminal 1: Khởi động Web Dashboard**
```bash
.venv\Scripts\Activate.ps1
python dashboard/app.py
```
*Truy cập bảng điều khiển tại địa chỉ `http://127.0.0.1:5000`*

**Terminal 2: Khởi động Lõi AI**
```bash
.venv\Scripts\Activate.ps1
python src/main.py
```

*Lưu ý: Đảm bảo dịch vụ Mosquitto broker của bạn đang chạy ngầm ở background.*

---

## 🎯 Trường hợp Sử dụng (Use Cases)

- **Quản lý Đồ cá nhân:** Theo dõi các đồ vật thường xuyên bị thất lạc (chìa khóa, ví tiền, AirPods).
- **Phân tích Hành vi:** Ghi lại tần suất và thời điểm bạn sử dụng một vật dụng cụ thể trên bàn làm việc.

---

## ⚠️ Giới hạn hệ thống (Limitations)

- **Nghẽn cổ chai CPU:** Mặc dù ONNX đã cải thiện tốc độ đáng kể, việc chạy YOLOv8 liên tục vẫn tiêu tốn khá nhiều tài nguyên CPU trên các máy tính không có GPU chuyên dụng. Khuyến nghị thiết lập `skip_frames` để giảm tải.
- **Phụ thuộc Ánh sáng:** Độ chính xác của việc nhận diện đồ vật giảm mạnh trong điều kiện thiếu sáng.
- **Che khuất (Occlusion):** Nếu một đồ vật bị che khuất hoàn toàn bởi một đồ vật khác lớn hơn (ví dụ: laptop che khuất chùm chìa khóa), hệ thống sẽ ghi nhận đồ vật đó đã bị `BIẾN MẤT` (REMOVED).
---
