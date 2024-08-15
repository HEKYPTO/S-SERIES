from setuptools import setup
from Cython.Build import cythonize
import os

os.environ["CFLAGS"] = "-O3"

setup(ext_modules=cythonize("bench.pyx"))
