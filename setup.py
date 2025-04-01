from setuptools import find_packages, setup

setup(
    name="fastcmd",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "openai",
        "scikit-learn",
        "sqlite-vec",
    ],
    entry_points={
        "console_scripts": [
            "fastcmd=src.fastcmd:main",
        ],
    },
    python_requires=">=3.8",
)
