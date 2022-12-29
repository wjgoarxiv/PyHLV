from setuptools import setup
setup(
	  name='PyHLV', 
	  version='1.2.4',  
	  description='::A simple phase EQ extractor for gas hydrate researchers::',
	  long_description= 'Revised some minor errors...', 
	  author='wjgo-unist',
	  author_email='woo_go@yahoo.com',
	  url='https://pypi.org/project/PyHLV/',
	  license='MIT',
	 	py_modules=['PyHLV'],
	  python_requires='>=3.8', #python version required
	  install_requires = [
	  'pandas',
	  'numpy',
	  'matplotlib',
	  'seaborn',
	  'ruptures',
	  'tabulate',
	  'pyfiglet',
		'argparse'
	  ],
	  packages=['PyHLV'],
		entry_points={
			'console_scripts': [
				'pyhlv = PyHLV.__main__:main'
			]
		}
	)
