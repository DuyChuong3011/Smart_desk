import paho.mqtt.client as mqtt
import logging
import json

class SmartDeskMQTTClient:
    def __init__(self, config):
        self.config = config.get('mqtt', {})
        self.broker = self.config.get('broker', '127.0.0.1')
        self.port = self.config.get('port', 1883)
        self.topic = self.config.get('topic', 'smartdesk/events')
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "SmartDeskPC")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        self.connected = False

    def connect(self):
        try:
            logging.info(f"Connecting to MQTT Broker {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            self.connected = True
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            self.connected = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.warning(f"Failed to connect, return code {reason_code}")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        logging.info("Disconnected from MQTT Broker")
        self.connected = False

    def publish_event(self, event_type, object_name):
        if not self.connected:
            return
            
        payload = {
            "event": event_type,
            "object": object_name
        }
        
        try:
            msg_info = self.client.publish(self.topic, json.dumps(payload), qos=1)
            msg_info.wait_for_publish()
            logging.info(f"MQTT Published: {self.topic} -> {payload}")
        except Exception as e:
            logging.error(f"Failed to publish MQTT message: {e}")

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
