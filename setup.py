from setuptools import setup

setup(
    name='subfix',
    version='0.1',
    description='Subtitle fixer',
    url='https://github.com/alin23/subfix',
    author='Alin Panaitiu',
    author_email='alin.p32@gmail.com',
    license='MIT',
    packages=['subfix'],
    install_requires=[
        'fire',
        'pysrt',
        'daiquiri'
    ],
    entry_points={
        'console_scripts': ['subfix = subfix.subfix:main']
    },
    zip_safe=False
)
