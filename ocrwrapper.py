import subprocess

class OcrWrapper:

	def __init__(self, script):
		self.script = script

	def doOcr(self, filepath):
		return subprocess.check_output([self.script,filepath])
