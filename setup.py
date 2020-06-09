# Schedule Library imported 
from flask import Flask
import os
import schedule 
import threading
import time


count = 1

def main():
    global count
    print("running process covid data ",count," time")
    # run initWorldCity.py file
    print("...Running initWorldCity.py file...")
    exec(open('initWorldCity.py').read())
    print("...Succesfully ran initWorldCity.py file...\n")

    # run initWorldState.py file
    print("...Running initWorldState.py file...")
    exec(open('initWorldState.py').read())
    print("...Succesfully ran initWorldState.py file...\n\n")
    count = count + 1

# Task scheduling 
# After every 30mins main() is called.  
schedule.every(25).minutes.do(main)
# schedule.every(10).seconds.do(main)

def start_scheduling():
    # Loop so that the scheduling task 
    # keeps on running all time. 
    while True: 
        print("sheduling working..")
        # Checks whether a scheduled task  
        # is pending to run or not 
        schedule.run_pending() 
        time.sleep(1)

app = Flask(__name__)

x = threading.Thread(target=start_scheduling)

if __name__ == '__main__':
    # main()
    x.start()
    PORT = os.environ.get("PORT", 5000)
    app.run(host='0.0.0.0', port= PORT, load_dotenv=True)