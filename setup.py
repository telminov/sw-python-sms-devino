# coding: utf-8
# python setup.py sdist register upload
from setuptools import setup

setup(
    name='sw-python-sms-devino',
    version='0.0.1',
    description='Integration with API of devinotele.com.',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-python-sms-devino',
    packages=[
        'sms_devino',
        'sms_devino.tests',
    ],
    include_package_data=True,
    license='The MIT License',
    test_suite='sms_devino.tests',
    install_requires=[
        'requests',
    ],
    tests_requirements=[
        'nose', 'mock'
    ]
)