import threading
from devonics_api import DevonicsApi
from dobot_api import DobotApi,DobotApiMove,DobotApiDashboard, MyType
from time import sleep
import numpy as np

def connectRobot():
    try:
        ip = "192.168.5.1"
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
    
def connectTool(dashboard):
    try:
        ip = "127.0.0.1"
        port = 60000
        slave_id = 1
        rtu = 1
        model = "PGC-50"

        Tool = DevonicsApi(dashboard,ip,port,slave_id,rtu)
        print("Tool Connection Successful!")
        return Tool
    except Exception as e:
        print("Tool Connection Failed")
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
    Tool = connectTool(dashboard)

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
            Tool.initialize()
            move.Sync()
        elif choice == '2':
            print("Open Max")
            Tool.setPosition(60000)
            move.Sync()
        elif choice == '3':
            print("Close Max")
            Tool.setPosition(55000)
            move.Sync()
        elif choice == '4':
            print("")
            ## print("Check getPosition")
            new_position = Tool.getPosition()
            while new_position == -1:
                sleep(1)
                new_position = Tool.getPosition()
            print(new_position)
            print("")
        elif choice == '5':
            print("Speed Max")
            Tool.setSpeed(1000)
            move.Sync()
        elif choice == '6':
            print("Speed Mix")
            Tool.setSpeed(0)
            move.Sync()
        elif choice == '7':
            print("DisableRobot")
            dashboard.DisableRobot()
        elif choice == '8':
            print("EnableRobot")
            dashboard.EnableRobot(0,0,0,0)
        elif choice == '9':
            print("moving")
            sleep(1)
            Tool.setPosition(54800)
            sleep(1)
            Tool.setPosition(57800)
            sleep(4)            
            Tool.setPosition(54800)
            sleep(1)
            Tool.setPosition(57800)
            sleep(4)               
            Tool.setSpeed(400)
            sleep(0.5)            
            Tool.setPosition(57800)
            sleep(4)
            move.ServoJ(220.5336, -0.7835, -101.3674, -77.0847, -99.0267, -270.0711) ##up 1
            sleep(1)
            dashboard.SpeedFactor(20)
            move.ServoJ(220.5053, -4.2104, -109.9835, -65.0564, -98.7649, -270.1451) ##down 1
            sleep(2)
            Tool.setPosition(37000)
            sleep(10)            
            move.ServoJ(220.5336, -0.7835, -101.3674, -77.0847, -99.0267, -270.0711) ##up 1
            sleep(1)
            move.ServoJ(230.9164, 11.0592, -113.8871, -76.6806, -88.6233, -270.2754)  ##up 2
            sleep(1)
            move.ServoJ(230.8801, 8.7287, -120.1101, -68.1278, -88.4557, -270.3236) ## down 2
            sleep(2)
            Tool.setPosition(60000)
            sleep(10)
            move.ServoJ(230.9164, 11.0592, -113.8871, -76.6806, -88.6233, -270.2754)  ##up 2
            sleep(1)
            Tool.setPosition(50800)
            sleep(1)
            Tool.setPosition(56800)
            sleep(1)
            Tool.setPosition(60000)
        elif choice == '-':
            print("GetErrorID")
            print(dashboard.GetErrorID())
        elif choice == '0':
            print("Disconnect")
            Tool.disconnect()
            dashboard.DisableRobot()
            condition = False
        elif choice == 'r':
            move.ServoJ(265,60,-130,-20,90,-270)
        else:
            print("Please select a valid option")        
   

main()