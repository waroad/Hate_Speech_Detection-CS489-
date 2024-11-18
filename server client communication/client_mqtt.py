# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt

# Broker information
broker_address = "broker.hivemq.com"
port = 1883
receive_topic = "test/cs489/1"
send_topic = "test/cs489/2"

# Callback when the client receives a message
def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    print(f"\nClient received: {received_message}")

# Create MQTT client instance and set callback
client = mqtt.Client("Client")
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, port)

# Subscribe to the topic where echo messages are received
client.subscribe(receive_topic)

# Start the loop in a separate thread to process network traffic and dispatch callbacks
client.loop_start()

# Continuously get input from CLI and send it to the server
try:
    while True:
        message = input("Enter a message to send to the server: ")
        if message.lower() == 'exit':
            break  # Exit the loop if 'exit' is typed
        client.publish(send_topic, message)
        print(f"Client sent: {message}")
except KeyboardInterrupt:
    print("\nExiting...")

# Stop the loop and disconnect cleanly
client.loop_stop()
client.disconnect()
