from setuptools import setup, find_packages
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name="PiGro",
    version="0.2.1.1",
    packages=find_packages(),
    scripts=[],
    setup_requires=['wheel'],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["PyYAML","adafruit-circuitpython-dht","w1thermsensor","ephem","geopy","gpiod","adafruit-circuitpython-pca9685","PCA9685-driver"],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.py", "*.yaml", "*.txt"],
    },

    # metadata to display on PyPI
    author="Daniel Sebastian Wienzek",
    author_email="wienzek.daniel@gmail.com",
    description="Raspberry Pi driven horticulture",
    keywords="horticulture grow pwm control temperature humidity",
    url="https://github.com/dawigit/pigroprometheus",   # project home page, if any
    project_urls={
        "Source Code": "https://github.com/dawigit/pigroprometheus",
    },
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License"
    ],
    
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6'

    # could also include long_description, download_url, etc.
)
