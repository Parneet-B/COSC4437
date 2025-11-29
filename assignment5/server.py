import socket
import threading
import time

host = '127.0.0.1'
port = 5050

players = []

def handle_player(conn, addr):
    players.append(conn)
    print(addr, "joined")

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            #added this for clock sync
            if data == "TIME_REQUEST":
                now = time.time()      #the server sends the current time for Crisitan's Algorithm
                conn.send(f"TIME_REPLY|{now}".encode())
                continue

            #player actions
            parts = data.split("|")
            if len(parts) == 3:
                ts, who, action = parts
                line = f"{ts}|{who}|{action}"
                for p in players:
                    if p != conn:
                        p.send(line.encode())
    except:
        pass

    try:
        players.remove(conn)
    except:
        pass

    print(addr, "left")
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()
print("Server is running...")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_player, args=(conn, addr), daemon=True).start()
