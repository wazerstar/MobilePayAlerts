from os import getppid
from psutil import Process
import asyncio, requests, websockets, json
import configurator

log = configurator.LOG.get()
cfg = configurator.CFG().load("settings.json")

class Alerts():
	def __init__(self):

		self.parent_id = getppid()
		self.parent_exe = Process(self.parent_id).name()

		log.info(f"{self.parent_exe} process id: {self.parent_id}")
		print(f"{self.parent_exe} process id: {self.parent_id}")

	def startReceiving(self):
		self.async_alert_event = asyncio.get_event_loop().run_until_complete(self.notifications())

	def stopReceiving(self):
		log.info("Stopping loop")
		try:
			asyncio.get_running_loop().close()
		except RuntimeError:
			pass

	async def notifications(self):
		log.info("Connecting to Pushbullet WSS stream")
		async with websockets.connect(f"wss://stream.pushbullet.com/websocket/{cfg['pb_token']}") as websocket:
			while True:
				data = await websocket.recv()

				log.info(f"Received data: {data}")
				print(f"Received data: {data}")

				if Process(self.parent_id).name() != self.parent_exe:
					print(f"CLOSING {self.parent_id.name()}, {self.parent_exe}")
					log.error("Parent process isn't available, closing self")
					self.stopReceiving()

				if "push" and "application_name" in data:
					self.handleData(data)

	def handleData(self, data):
		json_data = json.loads(data)

		name, msg, amount = "", "", ""

		if json_data["push"]["application_name"] == "MobilePay" or json_data["push"]["title"] == "MobilePay":
			log.info("Received donation!")
			log.info(f"Raw data: {json_data}")

			log.info("Splitting donation data")
			body = json_data["push"]["body"]
			body = body.split()

			# Amount
			log.info("Getting donation amount")
			amount = body[3]
			amount = amount.replace(",", ".", 1)

			# Name
			log.info("Getting donation name")
			if body[7] == "billede":
				name = body[9][1:]
			else:
				name = body[6][1:]

			name = name.strip()

			# Message
			log.info("Getting donation message")
			for i in range(len(body)):
				if ":" in body[i]:
					msg = body[i+1:]
					msg = " ".join(msg)
					break
				else:
					msg = ""

			log.info(f"Donation data: {name} - {amount} - \"{msg}\"")

		elif json_data["push"]["title"] == "Test notification" and json_data["push"]["application_name"].lower() == "pushbullet":
			log.info("Received test notification via the Pushbullet API")
			print("Received test notification via the Pushbullet API")

		else:
			log.info(f"Unknown data received: {json_data}")

		if name.strip() == "":
			name = cfg["default_name"]

		if msg.strip() == "":
			msg = cfg["default_msg"]

		if amount.strip() == "":
			amount = None
		else:
			log.info("Triggering donation alert")
			self.triggerAlert(name, msg, amount)

	def triggerAlert(self, name, msg, amount):
		url = "https://streamlabs.com/api/v1.0/donations"

		data = {
			"access_token"	:cfg["sl_token"],
			"name"			:name,
			"identifier"	:"MobilePay",
			"amount"		:amount,
			"currency"		:"DKK",
			"message"		:msg,
		}

		self.request(url, data)

	def testAlert(self):
		url = "https://streamlabs.com/api/v1.0/alerts/send_test_alert"

		data = {
			"access_token":cfg['sl_token'],
			"type":"donation",
		}

		self.request(url, data)

	def request(self, url, data):
		log.info("Alert request has been sent!")
		response = requests.post(url, data)

		print(f"Alert request returned: \"{response.text}\"")
		log.info(f"Alert request returned: \"{response.text}\"")
