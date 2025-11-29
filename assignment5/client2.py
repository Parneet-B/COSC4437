import socket
import threading
import time
import random

host = '127.0.0.1'
port = 5050
name = "Player 2"
clock = time.time()

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((host, port))

def drift():
    global clock
    while True:
        clock += 1 + random.uniform(-0.05, 0.05)
        time.sleep(1)

def listen():
    while True:
        try:
            msg = c.recv(1024).decode()
            if msg:
                print(msg)
        except:
            break

#Cristian's Algorithm for clock sync
def sync_clock():
    global clock
    while True:
        try:
            start = time.time()
            c.send("TIME_REQUEST".encode())   #requests the server time 
            reply = c.recv(1024).decode()
            if reply.startswith("TIME_REPLY"):
                server_time = float(reply.split("|")[1])
                rtt = time.time() - start
                clock = server_time + rtt/2       #clock adjusts according to the round trip time
        except:
            pass
        time.sleep(5)     #sync every 5 seconds

def play():
    moves = ["move", "shoot", "pickup"]
    while True:
        m = random.choice(moves)
        time.sleep(random.uniform(1, 3))
        c.send(f"{clock}|{name}|{m}".encode())

threading.Thread(target=drift, daemon=True).start()
threading.Thread(target=listen, daemon=True).start()
threading.Thread(target=sync_clock, daemon=True).start()
threading.Thread(target=play, daemon=True).start()

while True:
    time.sleep(1)
