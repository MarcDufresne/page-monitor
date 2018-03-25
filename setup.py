import os
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="page-monitor",
    version="0.2",
    author="MarcDufresne",
    author_email="marc.andre.dufresne@gmail.com",
    description="Simple Python based Page monitoring with "
                "JS support and notifications",
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    license="MIT",
    keywords="page-monitor monitoring website-monitor "
             "email telegram-messages mailgun smtp telegram",
    url="https://github.com/MarcDufresne/page-monitor",
    packages=["page_monitor"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Utilities"
    ],
    include_package_data=True,
    zip_safe=True,
    install_requires=read("requirements.txt"),
    entry_points={
        "console_scripts": [
            "page_monitor = page_monitor.monitor:run_monitor"
        ]
    }
)
