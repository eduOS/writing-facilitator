from setuptools import setup, find_packages

exec(open("src/writing_facilitator/version.py").read())

setup(
    name="writing_facilitator",
    package_dir={'':'src'},
    packages=find_packages('src'),
    version=__version__,
    description="A chatGPT writing facilitator on the terminal",
    author="Lerner Zhang",
    author_email="lerner.zhang@gmail.com",
    long_description_content_type="text/markdown",
    keywords=[
        "artificial intelligence",
        "openai",
        "language learning",
        "writing",
    ],
    install_requires=[
        "rich",
        "openai",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={"console_scripts": [
        "facilitator=writing_facilitator.writing_facilitator:main",
        "chat=writing_facilitator.writing_facilitator:main",
        ]},
)
