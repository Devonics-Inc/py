import socket
import time
import requests
import threading
from dobot.dobot_api import DobotApi,DobotApiMove,DobotApiDashboard, MyType
from time import sleep
import numpy as np
import socket
import sys
import venhubApi


robot1 = "192.168.5.200"
robot2 = "192.168.5.201"
rail1 = "192.168.5.170"
rail2 = "192.168.5.171"
conveyor = "192.168.5.180"
delivery = "192.168.5.160"


def connectRobot(ip):
    try:
        # ip = "192.168.5.201"
        dashboard_p = 29999
        move_p = 30003
        feed_p = 30004


        print("Connecting to {}...".format(ip))
        dashboard2 = DobotApiDashboard(ip, dashboard_p)
        move2 = DobotApiMove(ip, move_p)
        feed2 = DobotApi(ip, feed_p)
        print("Connection Successful!")
        return dashboard2, move2, feed2
    except Exception as e:
        print("Failed to connect")
        raise e
    

def sendToController(ip, msg):
    #send_data = input("Type some text to send =>");
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.sendto(msg.encode('utf-8'), (ip, 8888))
    print("\n\n 1. Client Sent : ", msg, "\n\n")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Client received : ", data.decode('utf-8'), "\n\n")
    # s.close()
    return data.decode('utf-8')   

def waitForRobot(dash):
    sleep(0.5)
    while True:
        mode = dash.RobotMode()
        mode_list = mode.split(',')
        print("waiting..")
        print(mode_list[1][1:2])

        sleep(0.5)

        if(mode_list[1][1:2] == "5"):
            print("done wainting")
            break

# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

#second robot(the of on the left facing the booth)
dashboard1, move1, feed1 = connectRobot(robot1)
dashboard2, move2, feed2 = connectRobot(robot2)


# print(dashboard2.RobotMode())
# dashboard.RunScript('test123')
# dashboard1.RunScript('Diet-Coke')
# quit('testing')
dashboard1.ClearError()
dashboard2.ClearError()
dashboard1.EnableRobot(1.5,0,0,30)
dashboard2.EnableRobot(1.5,0,0,30)

while True:
    try:
        # items = requests.get('http://askgpt.ddns.net:8000/items')
        items = requests.get('http://venhub.quicksytes.com/items')
        send_data = items.json()
    except Exception:
        print("Connection error, please check the store front end")
    


    # print(send_data)
    # quit(send_data)

    for item in send_data:
        
        if(len(send_data) >= 1):
            data = item['location'].split(',')
            location_data =data[:-1]
            locations = location_data[2:]
            first_location = locations[0]
            robot_id = location_data[0]
            robot_program = location_data[1]
            sku = data[-1]
            print('Starting...')
            sleep(0.5)
            print(first_location)
            print(robot_id)
            print(robot_program)
            if (robot_id == '1'):
                rail_in_use = rail1
                robot_in_use = robot1
            elif (robot_id == '2'):
                rail_in_use = rail2
                robot_in_use = robot2
            else:
                robot_in_use = 0
                quit('No Robot Selected!')

            # quit('end')

            sendToController(rail_in_use, f'{first_location},400')
            if (robot_id == '1'):
                dashboard1.SpeedFactor(60)
                dashboard1.RunScript(robot_program)
                waitForRobot(dashboard1)
            elif (robot_id == '2'):
                dashboard2.SpeedFactor(60)
                dashboard2.RunScript(robot_program)
                waitForRobot(dashboard2)
        requests.get('http://venhub.quicksytes.com/items/' + str(item['id']) + '/edit')
        print("done wainting 1 seconds")
        sendToController(rail_in_use, "1,400")
    if (len(send_data) >= 1):
            sendToController("192.168.5.180", "19000,400")
            sendToController("192.168.5.180", "-19000,400")
    time.sleep(1)
