"""
Setup script so this package can be installed using distutils, setuptools, or pip
"""

from setuptools import setup

setup(
    name="jumerge",
    version="1.0",
    description="Huge Library for merging JUNIT reports. Avoids repeats accross multiple browsers and sizes.",
    py_modules=['jumerge', 'junit_tree']
)
