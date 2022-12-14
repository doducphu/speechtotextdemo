import serial
import time
from threading import Thread
from pynput.keyboard import Key, Listener
from pynput.keyboard import KeyCode
# 390  Open
# 375  Close
# KeyCode.from_char('w'):

# Serial port (need to be precised)

s = serial.Serial('COM9')


# Send signal to arduino
def send(port, sig=""):
    out = (str(port) + str(sig)).replace("\r\n", "")
    print(out)
    s.write(bytes(out, "ascii"))


# Print out output from serial
def watch():
    while True:
        print(s.readline())


# Default positions for all servos
lr_ang = 93
up_ang = 93
fw_ang = 93
oc_ang = 93

lr_str = 15
up_str = 20
fw_str = 20


# Rotate
def rotate(key):
    global lr_ang
    global lr_str
    # Rotation Servo
    if (key == KeyCode.from_char('h') and lr_ang + lr_str <= 120):
        lr_ang += lr_str
        send(2, lr_ang)
        return True
    elif (key == KeyCode.from_char('k') and lr_ang - lr_str >= 0):
        lr_ang -= lr_str
        send(2, lr_ang)
    else:
        return False


# Grab and release
def grab(key):
    global oc_ang
    # Grab servo
    if (key == KeyCode.from_char('d')):
        oc_ang = 90
        send(3, oc_ang)
        return True
    elif (key == KeyCode.from_char('x')):
        oc_ang = 75
        send(3, oc_ang)
        return True
    else:
        return False


# Up and down
def updown(key):
    global up_ang
    global up_str
    # Up down Servo 1
    if (key == KeyCode.from_char('u') and up_ang + up_str <= 150):
        up_ang += up_str
        send(4, up_ang)
        return True
    elif (key == KeyCode.from_char('j') and up_ang - up_str >= 0):
        up_ang -= up_str
        send(4, up_ang)
        return True
    else:
        return False


# Forward and backward
def forback(key):
    global fw_ang
    global fw_str
    # Up down Servo 2
    if (key == KeyCode.from_char('w') and fw_ang + fw_str <= 150):
        fw_ang += fw_str
        send(5, fw_ang)
        return True
    elif (key == KeyCode.from_char('s') and fw_ang - fw_str >= 0):
        fw_ang -= fw_str
        send(5, fw_ang)
        return True
    else:
        return False


# Reset to default position
def reset_default(key):
    global lr_ang
    global lr_str
    global up_ang
    global up_str
    global fw_ang
    global fw_str
    # Reset all servo
    if (key == KeyCode.from_char('q')):
        lr_ang = 110
        send(2, lr_ang)
        # time.sleep(2)
        # send(3, 90)
        time.sleep(2)
        up_ang = 40
        fw_ang = 30
        send(5, fw_ang)
        time.sleep(2)
        send(4, up_ang)
        return True
    else:
        return False


# Reset to power position
def reset_power(key):
    global lr_ang
    global lr_str
    global up_ang
    global up_str
    global fw_ang
    global fw_str
    # Set rotate servo to center
    if (key == KeyCode.from_char('a')):
        lr_ang = 93
        send(2, lr_ang)
        time.sleep(2)
        send(3, 93)
        time.sleep(2)
        up_ang = 93
        fw_ang = 93
        send(5, fw_ang)
        time.sleep(2)
        send(4, up_ang)
        return True
    else:
        return False


# Turn to center
def center(key):
    global lr_ang
    # Set rotate servo to center
    if (key == KeyCode.from_char('f')):
        lr_ang = 48
        send(2, lr_ang)
        return True
    else:
        return False


def go_grab(key):
    if (key == KeyCode.from_char('y')):
        send(10)

        return True


def retrack(key):
    global lr_ang
    global lr_str
    global up_ang
    global up_str
    global fw_ang
    global fw_str
    if (key == KeyCode.from_char('i')):
        fw_ang = 30
        up_ang = 40
        send(5, fw_ang)
        time.sleep(2)
        send(4, up_ang)
        return True
    else:
        return False


manual_scan = False


def m_scan():
    global lr_ang
    global lr_str
    global up_ang
    global up_str
    global fw_ang
    global fw_str
    global oc_ang
    global manual_interrupt
    global manual_scan

    while True:
        if (manual_scan):
            lr_ang = 90
            send(2, lr_ang)
            time.sleep(2)
            retrack(KeyCode.from_char('i'))
            while manual_scan and lr_ang > 0:
                time.sleep(1.5)
                lr_ang -= 10
                send(2, lr_ang)
        else:
            time.sleep(1)


def manual(key):
    global manual_scan
    if (key == KeyCode.from_char("o")):
        if (manual_scan):
            manual_scan = False
        else:
            manual_scan = True
        return True
    else:
        return False


# Handle control from serial/voice
def handle_press(key):
    if not rotate(key):
        if not grab(key):
            if not updown(key):
                if not forback(key):
                    if not reset_default(key):
                        if not reset_power(key):
                            if not go_grab(key):
                                if not center(key):
                                    if not retrack(key):
                                        manual(key)
    print(key)


# Dictionaries for controls
# Left
left_dict = ("left", "bless", "less")
# Right
right_dict = ("right", "rise", "rice")
# Backward
backward_dict = ("back", "mac", "mike", "beck", "but")
# Forward
forward_dict = ("front", "from", "forward", "face", "place", "want", "rice", "out")
# Turn strength small
lr_str_small = ("small")
# Turn strength big
lr_str_big = ("big", "mick")
# Close
grab_dict = ("close", "klaus", "crap", "grab", "cloth")
# Open
release_dict = ("open", "release")
# Up
up_dict = ("up", "yup")
# Down
down_dict = ("down", "now", "wow", "dow")
# Auto
scan_dict = ("auto", "scan", "alto", "scam", "scout")
# Stop
stop_dict = ("stop", "top", "sob", "sorrow", "shop")
# Look
look_dict = ("look", "luke")
# Manual
manual_dict = ("manual", "meanwhile", "manila")
# Reach
reach_dict = ("reach", "rich", "rick", "risk")
# Retract
retract_dict = ("retract", "retrack")


# Handle voice commands
def handle_voice(voice):
    global lr_str
    global manual_scan
    global lr_ang
    if (voice in lr_str_small):
        lr_str = 5
        print("Changed rotation speed to " + str(lr_str))
        return True
    elif (voice in lr_str_big):
        lr_str = 15
        print("Changed rotation speed to " + str(lr_str))
        return True

    if (voice in left_dict):
        rotate(KeyCode.from_char('h'))
        return True
    elif (voice in right_dict):
        rotate(KeyCode.from_char('k'))
        return True

    if (voice in grab_dict):
        grab(KeyCode.from_char('x'))
        return True
    elif (voice in release_dict):
        grab(KeyCode.from_char('d'))
        return True

    if (voice in up_dict):
        updown(KeyCode.from_char('u'))
        return True
    elif (voice in down_dict):
        updown(KeyCode.from_char('j'))
        return True

    if (voice in forward_dict):
        # updown(KeyCode.from_char(‘u’) )
        # time.sleep(1)
        forback(KeyCode.from_char('w'))
        return True

    elif (voice in backward_dict):
        # updown(KeyCode.from_char(‘j’) )
        # time.sleep(1)
        forback(KeyCode.from_char('s'))
        return True

    elif (voice in scan_dict):
        send(7, "")
        return True

    elif (voice in stop_dict):
        if not manual_scan:
            send(8, "")
        else:
            manual_scan = False
            lr_ang = lr_ang + 20
            send(2, lr_ang)
        return True

    elif (voice in look_dict):
        send(9, "")
        return True

    elif ("reset" == voice):
        reset_power(KeyCode.from_char('a'))
        return True

    elif ("default" == voice):
        reset_default(KeyCode.from_char('q'))
        return True

    elif (voice == "center"):
        center(KeyCode.from_char('f'))
        return True

    elif (voice in manual_dict):
        manual(KeyCode.from_char('o'))
        return True

    elif (voice in reach_dict):
        go_grab(KeyCode.from_char('y'))

    elif (voice in retract_dict):
        retrack(KeyCode.from_char('i'))


# Handle control from serial
def run_control():
    with Listener(on_release=handle_press) as listener:
        listener.join()


# Main program
def main(watched=True):
    if (watched):
        t = Thread(target=watch)
        inp = Thread(target=run_control)
        sca = Thread(target=m_scan)
        t.start()
        inp.start()
        sca.start()