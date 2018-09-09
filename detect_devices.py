import subprocess
import re
import time
import paho.mqtt.client as mqtt


def get_associated():
	#print("Fetching")
	macs = []
	for interface in ["wlan0", "wlan1"]:
		cmd = subprocess.Popen('iw dev ' + interface + ' station dump', shell=True, stdout=subprocess.PIPE)
		for line in cmd.stdout:
			line = bytes(line).decode("utf-8") 
			if "Station" in line:
				line = line.strip()
				m = re.search('Station ([0-9a-f:]+) \(on wlan.\)', line)
				if m != None:
					macs.append(m.group(1).replace(":", ""))
	return macs


client = mqtt.Client()
client.username_pw_set("mqtt_username", "mqtt_password")
client.connect("127.0.0.1", 1883, 60)
macs = []
last_check = 0
while True:
	if time.time() - last_check > 1.0:
		last_check = time.time()
		new_macs = get_associated()
		for m in new_macs:
			if m not in macs:
				client.publish("device_track/" + m, "home")
				print("Added %s" % m)
		for m in macs:
			if m not in new_macs:
				client.publish("device_track/" + m, "not_home")
				print("Removed %s" % m)
		macs = new_macs
	client.loop()
