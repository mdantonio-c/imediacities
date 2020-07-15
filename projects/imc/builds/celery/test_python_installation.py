import os
import sys
import urllib.request

import cv2
import numpy as np

__author__ = "Christian Weigel"
__copyright__ = "Fraunhofer IDMT"
__doc__ = "short script checking if python and system installation suits IMC needs"

if __name__ == "__main__":
    assert sys.version_info >= (3, 4)
    assert sys.version_info < (3, 6)

    video_testfile_path = os.path.join(
        os.path.abspath(os.path.curdir), "SampleVideo_640x360_1mb.mp4"
    )
    img01_testfile_path = os.path.join(os.path.abspath(os.path.curdir), "img_01.png")
    img02_testfile_path = os.path.join(os.path.abspath(os.path.curdir), "img_01.jpg")

    if not os.path.exists(video_testfile_path):
        # try downloading testdata
        response = urllib.request.urlopen(
            "https://seafile.idmt.fraunhofer.de/f/4d62eed6de/?raw=1"
        )
        with open(video_testfile_path, "wb") as output:
            output.write(response.read())

    if not os.path.exists(video_testfile_path):
        raise RuntimeError("Could not run test - missing sample video.")

    # check capture capabilities
    cap = cv2.VideoCapture(video_testfile_path)

    if not os.path.exists("SampleVideo_640x360_1mb.mp4"):
        raise RuntimeError("Could not run test - missing sample video.")

    if not cap.isOpened():
        raise RuntimeError(
            "Could open capture device - OpenCV might not have been compiled with FFMPEG support!"
        )
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if frame is not None:
            assert frame.shape == (368, 640, 3)
            frame_count += 1
        else:
            break

        if frame_count == 100:
            cv2.imwrite(img01_testfile_path, frame)
        if frame_count == 120:
            cv2.imwrite(img02_testfile_path, frame)

    cap.release()
    assert frame_count == 160

    # check contrib package - i.e. do SIFT matching
    img_01 = cv2.imread(img01_testfile_path)
    rows, cols, chans = img_01.shape
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 25, 1.1)
    img_01 = cv2.warpAffine(img_01, M, (cols, rows))
    img_02 = cv2.imread(img02_testfile_path)
    gray_01 = cv2.cvtColor(img_01, cv2.COLOR_BGR2GRAY)
    gray_02 = cv2.cvtColor(img_02, cv2.COLOR_BGR2GRAY)

    sift = cv2.xfeatures2d.SIFT_create()

    kp_01, desc_01 = sift.detectAndCompute(gray_01, None)
    kp_02, desc_02 = sift.detectAndCompute(gray_02, None)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(desc_01, desc_02, k=2)
    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    print("Successfully ran test script!")
