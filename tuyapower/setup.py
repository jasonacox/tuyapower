import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tuyapower-jasonacox",
    version="0.0.1",
    author="Jason Cox",
    author_email="jason@jasonacox.com",
    description="Pull power and state data from Tuya WiFi smart devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="ttps://github.com/jasonacox/tuyapower",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)