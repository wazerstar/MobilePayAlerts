from os import system
import json
import configurator, authentication, alerts

log = configurator.LOG.get()
cfg = configurator.CFG().load("settings.json")

class Main():
	def __init__(self):
		log.info("\n")

		if cfg["pb_token"] == "" or cfg["sl_token"] == "":
			input("Press ENTER to start setup")
			self.setup()
		else:
			self.menu()

	def menu(self):
		system("cls || clear")
		log.info("[Menu]")

		print("[Main]")
		print(" [1] Start")
		print(" [2] Stop")
		print(" [3] Test\n")

		print("[Settings]")
		print(" [4] Reset settings.json (Includes authentication tokens)")
		print(" [5] Re-do account authentication")

		try:
			choice = int(input("\nChoice: "))
		except ValueError as err:
			log.error(err)
			self.menu()

		options = {
			1: alerts.Alerts().startReceiving,
			2: alerts.Alerts().stopReceiving,
			3: alerts.Alerts().testAlert,
			4: self.resetConfig,
			5: self.setup,
		}

		if choice > 0 and choice <= len(options):
			options[choice]()
			self.menu()
		else:
			log.error(f"No valid option was chosen!")
			self.menu()

	def setup(self):
		log.info("Starting setup!")
		authentication.runServer()
		
		log.info("Setup done!")
		self.menu()

	def resetConfig(self):
		log.info("Resetting config!")
		configurator.CFG().reset("settings.json")

	def alerts(self, instruction):
		options = {
			"start"	:ReceiveAPI,
			"stop"	:StopAPI,
			"test"	:TestAPI
		}

		if instruction in options:
			log.info(f"{instruction}ing alert(s)!")
			options[instruction]()
		else:
			log.error("No valid option was chosen!")
			self.menu()

Main()