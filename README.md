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
    "stop": "boolean",  // if true robot is stopped
    "freedrive": "boolean",  //allow the robot to be move by the hands of operator
    "speed": "integer",

    "program_loop": "boolean", //loop the instruction
    "reference_plan": "char[2]", // if true TCP position move of distance
    "new_pos": ["float", "float", "float", "float", "float", "float"], // X,Y,Z,Rx,Ry,Rz of reference plan
    "target_point": "integer", // go to target point 1,2,3 etc...
    "gripper": ["integer","integer", "boolean"], // target, force, depth compensation    
    "systeme_msg" : "String" //message shwow to the operator
}
```
## Status of the robot
**You need to subscribe to this topic robot/status**

```json
{
    "status": "string" //OK, turn_on, turn_off
}
```