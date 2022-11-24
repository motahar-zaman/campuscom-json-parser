from setuptools import setup, find_packages

setup(
    name='campuscomjsonparser',
    version='0.0.1',
    packages=find_packages(include=['campuscomjsonparser', 'campuscomjsonparser.*']),
    install_requires=[
        'mysql-connector-python',
        'click',
    ],

    entry_points={
        'console_scripts': ['parse=campuscomjsonparser.parser:main']
    }
)
