from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
	name='FEcluster',
	version='0.0',
	description='Distribute FE simulation tasks across multiple computers via SSH.',
    long_description=long_description,
    url='',
    license='',
	author='Qilong Liu',
	author_email='qilong-kirov.liu@outlook.com',
	packages=['FEcluster'],
	install_requires=[
		'paramiko',
        'pyyaml',
        'numpy',
	],
)