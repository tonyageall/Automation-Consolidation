# setup.py
from setuptools import setup, find_packages

setup(
    name='PfastFeas',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
	'numpy',
	'matplotlib',
	'seaborn',
	'neo4j',
	'datetime',
    'biopython'
    ]
)
