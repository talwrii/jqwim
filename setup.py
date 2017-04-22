import setuptools
import os

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='jqwim',
    version="0.1.0",
    author='Tal Wrii',
    author_email='talwrii@gmail.com',
    description='',
    license='GPLv3',
    keywords='',
    url='',
    packages=['jqwim'],
    long_description='See https://github.com/talwrii/jqwim',
    entry_points={
        'console_scripts': ['jqwim=jqwim.jqwim:main']
    },
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    test_suite='nose.collector',
    install_requires=[]
)
