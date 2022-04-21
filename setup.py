import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyplaato",
    version="0.0.18",
    author="JohNan",
    author_email="johan.nanzen@gmail.com",
    description="Asynchronous Python client for getting Plaato Airlock and Keg data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohNan/pyplaato",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3',
)
