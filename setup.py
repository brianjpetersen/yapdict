import os
import sys
import setuptools
import shutil


__where__ = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(__where__, 'yapdict', 'VERSION.txt'), 'rb') as f:
    __version__ = f.read().decode('ascii').strip()


# would prefer to just use markdown, but not compatible with setuptools; see the following Github
# issue for more information: https://github.com/pypa/packaging-problems/issues/46
with open(os.path.join(__where__, 'DESCRIPTION.rst'), 'rb') as f:
    long_description = f.read().decode('utf-8').strip()


class TestCommand(setuptools.Command):
    
    description = 'Test the yapdict package with pytest.'
    user_options = []
    
    def initialize_options(self): pass

    def finalize_options(self): pass
    
    def run(self):
        import pytest
        exit_code = pytest.main(['tests.py', ])
        sys.exit(exit_code)


class PublishCommand(setuptools.Command):
    
    description = 'Build and publish the package.'
    user_options = []
    
    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        try:
            print('removing previous builds...')
            shutil.rmtree(os.path.join(__where__, 'dist'))
        except FileNotFoundError:
            pass
        print('building source and wheel (universal) distribution...')
        os.system(f'{sys.executable} setup.py sdist bdist_wheel --universal')
        print('uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')
        sys.exit()


setuptools.setup(
    name='yapdict',
    version=__version__,
    description='Yet Another Persistent Dict: sqlite-backed storage with a Python dict API.',
    long_description=long_description,
    author='Brian J Petersen',
    author_email='brianjpetersen@gmail.com',
    url='https://github.com/brianjpetersen/yapdict',
    packages=setuptools.find_packages(),
    install_requires=['apsw>=3.9.2-r1', ],
    tests_require=['pytest', ],
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    cmdclass={
        'publish': PublishCommand,
        'test': TestCommand,
    },
)
