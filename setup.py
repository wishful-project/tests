from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_testing_framework',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz',
    author_email='gawlowicz@tkn.tu-berlin.de',
    description='WiSHFUL Testing Framework',
    long_description='Test of WiSHFUL Control Framework',
    keywords='testing',
    install_requires=['pytest', 'sh', 'PyRIC', 'pyzmq', 'gevent']
)
