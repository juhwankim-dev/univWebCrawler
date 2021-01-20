import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="inko-py",
    version="1.0.0",
    author="JackCme",
    author_email="pitou_106@naver.com",
    description="Python pip module of Inko.js",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JackCme/inko.py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)