from setuptools import setup, Extension

module = Extension('path_finding', sources=['path_finding.c'])

setup(
    name='path_finding',
    version='1.0',
    description='This is a path finding module.',
    ext_modules=[module],
)
