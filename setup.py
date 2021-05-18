from setuptools import setup
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='opdm-api',
    version=versioneer.get_version().split("+")[0],
    cmdclass=versioneer.get_cmdclass(),
    packages=['OPDM'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Haigutus/OPDM',
    license='MIT',
    author='Kristjan Vilgo',
    author_email='kristjan.vilgo@gmail.com',
    description='ENTSO-E OPDM client SOAP API implementation in python',
    install_requires=[
        "requests", "zeep", 'urllib3', 'lxml', 'aniso8601', 'xmltodict',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
