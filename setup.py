
import re
from setuptools import setup

version = re.search("__version__ = '([^']+)'", 
        open('hugophotoswipe/__init__.py').read()).group(1)

setup(
        name="hugophotoswipe",
        version=version,
        description="Tool for creating and managing PhotoSwipe albums in Hugo",
        url="www.github.com/GjjvdBurg/HugoPhotoSwipe",
        author="Gertjan van den Burg",
        author_email="gertjanvandenburg@gmail.com",
        keywords="<keywords>",
        license="GPL v3",
        packages=["hugophotoswipe"],
        scripts=['bin/hps'],
        include_package_data=True,
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

            # Python 2 and 3?
            'Programming Language :: Python :: 2'
            'Programming Language :: Python :: 2.3'
            'Programming Language :: Python :: 2.4'
            'Programming Language :: Python :: 2.5'
            'Programming Language :: Python :: 2.6'
            'Programming Language :: Python :: 2.7'
            'Programming Language :: Python :: 3'
            'Programming Language :: Python :: 3.0'
            'Programming Language :: Python :: 3.1'
            'Programming Language :: Python :: 3.2'
            'Programming Language :: Python :: 3.3'
            'Programming Language :: Python :: 3.4'
            ],
        )
