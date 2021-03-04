import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reactive-net",
    version="0.1.1",
    author="Gianluca Scopelliti",
    author_email="gianlu.1033@gmail.com",
    description="Networking library for reactive-tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gianlu33/reactive-net",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
