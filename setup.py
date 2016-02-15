from distutils.core import setup

setup(
    name='PyCast3',
    version='0.0.1',
    packages=['PyCast3'],
    scripts=['bin/PyCast3'],
    url='https://github.com/Arthelon/PyCast3',
    license='LICENSE.txt',
    author='Daniel',
    author_email='hsing.daniel@gmail.com',
    description='Search for and download your favourite podcasts',
    install_requires=[
        'requests',
        'feedparser',
        'clint',
        'pytest'
    ]
)
