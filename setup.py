from setuptools import setup

setup(
    name='cloudify-nagiosrest-plugin',
    version='0.2.3',
    packages=[
        'nagiosrest_plugin',
    ],
    install_requires=['cloudify-plugins-common>=3.3.1'],
)
