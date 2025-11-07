# MQTT Twitter Publisher - COSC Assignment 2

import tkinter as tk
from tkinter import scrolledtext
import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "test.mosquitto.org"
PORT = 1883

# the window for subscribing to tweets
window = tk.Tk()
window.title("Publish Tweets")
window.geometry("400x320")

# box where the user enters username
tk.Label(window, text="Enter username:").pack(pady=4)
username_box = tk.Entry(window, width=35)
username_box.pack()

# tweet text's box
tk.Label(window, text="Enter tweet Message:").pack(pady=4)
tweet_box = tk.Entry(window, width=40)
tweet_box.pack()

# box for hashtag or topic name (without #)
tk.Label(window, text="Hashtag or Topic (without #):").pack(pady=4)
topic_box = tk.Entry(window, width=35)
topic_box.pack()

# output or result area to show connection and status messages
output_box = scrolledtext.ScrolledText(window, width=45, height=8)
output_box.pack(pady=6)

#  MQTT client
client = mqtt.Client()

# callback for successful or failed connections
def when_connected(client, userdata, flags, status):
    if status == 0:
        output_box.insert(tk.END, "Successfully connected to MQTT broker.\n")
    else:
        output_box.insert(tk.END, f"Unsuccessful - Connection failed: {status}\n")

# callback that print messages 
def when_messaged(client, userdata, msg):
    text = msg.payload.decode()
    output_box.insert(tk.END, f"#{msg.topic}: {text}\n")
    output_box.see(tk.END)
    print("Received:", text)

# callbacks assigned to client
client.on_connect = when_connected
client.on_message = when_messaged

# trying to connect to the broker
try:
    client.connect(BROKER, PORT, 60)
    output_box.insert(tk.END, "Successfully connected to MQTT broker.\n")
except:
    output_box.insert(tk.END, "Unsuccessful - Failed to connect to broker.\n")

# start the loop right after connecting so publisher stays connected
client.loop_start()

# function for sending the tweet
def send_tweet():
    # get input 
    user = username_box.get().strip()
    msg = tweet_box.get().strip()
    topic = topic_box.get().strip()

    # validation for empty boxes
    if not user or not msg or not topic:
        output_box.insert(tk.END, "Please fill all fields to proceed.\n")
        return

    # the topic will work exactly as the user entered it
    full_topic = topic

    # formating the tweet message
    message = f"{user}: {msg}"

    # publish the message (made retain = False so it's not stored on broker)
    client.publish(full_topic, message, retain=False)

    # confirmation in the window
    output_box.insert(tk.END, f"Tweet posted to #{topic}\n")
    output_box.see(tk.END)

    # after sending, clear the tweet box
    tweet_box.delete(0, tk.END)

    # alongside printing confirmation in terminal
    print("Published:", message)

# button that publishes the tweet
tk.Button(window, text="Publish", command=send_tweet, bg="#1DA1F2", fg="white").pack(pady=10)

# start the Tkinter main window loop
window.mainloop()

# stop MQTT loop when window closes
client.loop_stop()
