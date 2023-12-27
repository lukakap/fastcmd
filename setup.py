from setuptools import setup, find_packages

setup(
    name='fastcmd',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'openai==1.6.1',
        'scikit-learn==1.3.2',
        'numpy==1.26.2',
        
    ],
    entry_points={
        'console_scripts': [
            'fastcmd=fastcmd:main',  # This allows the use of 'fastcmd' command
        ],
    },
)
