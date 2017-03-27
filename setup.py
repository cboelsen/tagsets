from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tagsets',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='Python lib/cli to search for sets of tags and analyse the sets',
    long_description=long_description,

    url='https://github.com/gerardlt/tagsets',

    author='Gerard Thornley',
    author_email='gthtg@gerardlt.org.uk',

    license='MIT License',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        # TODO: Not yet checked
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.2',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='tags traceability development',

    packages=['tagsets'],
    package_data={'': ['config-schema.yaml']},
    install_requires=['docopt>=0.6.2',
                      'PyYAML>=3.11',
                      'pykwalify>=1.5.0',
                      'termcolor>=1.1.0',
    ],

    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'tagsets=tagsets.cli:main',
        ],
    },
)
