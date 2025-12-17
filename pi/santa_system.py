import time
import cv2
import random
import paho.mqtt.client as mqtt
from gpiozero import MCP3008, OutputDevice, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device

# --- [설정] ---
# 터미널에서 'sudo pigpiod' 실행 필수!
Device.pin_factory = PiGPIOFactory()

MQTT_BROKER = "localhost"
# 밝기 기준 (손으로 가렸을 때 값보다 약간 높게 설정)
LIGHT_THRESHOLD = 0.01 

# --- [하드웨어 연결] ---
light_sensor = MCP3008(channel=0) # 조도 센서
servo = AngularServo(18, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025) # 모터
DATA_PIN = OutputDevice(17)  # LED (DS)
LATCH_PIN = OutputDevice(27) # LED (STCP)
CLOCK_PIN = OutputDevice(22) # LED (SHCP)
camera = cv2.VideoCapture(0) # 카메라

# --- [기능 함수] ---
def shift_out(val):
    """LED 8개 제어 (0~255)"""
    LATCH_PIN.off()
    for i in range(8):
        CLOCK_PIN.off()
        if (val & (1 << (7 - i))): DATA_PIN.on()
        else: DATA_PIN.off()
        CLOCK_PIN.on()
    LATCH_PIN.on()

def move_doll_wake_up():
    """인형 기상 액션"""
    print("🧸 인형이 뒤척이며 일어납니다!")
    for _ in range(3): # 좌우 뒤척임
        servo.angle = 45; time.sleep(0.2)
        servo.angle = 135; time.sleep(0.2)
    servo.angle = 90 # 기상
    time.sleep(0.5)

def take_photo():
    """사진 촬영 및 전송"""
    if camera.isOpened():
        for _ in range(3): camera.read() # 버퍼 비우기
        ret, frame = camera.read()
        if ret:
            filename = f"santa_{int(time.time())}.jpg"
            filepath = f"./static/{filename}"
            cv2.imwrite(filepath, frame)
            print(f"\n📸 찰칵! 저장 완료: {filename}")
            client.publish("santa/photo", filename)
        else:
            print("❌ 카메라 오류")

# --- [LED 패턴] ---
def pattern_sequential():
    for _ in range(3):
        for i in range(8): shift_out(1 << i); time.sleep(0.1)
    shift_out(0)

def pattern_jingle():
    shift_out(3); time.sleep(0.3); shift_out(0); time.sleep(0.1)
    shift_out(12); time.sleep(0.3); shift_out(0); time.sleep(0.1)
    shift_out(48); time.sleep(0.3); shift_out(0); time.sleep(0.1)
    shift_out(255); time.sleep(0.5); shift_out(0)

def pattern_random():
    for _ in range(10): shift_out(random.randint(0, 255)); time.sleep(0.2)
    shift_out(0)

# --- [MQTT 설정] ---
def on_connect(client, userdata, flags, rc):
    print("📡 MQTT 브로커 연결됨")
    client.subscribe("santa/control")

def on_message(client, userdata, msg):
    global trigger_activated
    payload = msg.payload.decode("utf-8")
    print(f"🌍 웹 명령: {payload}")
    
    if payload == "pattern1": pattern_sequential()
    elif payload == "pattern2": pattern_jingle()
    elif payload == "pattern3": pattern_random()
    elif payload.isdigit():
        cmd = int(payload)
        shift_out(cmd)
        if cmd == 0: trigger_activated = False # 끄면 다시 감시 모드로

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883)
client.loop_start()

# --- [메인 루프] ---
print("🎄 산타 감지 시스템 가동 🎄")
print(f"설정: 밝기가 {LIGHT_THRESHOLD} 미만이면 작동")

trigger_activated = False
servo.angle = 0
shift_out(0)

try:
    while True:
        if not trigger_activated:
            # 1. 감시 모드
            current_light = light_sensor.value
            # flush=True로 실시간 출력 보장
            print(f"감시 중... (밝기:{current_light:.2f})   ", end="\r", flush=True)

            if current_light < LIGHT_THRESHOLD:
                print("\n\n🎅 산타 침입 감지!!! 🎅")
                move_doll_wake_up() # 인형 기상
                shift_out(255)      # LED 켜기
                take_photo()        # 사진 촬영
                trigger_activated = True 
            time.sleep(0.1) 
        else:
            # 2. 감지 후 (파티 모드)
            shift_out(255); time.sleep(0.5)
            shift_out(0); time.sleep(0.5)

except KeyboardInterrupt:
    print("\n시스템 종료")
    shift_out(0); servo.angle = 0
    servo.close(); light_sensor.close(); camera.release()
    client.disconnect()
