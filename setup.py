from setuptools import setup

setup(
    name='pydeploy',
    version='0.1.0',
    author='Tony Han',
    author_email='itony9401@live.com',
    description='Pydeploy automate static websites deployment to S3.',
    license='GPLv3+',
    packages=['pydeploy'],
    url='https://github.com/tyh835/pydeploy',
    install_requires=[
        'click',
        'boto3'
    ]
)