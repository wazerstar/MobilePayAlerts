from os import system
import json
import PySimpleGUIQt as sg
import configurator, authentication, alerts, qr #, window

log = configurator.LOG.get()
cfg = configurator.CFG().load("settings.json")

lang = configurator.CFG().load("language.json")
text = configurator.CFG().load("language.json")[cfg["language"].lower()]
for key, value in lang["common"].items():
	text[key] = value

class GUI():
	def __init__(self):
		self.WINDOW_TITLE = "MobilePayAlerts"

		self.event_combiner = {
			"_BTN_RESET_": Main.resetConfig,
			"_BTN_SETUP_": Main.setup,
			"_BTN_GENQR_": qr.generate
		}

		tab_1 = sg.Tab(text["tab_1"]["text"], 
				   	[[sg.HorizontalSeparator()],
				   	 [sg.Button("Start", key="_BTN_START_", size=(250, 40), visible=True)],
				   	 [sg.HorizontalSeparator()],
					 [sg.Button("Stop",  key="_BTN_STOP_", 	size=(250, 40), visible=False)],
					 [sg.HorizontalSeparator()],
					 [sg.Button("Test",  key="_BTN_TEST_", 	size=(250, 40), visible=True)],
					 [sg.HorizontalSeparator()]
					])

		tab_2 = sg.Tab(text["tab_2"]["text"], 
					[[sg.Text(text["label_settings"]["text"], font=("def", "def", "bold"))],
					 [sg.Text(text["label_name"]["text"], size=(11, 0.6)), sg.InputText(default_text=cfg["default_name"], key=text["input_name"]["key"], do_not_clear=True, tooltip=text["input_name"]["tt"])],
					 [sg.Text(text["label_msg"]["text"],  size=(11, 0.6)), sg.InputText(default_text=cfg["default_msg"],  key=text["input_msg"]["key"],  do_not_clear=True, tooltip=text["input_msg"]["tt"])],
					 [sg.Text(text["label_lang"]["text"], size=(11, 0.6)), sg.InputCombo(text["languages"], key=text["combobox"]["key"], default_value=cfg["language"].capitalize())],
					 [sg.Button(text["btn_save"]["text"], key=text["btn_save"]["key"], tooltip=text["btn_save"]["tt"])],
							 
					 [sg.HorizontalSeparator()],

					 [sg.Button(text["btn_generate"]["text"], key=text["btn_generate"]["key"], tooltip=text["btn_generate"]["tt"])],

					 [sg.HorizontalSeparator()],
							
					 [sg.Text(text["label_other_settings"]["text"], font=("def", "def", "bold"))],
					 [sg.Button(text["btn_reset"]["text"], key=text["btn_reset"]["key"]), sg.Button(text["btn_setup"]["text"], key=text["btn_setup"]["text"])],
					])

		self.layout = [[sg.TabGroup([[tab_1, tab_2]])]]

	def main(self):
		window = sg.Window(self.WINDOW_TITLE, size=(250, 250)).Layout(self.layout)

		print(window)

		while True:
			event, values = window.Read()
			if event is None or event == "Exit":
				break

			if event == "_BTN_START_":
				alerts.Alerts().startReceiving
				window.FindElement(event).Update(visible=False)
				window.FindElement("_BTN_STOP_").Update(visible=True)
			
			elif event == "_BTN_STOP_":
				alerts.Alerts.stopReceiving
				window.FindElement("_BTN_STOP_").Update(visible=False)
				window.FindElement("_BTN_START_").Update(visible=True)

			elif event == "_BTN_TEST_":
				window.FindElement("_BTN_TEST_").Update(visible=False)
				alerts.Alerts.testAlert
				window.FindElement("_BTN_TEST_").Update(visible=True)

			elif event in self.event_combiner:
				self.event_combiner[event]()

			print(event, values)

		window.Close()

	def setup(self):
		sg.PopupOK("Opsætning", "Opsætning er krævet")

	def save(self, values):
		cfg["language"] 	= values["_COMBO_LANG_"]
		cfg["default_name"] = values["_INPUT_NAME_"]
		cfg["default_msg"]  = values["_INPUT_MSG_"]
		configurator.CFG().save("settings.json", cfg)


class Main():
	def __init__(self):
		log.info("\n")

		if cfg["pb_token"] == "" or cfg["sl_token"] == "":
			gui.setup()

			self.setup()
		else:
			GUI().main()

	def setup(self):
		log.info("Starting setup!")
		authentication.runServer()
		
		log.info("Setup done!")
		GUI().main()

	def resetConfig(self):
		log.info("Resetting config!")
		configurator.CFG().reset("settings.json")

Main()