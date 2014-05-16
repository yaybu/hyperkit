from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='Hyperkit',
      version=version,
      url="http://yaybu.com/",
      description="Hypervisor tools",
      long_description = open("README.rst").read(),
      author="Isotoma Limited",
      author_email="support@isotoma.com",
      license="Apache Software License",
      classifiers = [
          "Intended Audience :: System Administrators",
          "Operating System :: POSIX",
          "License :: OSI Approved :: Apache Software License",
      ],
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyyaml',
          'ipaddress',
      ],
      extras_require = {
          'test': ['unittest2', 'mock'],
          },
      entry_points = """
      [console_scripts]
      hyperkit = hyperkit.command:main
      """
      )
