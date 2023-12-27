from setuptools import setup

setup(
    name="gym-open-poker",
    packages = ["gym-open-poker"],
    description='gym-open-poker',
    version="0.0.1",
    author='Min-Hsueh Chiu',
    author_email='peter810601@gmail.com',
    url="https://github.com/minhsueh/gym-open-poker",
    install_requires=["gym==0.26.0", "pygame==2.1.0"],
    python_requires="==3.9"
)
