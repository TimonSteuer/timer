import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timer",
    version="0.0.1",
    author="Timon Steuer",
    author_email="t.steuer@live.com",
    description="Simple timer CLI application storing tracked activities in SQLite3 database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimonSteuer/timer",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9.2',
)