#!/usr/bin/env python

import configparser
import os
import setuptools

with open("README.md", "r") as rf:
    long_description = rf.read()

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "chord_notification_service", "package.cfg"))

setuptools.setup(
    name=config["package"]["name"],
    version=config["package"]["name"],

    python_requires=">=3.6",
    install_requires=[
        "chord_lib[flask]==0.8.0",
        "Flask>=1.1,<2.0",
        "SQLAlchemy>=1.3,<1.4",
        "Flask-SQLAlchemy>=2.4,<3.0",
        "Flask-Migrate>=2.5,<3.0"
    ],

    author=config["package"]["authors"],
    author_email=config["package"]["author_emails"],

    description="A notification service for the CHORD project.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    include_package_data=True,

    url="https://github.com/c3g/chord_notification_service",
    license="LGPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent"
    ]
)
