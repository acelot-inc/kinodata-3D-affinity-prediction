from setuptools import setup, find_packages

setup(
    name="kinodata",
    version="1.0.0",
    packages=find_packages(include=[
        "kinodata",
        "kinodata.transform",
        "kinodata.model",
        "kinodata.training",
        "kinodata.data",
        "kinodata.data.featurization",
        "kinodata.data.io",
        "kinodata.data.utils"
    ]),
)
