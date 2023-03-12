import random
import time
import matplotlib.pyplot as plt
import numpy as num
import pyaudio
import sys
import aubio
import audioop

fig = plt.figure(facecolor='lightgrey')
ax = fig.add_subplot(1, 1, 1)
heart_rate = [random.randint(60, 80) for _ in range(5)]
num_seconds = 6000
patient = ["Name: Alice - Age: 12", "Name: David - Age 27", "Name: Jackson - Age: 19", "Name: Betty - Age: 62",
           "Name: Bob - Age: 38"]

BUFFER_SIZE = 2048
CHANNELS = 1
FORMAT = pyaudio.paFloat32
METHOD = "default"
SAMPLE_RATE = 44100
HOP_SIZE = BUFFER_SIZE // 2
PERIOD_SIZE_IN_FRAME = HOP_SIZE
Volume = 0

pA = pyaudio.PyAudio()
# Open the microphone stream.
mic = pA.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True, frames_per_buffer=PERIOD_SIZE_IN_FRAME)
# Initiating Aubio's pitch detection object.
pDetection = aubio.pitch(METHOD, BUFFER_SIZE, HOP_SIZE, SAMPLE_RATE)
# Set unit.
pDetection.set_unit("Hz")
# Frequency under -40 dB will considered
# as a silence.
pDetection.set_silence(-40)

# minimum = 0
# maximum = 10000
patientNumber = input("Enter the number of the patient you wish to simulate:"
                      "\n 1: Alice"
                      "\n 2: David"
                      "\n 3: Jackson"
                      "\n 4: Betty"
                      "\n 5: Bob ")
if patientNumber == "1":
    minimum = 64
    maximum = 95
if patientNumber == "2":
    minimum = 55
    maximum = 90
if patientNumber == "3":
    minimum = 50
    maximum = 90
if patientNumber == "4":
    minimum = 63
    maximum = 95
if patientNumber == "5":
    minimum = 60
    maximum = 90
title = "Heart Rate Monitor For " + patient[int(patientNumber) - 1]
# plot the initial data
ax.set_title(title, fontsize=20)
ax.set_xlabel('Time (s)', fontsize=14)
ax.set_ylabel('BPM', fontsize=14)
line, = ax.plot(range(len(heart_rate)), heart_rate, color='green')
ax.set_xlim(0, num_seconds)
ax.set_ylim(50, 110)
ax.set_yticks(range(50, 111, 10))
# initialize max, min, and average values
max_rate = 0
min_rate = 10000
average_rate = 0
status = "Normal"
# add annotations for max, min, and average values
max_text = ax.text(0.1, 0.9, f"Peak: {max_rate}", transform=ax.transAxes, fontsize=14)
min_text = ax.text(0.1, 0.85, f"Low: {min_rate}", transform=ax.transAxes, fontsize=14)
average_text = ax.text(0.1, 0.8, f"Average: {average_rate}", transform=ax.transAxes, fontsize=14)
status_text = ax.text(0.1, 0.75, f"Status: {status}", transform=ax.transAxes, fontsize=14)
plt.show(block=False)
manager = plt.get_current_fig_manager()
#try:
    #manager.full_screen_toggle()
#except AttributeError:
    #manager.window.state('zoomed')
rate = (minimum + maximum) / 2
lastFive = [0, 0, 0, 0, 0]
SMA5 = (lastFive[0] + lastFive[1] + lastFive[2] + lastFive[3] + lastFive[4]) / 5
counter = 0
patientMin = 100000
patientMax = 0

for i in range(num_seconds):
    data = mic.read(PERIOD_SIZE_IN_FRAME)
    samples = num.fromstring(data, dtype=aubio.float_type)

    # Compute the energy (volume)
    # of the current frame.
    volume = num.sum(samples ** 2) / len(samples)
    # Format the volume output so it only
    # displays at most six numbers behind 0.
    volume = "{:6f}".format(volume)
    if float(volume) > 0.000050:
        rate = rate + 5
    # Finally print the pitch and the volume.
    print(str(volume))
    # generate a random heart rate value between 60 and 100 BPM
    rate = random.randint(int(rate) - 4, int(rate) + 2)
    if rate < minimum:
        rate = minimum
    if rate > maximum:
        rate = maximum
    if rate < patientMin:
        patientMin = rate
    if rate > patientMax:
        patientMax = rate
    lastFive[counter % 5] = rate
    counter = counter + 1
    SMA5 = (lastFive[0] + lastFive[1] + lastFive[2] + lastFive[3] + lastFive[4]) / 5
    print(SMA5)
    if SMA5 < 70:
        status = "Good"
    if 83 > SMA5 > 70:
        status = "Normal"
    if SMA5 > 83:
        status = "Bad"
    # update max, min, and average values
    if rate > max_rate:
        max_rate = rate
        max_text.set_text(f"Peak: {max_rate}")
    if rate < min_rate:
        min_rate = rate
        min_text.set_text(f"Low: {min_rate}")
    heart_rate.append(rate)
    average_rate = sum(heart_rate) / len(heart_rate)
    average_text.set_text(f"Average: {average_rate:.2f}")
    min_text.set_text(f"Minimum: {patientMin:.2f}")
    max_text.set_text(f"Maximum: {patientMax:.2f}")
    status_text.set_text(f"Status: {status}")


    # update the plot
    line.set_data(range(len(heart_rate)), heart_rate)
    ax.relim()
    ax.autoscale_view()
    ax.set_xlim(max(0, i - 55), i + 0)
    ax.set_ylim(50, 110)
    fig.canvas.draw()
    fig.canvas.flush_events()
    # wait for 1 second before generating the next value
    time.sleep(0.01)
    # print(status)
