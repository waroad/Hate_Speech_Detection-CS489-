// Environment setup
// npm install mqtt

// Code run
// node client.js

// Run `npm install mqtt` to install the MQTT library
const mqtt = require('mqtt');

// Broker information
const brokerAddress = 'mqtt://broker.hivemq.com';
const receiveTopic = 'test/cs489/1';
const sendTopic = 'test/cs489/2';

// Connect to the broker
const client = mqtt.connect(brokerAddress);

// Event handler when the client is connected to the broker
client.on('connect', () => {
    console.log('Client connected to broker');

    // Subscribe to the topic to receive messages
    client.subscribe(receiveTopic, (err) => {
        if (!err) {
            console.log(`Subscribed to topic: ${receiveTopic}`);
        } else {
            console.error('Subscription error:', err);
        }
    });
});

// Event handler when the client receives a message
client.on('message', (topic, message) => {
    console.log(`\nClient received: ${message.toString()}`);
});

// Function to send messages from the command line
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

const promptInput = () => {
    readline.question('Enter a message to send to the server: ', (input) => {
        if (input.toLowerCase() === 'exit') {
            console.log('Exiting...');
            client.end(); // Disconnect the client
            readline.close(); // Close the input interface
            return;
        }
        client.publish(sendTopic, input);
        console.log(`Client sent: ${input}`);
        promptInput(); // Recursively prompt for the next input
    });
};

// Start the prompt loop
promptInput();
