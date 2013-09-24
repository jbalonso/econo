from setuptools import setup, find_packages
import sys

setup(
    name="econo",
    version = '0.1',
    maintainer='Jason B. Alonso',
    maintainer_email='jalonso@hackorp.com',
    license = "MIT",
    url = 'http://github.com/jbalonso/econo',
    platforms = ["any"],
    description = "Zero-forecast economic simulation",
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['econo = econo.cli:main',
             ]}
)
