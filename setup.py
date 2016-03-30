from setuptools import setup, find_packages

setup(
    name="pyuvis",
    version="0.4",
    packages=find_packages(),

    install_requires=['pvl', 'pandas', 'xarray'],

    # metadata
    author="K.-Michael Aye",
    author_email="kmichael.aye@gmail.com",
    description="Software tools for the Cassini UVIS instrument.",
    license="BSD",
    keywords="Cassini UVIS ",
)
