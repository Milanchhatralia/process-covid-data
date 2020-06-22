# Schedule Library imported 
from flask import Flask
import os
import schedule 
import threading
import time
import requests
import json

count = 1
# URL = "https://covid-live.azurewebsites.net"

def main():
    try:
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
    except Exception as e:
        print("got excetion: "+ json.dumps(e))
    
    # now heartbeat to covid-live api is sent using cron-job on every 15 minute
    # try:
    #     r = requests.get(url = URL) 
    #     print("Successfully send heartbeat to url: ", URL)
    # except Exception as e:
    #     print("error sending heartbeat to url: ", URL, " \n Error: ", e)


# Task scheduling 
# After every 30mins main() is called.  
schedule.every(15).minutes.do(main)
# schedule.every(11).seconds.do(main)

def start_scheduling():
    print("sheduling started..")
    # Loop so that the scheduling task 
    # keeps on running all time. 
    while True:
        # Checks whether a scheduled task  
        # is pending to run or not 
        schedule.run_pending() 
        time.sleep(1)

app = Flask(__name__)

x = threading.Thread(target=start_scheduling)

@app.route('/')
def heartbeat():
    return 'Hello'

if __name__ == '__main__':
    # main()
    x.start()
    PORT = os.environ.get("PORT", 5000)
    app.run(host='0.0.0.0', port= PORT, load_dotenv=True)