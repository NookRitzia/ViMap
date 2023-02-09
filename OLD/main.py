import threading
import time

import HandGestureTracker as ht
def gesture_tracker():
    ht.main()

def app_runner():
    while True:
        print("hi!")


thread_1 = threading.Thread(target=gesture_tracker, daemon=False)
thread_2 = threading.Thread(target=app_runner, daemon=True)

thread_1.start()
thread_2.start()


thread_1.join()
thread_2.join()


print("hello")