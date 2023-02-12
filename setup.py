from setuptools import setup, find_packages

from convid import name, version, url, description

with open("README.md") as ld:
    long_description = ld.read()

with open("requirements.txt") as req:
    install_requires = req.readlines()

setup(
    name=name,
    version=version,
    url=url,
    license="MIT",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Leovalcante",
    author_email="leovalcante@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.7",
    entry_points={"console_scripts": ["convid = convid.convid:convid"]},
)
