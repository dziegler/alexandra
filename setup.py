from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')


setup(
    name = "alexandra",
    version = '0.1',
    description = 'A thin abstraction over pycassa to interact with Cassandra from Django.',
    long_description = README,
    url = 'http://github.com/dziegler/alexandra',
    author = 'David Ziegler',
    author_email = 'david.ziegler@gmail.com',
    license = 'BSD',
    zip_safe = False,
    packages = find_packages(),
    install_requires = [
        'pycassa>=0.2'
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)