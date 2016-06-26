from setuptools import setup, find_packages

setup(
    name="crawling",
    version="0.1",
    scripts=["crawling.py"],
    author="pandada8",
    author_email="pandada8@gmail.com",
    packages=find_packages(),
    license="MIT",
    install_requires=["aiohttp >= 0.20"],
    url="https://github.com/pandada8/crawling"
)
