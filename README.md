# UR10E
Code for UR10E 

# JSON Payload

## Order of the robot
**You need to sent the order to the topic robot/order**

```json
{
    "stop": "boolean",  // if true robot is stopped
    "relative": "boolean", // if true TCP position move of distance
    "speed": "integer",
    "new_pos": ["float", "float", "float", "float", "float", "float"] // X,Y,Z,Rx,Ry,Rz of TCP distance of position
}
```
## Status of the robot
**You need to subscribe to this topic robot/status**

```json
{
    "status": "string" //OK, turn_on, turn_off
}
```