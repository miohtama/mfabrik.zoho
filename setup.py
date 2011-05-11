from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='mfabrik.zoho',
      version=version,
      description="Zoho API integration for Python",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='zoho api developers crm',
      author='mFabrik Research Oy',
      author_email='info@mfabrik.com',
      url='http://github.com/miohtama/mfabrik.zoho',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mfabrik'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
