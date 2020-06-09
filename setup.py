# Schedule Library imported 
import schedule 
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
schedule.every(30).minutes.do(main)
# schedule.every(10).seconds.do(main)



if __name__ == '__main__':
    # main()
    # Loop so that the scheduling task 
    # keeps on running all time. 
    while True: 
    
        # Checks whether a scheduled task  
        # is pending to run or not 
        schedule.run_pending() 
        time.sleep(1) 