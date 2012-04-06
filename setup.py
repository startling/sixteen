from distutils.core import setup
from glob import glob


setup(
    name = "sixteen",
    version = "0.00.0dev",
    author = "startling",
    author_email = "tdixon51793@gmail.com",
    packages = ["sixteen"],
    install_requires = ["bitstring"],
    scripts = glob("scripts/*"),
)
