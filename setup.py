# coding: utf-8
# python setup.py sdist register upload
from distutils.core import setup

setup(
    name='sw-python-sms-devino',
    version='0.0.1',
    description='Integration with API of devinotele.com.',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-python-sms-devino',
    packages=[
        'sms_devino',
    ],
    license='The MIT License',
    install_requires=[
        'requests',
    ],
)