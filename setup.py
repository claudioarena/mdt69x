import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdt69x",
    version="1.0.9",
    author="Claudio Arena",
    author_email="claudio.arena.12@ucl.ac.uk",
    description="Package to communicate with Thorlab MDT69X Piezo controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claudioarena/mdt69x",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'markdown',
        'pyserial'
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
