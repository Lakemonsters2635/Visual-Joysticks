import pyvjoy
import time
import winsound

j = pyvjoy.VJoyDevice(1)


def BeepAndWait(freq, dur):
    winsound.Beep(freq, dur)
    time.sleep(0.25)


def SweepAxis(vj, axis, start, end, inc, delay):
    stop = end + 1
    if inc < 0:
        stop = end - 1
    for ii in range(start, stop, inc):
        vj.set_axis(axis, ii)
        time.sleep(delay)
    BeepAndWait(440, 100)


while True:
    for i in range(1, 9):
        j.set_button(i, 1)
        BeepAndWait(440, 100)
        time.sleep(0.25)

    for i in range(1, 9):
        j.set_button(i, 0)
        BeepAndWait(440, 100)
        time.sleep(0.25)

    SweepAxis(j, pyvjoy.HID_USAGE_X, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_X, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_Y, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_Y, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_Z, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_Z, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RX, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RX, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RY, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RY, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RZ, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_RZ, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_SL0, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_SL0, 0x8000, 0x0, -2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_SL1, 0x0, 0x8000, 2048, 0.025)
    SweepAxis(j, pyvjoy.HID_USAGE_SL1, 0x8000, 0x0, -2048, 0.025)

    BeepAndWait(220, 500)
