#!/usr/bin/python3
# cython: language_level=3

"""
Author - Adam Asay
Company - INVITE Networks

Description:
"""

from setuptools import setup

setup(name='in_meraki',
      packages=['in_meraki'],
      version='0.1',
      description='INVITE Networks Meraki Tools',
      url='https://github.com/invite-networks/in-meraki',
      author='Adam Asay',
      author_email='adam@invitenetworks.com',
      license='Apache2',
      install_requires=[
          'pysnmp',
          'requests',
      ],
      zip_safe=False)
