from setuptools import setup

setup(
	name = 'msicontroller',
	version = '0.1',
	description = 'Python control script for MSI r-one exhibit',
	url = 'http://github.com/zkingston/msicontroller',
	author = 'zkk',
	license = 'MIT',
	packages = ['msicontroller'],
	install_requires = [
		'pyusb',
		'pyserial'
	],
	zip_safe = False
)
