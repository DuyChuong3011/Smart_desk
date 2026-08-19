#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>

// --- Cấu hình WiFi ---
const char *ssid = "Free_Wifie";
const char *password = "tenwaifucuatoi";

// --- Cấu hình MQTT ---
const char *mqtt_server = "192.168.137.1";
const int mqtt_port = 1883;
const char *mqtt_topic = "smartdesk/events";

// --- Cấu hình Chân ESP32 (YOLO:bit) ---
#define RGB_PIN P14
#define BUZZER_PIN P1
#define NUM_LEDS 4

// Khởi tạo đối tượng LED RGB
Adafruit_NeoPixel strip(NUM_LEDS, RGB_PIN, NEO_GRB + NEO_KHZ800);

WiFiClient espClient;
PubSubClient client(espClient);

void setAllLEDs(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}

// ==========================================
// HÀM KIỂM TRA PHẦN CỨNG KHI KHỞI ĐỘNG
// ==========================================
void testHardware() {
  Serial.println("================================");
  Serial.println("Dang kiem tra LED RGB (P14) va Buzzer (P1)...");

  for (int i = 0; i < 3; i++) {
    setAllLEDs(255, 0, 0);  // Bật 4 LED màu đỏ
    tone(BUZZER_PIN, 2000); // Còi kêu
    delay(150);

    setAllLEDs(0, 0, 0); // Tắt toàn bộ LED
    noTone(BUZZER_PIN);  // Tắt còi
    delay(150);
  }

  Serial.println("Kiem tra phan cung hoan tat!");
  Serial.println("================================");
}
// ==========================================

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  // Chuyển payload thành string
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }
  Serial.println(messageTemp);

  // Parse JSON
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, messageTemp);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  const char *event_type = doc["event"];
  const char *object_name = doc["object"];

  // Phản ứng khi có sự kiện một vật thể bị lấy ra khỏi bàn
  if (strcmp(event_type, "REMOVED") == 0) {
    Serial.print("ALARM! Object REMOVED: ");
    Serial.println(object_name);

    // Bật LED đỏ và Buzzer cảnh báo
    setAllLEDs(255, 0, 0);  // Đỏ
    tone(BUZZER_PIN, 1000); // Kêu còi tần số 1000Hz

    delay(2000); // Báo động trong 2 giây

    setAllLEDs(0, 0, 0); // Tắt LED
    noTone(BUZZER_PIN);
  }
  // Phản ứng khi vật thể được đặt lại
  else if (strcmp(event_type, "APPEARED") == 0) {
    Serial.print("Object APPEARED: ");
    Serial.println(object_name);

    // Nháy đèn 1 lần màu xanh lá để báo hiệu
    setAllLEDs(0, 255, 0); // Xanh lá
    delay(200);
    setAllLEDs(0, 0, 0); // Tắt LED
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Tạo ID ngẫu nhiên cho ESP32
    String clientId = "ESP32SmartDesk-";
    clientId += String(random(0, 1000));

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Subscribe vào topic smartdesk
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Khởi tạo dải LED NeoPixel
  strip.begin();
  strip.show(); // Tắt toàn bộ LED ban đầu

  pinMode(BUZZER_PIN, OUTPUT);

  // Gọi hàm kiểm tra thiết bị ngay sau khi khai báo chân
  testHardware();

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
