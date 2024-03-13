### Arduino Load Cell Sensor with Python UI

## Materials:
- Arduino Uno board
- Load Cell Sensor (any weight)
- Hx711 Amplifier
- Some wires
- Breadboard (optional)

## Software:
- Arduino IDE
- Python
- VS Code (optional)

## Usage:
1. Clone this repository: [Arduino Project](https://github.com/xxlllllllxx/Arduino-Project.git)
2. Open the project in VS Code.
3. Navigate to `/Arduino/main.ino` and open [main.ino](https://github.com/xxlllllllxx/Arduino-Project/blob/main/Adruino/main.ino).
4. Connect the Arduino board, Hx711, and Load cell sensor with the provided configuration.
![Arduino Schema](/src/image1.png)
5. Connect the Arduino board to the PC using a USB connector.
6. Identify the port of the Arduino.
7. Go to `/Python/main.py` and open [main.py](https://github.com/xxlllllllxx/Arduino-Project/blob/main/Python/main.py).
8. Modify line 30 in [main.py](https://github.com/xxlllllllxx/Arduino-Project/blob/main/Python/main.py) to match the Arduino port.
9. Upload and run [main.ino](https://github.com/xxlllllllxx/Arduino-Project/blob/main/Adruino/main.ino).
10. Run [main.py](https://github.com/xxlllllllxx/Arduino-Project/blob/main/Python/main.py).
11. Observe the graphs.

![Python UI](/src/image2.png)

## Configurations:
- In settings, adjust the accuracy for calibrating the graphs output.
- Click "calibrate". Ensure no materials are currently on top of the sensor, then click "start".
- Wait for the list to stabilize, then click "ok".
- Add the weight and input the known weight of the object in the popup using kilograms. Click "start".
- Wait for the list to stabilize, then click "ok".
- Verify if the measurements are correct by observing the graphs.
