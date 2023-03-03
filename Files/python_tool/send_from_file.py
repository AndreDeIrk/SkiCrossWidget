import sys
import time
import numpy as np
import NDIlib as ndi
import cv2
import json
from pynput import keyboard
import threading

class vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x 
        self.y = y
        self.z = z



RES = vector(1920, 1080)
MAP_RES = vector(400, 400)
# MAP_DIRECTION = vector(1., 1.)
MAP_SPEED = vector(1., 1.)

def inc(a: str, d: float):
    return str(float(a) + d)

def next_map_position(x: str, y: str, dx=1., dy=1.):
    global MAP_SPEED
    if (0 < float(x) + dx < RES.x - MAP_RES.x):
        pass
    else:
        MAP_SPEED.x = -MAP_SPEED.x
        dx = MAP_SPEED.x

    if (0 < float(y) + dy < RES.y - MAP_RES.y):
        pass
    else:
        MAP_SPEED.y = -MAP_SPEED.y
        dy = MAP_SPEED.y
    
    return inc(x, dx), inc(y, dy)

telemetry = dict(
    Team='USSR',
    Speed='100mph',
    Widget=dict(
        Map=dict(
            Visible='On',
            X='0.0',
            Y='0.0',
        ),
        DetailLong=dict(
            Visible='On',
        ),
    ),    
    Length="1.0",
    Data='0'*(2**10),
)
# WORKING = True    
# stop_event = threading.Event()
controller = keyboard.Controller()

class StopException(Exception): pass

def on_press(key):
    global telemetry
    try: 
        if key == keyboard.Key.home:
            raise StopException(key)
        elif key.char == 'm':
            telemetry["Widget"]["Map"]["Visible"] = 'On' if telemetry["Widget"]["Map"]["Visible"] == 'Off' else 'Off'
            print(f'Map switched to {telemetry["Widget"]["Map"]["Visible"].upper()}')
            # Collect events until released
        elif key.char == 'l':
            telemetry["Widget"]["DetailLong"]["Visible"] = 'On' if telemetry["Widget"]["DetailLong"]["Visible"] == 'Off' else 'Off'
            print(f'DetailLong switched to {telemetry["Widget"]["DetailLong"]["Visible"].upper()}')
            # Collect events until released
        elif key.char == "p":
            telemetry["Data"] = "0"*(2**16)
            print('Decrease data')
    except AttributeError:
        pass


def kb_catch():
    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except StopException as e:
            print(f'{e.args[0]} was pressed')
        except Exception as e:
            print(f'Keyboard exception: {e}')

listener = threading.Thread(target=kb_catch)

def main():

    if not ndi.initialize():
        return 0

    ndi_send = ndi.send_create()

    if ndi_send is None:
        return 0

    # img = np.zeros((1080, 1920, 4), dtype=np.uint8)

    video_frame = ndi.VideoFrameV2()
    video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX

    # print(f'Frame format: {video_frame.data.shape}')

    listener.start()

    while True:
        try:
            vidcap = cv2.VideoCapture('planes.mp4')
            success, image = vidcap.read()
            count = 0
            print(f'{count=}')
            telemetry["Widget"]["Map"]["X"] = '0.0'
            telemetry["Widget"]["Map"]["Y"] = '0.0'
            telemetry["Data"] = "0"*(2**16)
            
            while success:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
                video_frame.data = image
                # telemetry["Widget"]["Map"]["X"] = inc(telemetry["Widget"]["Map"]["X"], 1.0)
                # telemetry["Widget"]["Map"]["Y"] = inc(telemetry["Widget"]["Map"]["Y"], 1.0)
                telemetry["Widget"]["Map"]["X"], telemetry["Widget"]["Map"]["Y"] = next_map_position(x=telemetry["Widget"]["Map"]["X"], 
                                                                                                     y=telemetry["Widget"]["Map"]["Y"],
                                                                                                     dx=MAP_SPEED.x,
                                                                                                     dy=MAP_SPEED.y)
                # if count % 30 == 0:
                #     telemetry["Data"] += "0"*(2**16)
                telemetry["Length"] = len(json.dumps(telemetry))
                video_frame.metadata = f'<json>{json.dumps(telemetry)}</json>'#json.dumps(telemetry[count])

                ndi.send_send_video_v2(ndi_send, video_frame)

                success, image = vidcap.read()
                count += 1

            print(f'{count=}')    
            print('Starting video again...')
        except KeyboardInterrupt:
            print('Keyboard interruption...')
            # stop_event.set()
            controller.press(keyboard.Key.home)
            break

    listener.join()
    ndi.send_destroy(ndi_send)

    ndi.destroy()
    print('FINISHED')
    return 0

if __name__ == "__main__":
    sys.exit(main())
