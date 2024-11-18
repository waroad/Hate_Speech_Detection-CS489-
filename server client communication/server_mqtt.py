# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt

# Broker information
broker_address = "broker.hivemq.com"
port = 1883
receive_topic = "test/cs489/2"
send_topic = "test/cs489/1"

# Callback when the server receives a message
def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    print(f"Server received: {received_message}")
    client.publish(send_topic, f"Echo: {received_message}")
    print(f"Server sent: Echo: {received_message}")

# Create MQTT client instance
client = mqtt.Client("Server")
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, port)

# Subscribe to the topic
client.subscribe(receive_topic)

# Start the loop to process network traffic and dispatch callbacks
print("Server is listening for messages...")
client.loop_forever()
