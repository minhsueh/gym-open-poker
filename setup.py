from setuptools import setup

setup(
    name="gym_open_poker",
    packages = ["gym_open_poker"],
    description='gym_open_poker',
    version="0.0.4",
    author='Min-Hsueh Chiu',
    author_email='peter810601@gmail.com',
    url="https://github.com/minhsueh/gym-open-poker",
    install_requires=["gym==0.26.0", "pygame==2.1.0", "PyYAML==6.0.1", "numpy==1.25.2"],
    python_requires=">=3.9"
)
