# IoT 기반 실시간 침입 감지 및 자동 대응 시스템
**(Smart Intrusion Detection System with Raspberry Pi)**

### 프로젝트 개요
조도 센서(SPI)와 카메라를 활용하여 **외부 침입을 실시간으로 감지**하고, 
서보 모터와 LED를 통한 **물리적 대응** 및 웹 대시보드를 통한 **원격 관제**가 가능한 보안 시스템입니다.
한정된 GPIO 핀을 효율적으로 사용하기 위해 **Shift Register(74HC595)** 칩을 활용하여 회로를 최적화했습니다.

### 기술 스택
* **Hardware:** Raspberry Pi 4, Pi Camera, Servo Motor (SG90), Shift Register (74HC595), MCP3008 (ADC)
* **Language:** Python 3 (GPIOZero, OpenCV), JavaScript
* **Network:** MQTT (Paho), Flask (Web Server)
* **Protocol:** SPI (Sensor), GPIO (Actuator)

### 시스템 아키텍처 (Architecture)
> **[Sensor]** 조도 감지 -> **[Process]** 침입 판단 (Python) -> **[Action]** 1. 촬영 & 전송 / 2. 모터 구동 / 3. LED 경고 -> **[Web]** 실시간 모니터링

### 핵심 기술 포인트
1.  **자원 최적화 (Resource Optimization):**
    * GPIO 핀 부족 문제를 해결하기 위해 **74HC595 시프트 레지스터**를 도입, 3개의 핀만으로 8개의 LED 패턴(순차 점등, 랜덤 등)을 제어함.
2.  **이기종 간 통신 (MQTT Protocol):**
    * Python(하드웨어 제어)과 JavaScript(웹 클라이언트) 간의 데이터를 **MQTT 브로커(Mosquitto)**를 통해 실시간으로 주고받음.
3.  **영상 처리 및 전송:**
    * OpenCV로 침입 순간을 포착하고, 비동기 방식으로 웹 서버에 이미지를 전송하여 보안 공백 최소화.

### 실행 화면 및 회로도

<img width="452" height="255" alt="image" src="https://github.com/user-attachments/assets/f7c7a6e4-9482-4e07-b2e4-6b17e72913d4" />

<img width="758" height="480" alt="스크린샷 2025-11-29 21 24 14" src="https://github.com/user-attachments/assets/d84e6a89-f1e1-4fc1-97fe-ca1dc8af9e7f" />

자세한 시현 동영상은 파일 첨부하겠습니다.
