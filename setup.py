#!/usr/bin/env python

from distutils.core import setup, find_packages

setup(name='TreinaPB',
      version='1.0',
      description='Training HTK models for forced alignment in Brazilian Portuguese.',
      author='Gustavo Silveira',
      author_email='silveira@tuta.io',
      packages(['treinapb'],
      license='GPL-3.0',
      install_requires = [
          'pydub',
          'pyenchant',
          'sly',
          'nltk',
          'termcolor',
          'pandas',
          'numpy',
          'pyyaml',
          'scipy',
          'TextGrid'
      ],
      entry_points={
          'console_scripts': ["treinapb=trainpb.__main__:main"]},
     )
