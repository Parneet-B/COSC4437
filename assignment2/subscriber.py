# MQTT Twitter Subscriber - COSC Assignment 2

import tkinter as tk
from tkinter import scrolledtext
import paho.mqtt.client as mqtt

# MQTT broker details 
BROKER = "test.mosquitto.org"
PORT = 1883

# the window for subscribing to tweets
root = tk.Tk()
root.title("Subscribe to Tweets")
root.geometry("420x320")

# box where the user enters topic or hashtag
tk.Label(root, text="Hashtag or Topic (without #):").pack(pady=4)
topic_box = tk.Entry(root, width=35)
topic_box.pack()

# text area where messages are displayed
output_box = scrolledtext.ScrolledText(root, width=50, height=15)
output_box.pack(pady=6)

# MQTT client
client = mqtt.Client()

# when connected to broker, callback
def when_connected(client, userdata, flags, status):
    if status == 0:
        output_box.insert(tk.END, "Successfully connected to MQTT broker.\n")
    else:
        output_box.insert(tk.END, f"Unsuccessful - Connection failed: {status}\n")

# callback -> when a message arrives from the subscribed topic
def when_messaged(client, userdata, msg):
    text = msg.payload.decode()
    output_box.insert(tk.END, f"{text}\n")
    output_box.see(tk.END)
    print("Received:", text)

# assigned callbacks
client.on_connect = when_connected
client.on_message = when_messaged

# trying to connect to the broker
try:
    client.connect(BROKER, PORT, 60)
    print("Successfully connected to MQTT broker.")
except:
    print("Unsuccessful - Failed to connect.")

# always start listening right after connecting
client.loop_start()

# button functions for subscribing and unsubscribing
def subscribe_to_topic():
    topic = topic_box.get().strip()
    if topic:
        # subscribe to the entered topic 
        client.subscribe(topic)
        output_box.insert(tk.END, f"Successfully subscribed to #{topic}\n")
        print("Subscribed to:", topic)

def unsubscribe_to_topic():
    topic = topic_box.get().strip()
    if topic:
        client.unsubscribe(topic)
        output_box.insert(tk.END, f"Successfully unsubscribed from #{topic}\n")
        print("Unsubscribed from:", topic)

# buttons for subscribing and unsubscribing
tk.Button(root, text="Subscribe", command=subscribe_to_topic, bg="black", fg="white").pack(pady=3)
tk.Button(root, text="Unsubscribe", command=unsubscribe_to_topic, bg="black", fg="white").pack(pady=3)


# start GUI window
root.mainloop()

# stop MQTT loop after window closes
client.loop_stop()
