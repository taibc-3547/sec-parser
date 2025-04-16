from setuptools import setup, find_packages

setup(
    name="your_sec_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.1"
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'sec-parser=your_sec_parser.app:main',
        ],
    },
) 