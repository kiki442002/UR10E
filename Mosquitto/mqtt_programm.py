import paho.mqtt.client as mqtt

topic_order = "robot/order"
topic_info = "robot/info"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic_info)  # Subscribe to a topic

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")

# Create an MQTT client
client = mqtt.Client()
# Définir le nom d'utilisateur et le mot de passe
client.username_pw_set("user", "admin")


# Set up callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker (replace with your broker details)
broker_address = "localhost"
client.connect(broker_address, 1883, 60)

# Start the MQTT loop
client.loop_start()

# Publish a message to the topic
client.publish(topic_order, "Hello, MQTT!")

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Script terminated.")

# Disconnect from the broker
client.disconnect()
