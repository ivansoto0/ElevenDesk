from elevendesk.app import ElevenDeskApp
from elevendesk import constants


def main():
	application = ElevenDeskApp(False)
	application.MainLoop()


if __name__ == constants.MAIN_MODULE_NAME:
	main()
