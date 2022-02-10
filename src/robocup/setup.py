from setuptools import setup

setup(
    name='robocup',
    version='0.1.0',
    keywords='games, environment, agent, rl, ai, gym',
    url='https://github.com/hardmaru/slimevolleygym',
    description='Slime Volleyball Gym Environment',
    packages=['robocup'],
    install_requires=[
        'gym>=0.9.4',
        'numpy>=1.13.0',
        'opencv-python>=3.4.2.0'
        'parameterized==0.8.1'
    ]
)
