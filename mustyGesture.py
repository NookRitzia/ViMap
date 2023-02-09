from HandGestureTracker import *
import pickle


tracker = HandGestureTracker()


def app_runner():
    while True:
        print(f'dX:{tracker.get_last_delta_x()}, dY:{tracker.get_last_delta_y()}, commands:{tracker.get_last_gesture()}')
        #print(str(tracker.get_last_delta_x()) + " " + str(tracker.get_last_delta_y()))
        time.sleep(0.1)

        #dX, dY, gesture = tracker.get_last_delta_x(), tracker.get_last_delta_y(), tracker.get_last_gesture()


#dash_server_thread = threading.Thread(target=frontEnd, daemon=True)
tracker_thread = threading.Thread(target=tracker.main, daemon=True)
app_runner_thread = threading.Thread(target=app_runner, daemon=False)

tracker_thread.start()
#dash_server_thread.start()
app_runner_thread.start()

#dash_server_thread.join()
tracker_thread.join()
app_runner_thread.join()