#!/home/pi/scripts/PyControl/venvpycontrol/bin/python
import grp
import os
import pwd
import logging
from button import *
import time
import datetime
import socket
import requests
from signal import signal, SIGINT, SIGTERM
import sys
import paramiko

hostIP = "0.0.0.0"
VMname = "MY_VM_NAME"


def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root, we are going to need that to continue.
        return
    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid
    # Reset group access list
    os.initgroups(uid_name, running_gid)
    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)
    # Ensure a very conservative umask
    old_umask = os.umask(077)


def get_shutdown_handler(message=None):
    """
    Build a shutdown handler, called from the signal methods
    :param message:
        The message to show on the second line of the LCD, if any. Defaults to None
    """
    def handler(signum, frame):
        print(message)
        exit(0)
    return handler


def funcPrintConsole(str):
    print(str)


def funcWriteLog(logtext):
    f= open("PyControlLog.txt","a+")
    f.write(logtext)
    f.close()


def execute_command_readlines(address, usr, pwd, command):
        try:
            print("ssh " + usr + "@" + address + ", running : " +
                         command)
            client = paramiko.SSHClient()
            client.load_system_host_keys()

            client.connect(address, username=usr, password=pwd)
            _, ss_stdout, ss_stderr = client.exec_command(command)
            r_out, r_err = ss_stdout.readlines(), ss_stderr.read()
            print(r_err)
            if len(r_err) > 5:
                print(r_err)
            else:
                print(r_out)
            client.close()
        except IOError:
            print(".. host " + address + " is not up")
            return "host not up", "host not up"

        #return r_out, r_err 


def funcWHb1():
    #btn1_push
    global hostIP
    global VMname
    execute_command_readlines("hostIP", "root", "", "virsh attach-device VMname --file /mnt/user/appdata/usbmonitor/usb_device_01.xml")
    funcWriteLog("Button 1 - SSH Command initiated\n")


def funcWHb2():
    #btn2_push - IFTTT example
    requests.post("https://maker.ifttt.com/trigger/btn2_push/with/key/<API-KEY-GOES-HERE>")
    funcWriteLog("Button 2 - Webhook initiated\n")


signal(SIGINT, get_shutdown_handler('SIGINT received'))
signal(SIGTERM, get_shutdown_handler('SIGTERM received'))

b1 = Button(18)
b2 = Button(24)

drop_privileges(uid_name='pi', gid_name='pi')

while True:
        if b1.is_pressed():
            funcPrintConsole("Button 1 Pushed!")
            funcWHb1()
            time.sleep(2)

        if b2.is_pressed():
            funcPrintConsole("Button 2 Pushed!")
            time.sleep(2)