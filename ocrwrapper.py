import subprocess
import logging

class OcrWrapper:

	def __init__(self, script):
		self.script = script
		self.logger = logging.getLogger('nxpush')

	def doOcr(self, filepath):
		self.logger.debug('path: %s ' %filepath)
		out = subprocess.check_output([self.script,filepath])
		self.logger.debug('out: %s ' %out)
		return out
