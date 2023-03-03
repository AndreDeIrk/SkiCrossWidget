import sys
import time
import numpy as np
import NDIlib as ndi
import cv2

def main():

    if not ndi.initialize():
        return 0

    ndi_send = ndi.send_create()

    if ndi_send is None:
        return 0

    img = np.zeros((1080, 1920, 4), dtype=np.uint8)

    vidcap = cv2.VideoCapture('planes.mp4')
    success, image = vidcap.read()

    video_frame = ndi.VideoFrameV2()

    video_frame.data = img
    video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX
    # print(cv2.cvtColor(image, cv2.COLOR_RGB2BGRA))
    print(img.shape, cv2.cvtColor(image, cv2.COLOR_RGB2BGRA).shape)

    start = time.time()
    while time.time() - start < 60 * 5:
        print(success)
        start_send = time.time()

        for idx in reversed(range(200)):
            print(idx)
            success, image = vidcap.read()
            img = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
            # video_frame.data = img
            ndi.send_send_video_v2(ndi_send, video_frame)
            print('\t', idx)

        print('200 frames sent, at %1.2ffps' % (200.0 / (time.time() - start_send)))

    ndi.send_destroy(ndi_send)

    ndi.destroy()
    print('FINISHED')
    return 0

if __name__ == "__main__":
    sys.exit(main())
