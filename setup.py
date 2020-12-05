import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dogfighter",
    version="0.0.1",
    author="Todd Perry",
    author_email="todd.perry@myport.ac.uk",
    description="High octate dogfighting simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djentleman/dogfighter",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts':
        ['dogfighter=dogfighter:main'],
    })
