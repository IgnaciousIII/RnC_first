import cv2
import numpy as np
import serial
import pyaudio

# Open the serial port for communication with Arduino
ser = serial.Serial('COM4', 9600)  # Replace 'COM4' with the appropriate port for your Arduino

# Initialize the video capture object
cap = cv2.VideoCapture(0)  # 0 for the default camera

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Initialize PyAudio for audio capture
audio = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Set the desired threshold for sound detection
threshold_sound = 10 # Adjust this value as needed
threshold_motion = 900  # Adjust this value as needed

ret, frame1 = cap.read()
ret, frame2 = cap.read()


def motionDetect():
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(
        dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


while cap.isOpened():  # Loop as long as the camera is opened
    ret, frame = cap.read()

    if not ret:
        print("Error: Unable to read frame.")
        break

    # Read audio data from the microphone
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

    # Calculate the average amplitude of the audio data
    avg_amp = np.mean(np.abs(audio_data))

    # Check if the average amplitude exceeds the threshold for sound detection
    if avg_amp > threshold_sound:
        # Send a signal to Arduino to turn on the sound LED
        ser.write(b'2')
    else:
        # Send a signal to Arduino to turn off the sound LED
        ser.write(b'3')

    # Motion detection
    contours = motionDetect()

    if contours:
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < threshold_motion:
                continue
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        if motion_detected:
            ser.write(b'1')  # Motion detected, turn motion LED on
        else:
            ser.write(b'0')  # No motion detected, turn motion LED off
    else:
        ser.write(b'0')  # No motion detected, turn motion LED off

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) == ord('x'):
        break

    frame1 = frame2
    ret, frame2 = cap.read()x

# Release the resources
cap.release()
cv2.destroyAllWindows()
ser.close()
audio.terminate()