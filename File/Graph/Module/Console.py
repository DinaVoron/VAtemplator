# -*- КОНСОЛЬ | Console -*- #
import sys

class Console:
	def LogMessagePart(operation, text):
		if operation:
			string = operation + ": " + text
			sys.stdout.write(f"\033[3m\033[5m\033[37m{string}\033[0m\033[37m\r")
			sys.stdout.flush()
		else:
			sys.stdout.write(f"\033[3m\033[5m\033[37m{text}\033[0m\033[37m\r")
			sys.stdout.flush()

	def LogMessage(operation, text):
		if operation:
			print("\033[3m\033[37m{}".format(operation + ": " + text)             + "\033[0m\033[37m")
		else:
			print("\033[3m\033[37m{}".format(text)                                + "\033[0m\033[37m")



	def LogInfo( operation, text):
		if operation:
			print("\033[34m{}".format("INFO:: " + operation + ": " + text) + "\033[0m\033[37m")
		else:
			print("\033[34m{}".format("INFO:: " + text)                    + "\033[0m\033[37m")

	def LogWarn( operation, text):
		if operation:
			print("\033[33m{}".format("WARN:: " + operation + ": " + text) + "\033[0m\033[37m")
		else:
			print("\033[33m{}".format("WARN:: " + text)                    + "\033[0m\033[37m")

	def LogError(operation, text):
		if operation:
			print("\033[31m{}".format("ERROR::" + operation + ": " + text) + "\033[0m\033[37m")
		else:
			print("\033[31m{}".format("ERROR::" + text)                    + "\033[0m\033[37m")