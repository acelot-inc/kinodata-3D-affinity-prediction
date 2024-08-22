from setuptools import setup, find_packages


def get_version() -> str:
    return "1.0.0"


print(find_packages())

setup(
    name="kinodata",
    version=get_version(),
    packages=find_packages(include=["kinodata", "kinodata.transform", "kinodata.model", "kinodata.training", "kinodata.data", "kinodata.data.featurization", "kinodata.data.io", "kinodata.data.utils"]),

)
