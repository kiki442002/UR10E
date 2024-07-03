# UR10E controller over MQTT
This repository allow the robot UR10e to be controlled by MQTT commands with this plugin:  https://www.universal-robots.com/fi/plus/products/4each/mqtt-connector-professional/.

# MQTT Broker
## Requirements
Install mosquitto broker: https://mosquitto.org/download/  

All setup files are in Mosquitto directory of this repository.

Set up your ip adress to be on the network: 192.168.4.0/24 and the ip adress of the broker must be 192.168.4.1 (basicely your PC).

## Start broker
You can start it with:

```
mosquitto -c path/of/mosquitto_robot.conf
```

You may have probleme with mosquitto_pswd.conf file. To resolve this start mosquitto in the current directory or change the line:
```
password_file path/of/file/mosquitto_pswd.conf
``` 

# JSON Payload

## Order of the robot
**You need to sent the order to the topic robot/order**
```json
{
     
    "order": "integer", 
    "new_pos": ["float", "float", "float", "float", "float", "float"],
    "target_point": "integer",
    "freedrive": "integer",
    "systeme_msg": "String"
}
```
Field description:


order: Defines the robot action type: give an object to preset zone at the user (1), take an object to user at the preset zone (2), make a relative movement (3), set the robot in freedrive (4), stop the robot in emergency (5), go robot at home position (6) or (-1) if there is an error in the request.
new_pos: Robot position in meters. x: Positive = Right, Negative = Left y: Positive = Front, Negative = Back z: Positive = Down, Negative = Up / rx, ry, rz: Robot rotation in degrees (specify rotation axes). By default, relative movement values are in centimeters.
target_point: Zone where the robot moves in absolute movement. The zones can be named tools (-1) if there is a problem with an absolute movement command.
freedrive: Take an object to user at the preset zone in freedrive mode (1).
systeme_msg: Description of problems encountered when interpreting the command (leave blank if no error).

## Status of the robot
**You need to subscribe to this topic robot/status**

```json
{
    "status": "string" //OK, turn_on, turn_off
}
```