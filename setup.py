from distutils.core import setup
from glob import glob


setup(
    name = "sixteen",
    version = "0.00.1dev",
    author = "startling",
    author_email = "tdixon51793@gmail.com",
    packages = ["sixteen"],
    scripts = glob("scripts/*"),
    install_requires = ["twisted", "txws"],
)
