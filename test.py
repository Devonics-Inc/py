import threading
from dobot_api import DobotApi,DobotApiMove,DobotApiDashboard, MyType
from time import sleep
import numpy as np

import socket
import sys

p1 = [-231.6905,119.8266,823.0284,-177.4091,15.8925,5.0779]
p2 = [775.6298,159.0963,601.4832,-111.1863,4.9268,-79.0828]
p3 = [-732.2058,-528.9229,790.9233,-176.4117,16.0701,113.5651]
p4 = [-699.6819,-516.0453,250.8455,172.9630,16.2223,110.7230]

def connectRobot():
    try:
        ip = "192.168.5.200"
        dashboard_p = 29999
        move_p = 30003
        feed_p = 30004


        print("Connecting...")
        dashboard = DobotApiDashboard(ip, dashboard_p)
        move = DobotApiMove(ip, move_p)
        feed = DobotApi(ip, feed_p)
        print("Connection Successful!")
        return dashboard, move, feed
    except Exception as e:
        print("Failed to connect")
        raise e
    

def get_feed(feed: DobotApi):
    global feedBackData
    global current_actual
    global payload
    global centerX
    global centerY
    global centerZ
    hasRead = 0

    data = bytes()
    while hasRead < 1440:
        temp = feed.socket_dobot.recv(1440 - hasRead)
        if len(temp) > 0:
            hasRead += len(temp)
            data += temp

    a = np.frombuffer(data, dtype=MyType)
    if hex((a['test_value'][0])) == '0x123456789abcdef':
        # Refresh Properties
        feedBackData = a
        current_actual = a["tool_vector_actual"][0]
        running_status = a["running_status"][0]
        payload = a["load"][0]
        centerX = a["center_x"][0]
        centerY = a["center_y"][0]
        centerZ = a["center_z"][0]
        # print("Running_Status", running_status)
        # print("Payload:", feedBackData["load"][0])
    sleep(0.001)

def main():
    dashboard, move, feed = connectRobot()

    feed_thread = threading.Thread(target=get_feed, args=(feed,))
    feed_thread.setDaemon(True)
    feed_thread.start()

    dashboard.EnableRobot(.5,0,0,30)
    
    condition = True
    while condition:
        print("1. Re-Initialize Dispenser")
        print("2. Open Max")
        print("3. Close Max")
        print("4. Get Current Position")
        print("5. Set Max Speed")
        print("6. Set Min Speed")

        choice = input("Please select an option:")
        
        if choice == '1':
            # Tool.initialize()
            move.Sync()
        elif choice == '2':
            print("Open Max")
        elif choice == '3':
            print("Close Max")
        elif choice == '4':
            print("")
        elif choice == '5':
            print("Speed Max")
        elif choice == '6':
            print("Speed Mix")
        elif choice == '7':
            print("DisableRobot")
            dashboard.DisableRobot()
        elif choice == '8':
            print("EnableRobot")
            dashboard.EnableRobot(0,0,0,0)
        elif choice == '9':
            print("moving")
            # sleep(5)
            dashboard.SpeedFactor(20)
            move.ServoJ(*p1)
            move.Sync()
            sendToController("192.168.5.171", "3000,200")            
            sleep(1)
            move.ServoJ(*p2)
            move.Sync()
            sleep(1)
            sendToController("192.168.5.171", "1000,200")
            sleep(1)
            move.ServoJ(*p3)
            move.ServoJ(*p4)
            move.Sync()
            sleep(2)
            move.ServoJ(*p3)
            move.ServoJ(*p1)
            move.Sync()
            sendToController("192.168.5.180", "2000,400")

        elif choice == '-':
            print("GetErrorID")
            print(dashboard.GetErrorID())
        elif choice == '0':
            print("Disconnect")
            # Tool.disconnect()
            dashboard.DisableRobot()
            condition = False
        elif choice == 'r':
            move.ServoJ(265,60,-130,-20,90,-270)
        else:
            print("Please select a valid option")        

def sendToController(ip, msg):
    #send_data = input("Type some text to send =>");
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.sendto(msg.encode('utf-8'), (ip, 8888))
    print("\n\n 1. Client Sent : ", msg, "\n\n")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Client received : ", data.decode('utf-8'), "\n\n")
    s.close()
    return data.decode('utf-8')   

main()
