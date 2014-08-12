import ez_setup
ez_setup.use_setuptools()
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name = "pyuvis",
    version = "0.2",
    packages = find_packages(),

    install_requires = ['pypds>=1.0'],
    tests_require = ['pytest'],

    cmdclass = {'test': PyTest},

    #metadata
    author = "K.-Michael Aye",
    author_email = "kmichael.aye@gmail.com",
    description = "Software tools for the Cassini UVIS instrument.",
    license = "BSD",
    keywords = "Cassini UVIS ",
)
