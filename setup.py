# Copyright (c) 2020-2025 JupiterOne
from setuptools import setup, find_packages

install_reqs = ["requests", "retrying"]

setup(
    name="jupiterone",
    version="1.1.0",
    description="A Python client for the JupiterOne API",
    license="MIT License",
    author="JupiterOne",
    author_email="solutions@jupiterone.com",
    maintainer="JupiterOne",
    url="https://github.com/JupiterOne/jupiterone-api-client-python",
    install_requires=install_reqs,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Security",
    ],
    packages=find_packages(),
)
