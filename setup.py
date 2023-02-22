from setuptools import setup

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
    name="pytheriak",
    version="0.0.17",
    description="Wrappers to call and read_out theriak from python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["pytheriak.wrapper", "pytheriak.hdfwriter"],
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=["numpy >= 1.23", ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Scientific/Engineering"]
)
