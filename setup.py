import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "Sphinx>=0.6",
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='sphinxcontrib-jsoncall',
    version='0.3',
    description='Sphinx extension that adds a simple button to perform test calls to JSON based apis',
    long_description=README,
    author='Alessandro Molina',
    author_email='alessandro.molina@axant.it',
    license='MIT',
    url='https://github.com/amol-/sphinxcontrib.jsoncall',
    packages=find_packages(),
    namespace_packages=['sphinxcontrib'],
    install_requires=install_requires,
    include_package_data=True,
    package_data={'sphinxcontrib.jsoncall': ['_static/*']},
    zip_safe=False
)

