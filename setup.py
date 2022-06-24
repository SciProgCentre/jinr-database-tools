import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smart-data-parser",
    version="0.0.1",
    author="NPM Group",
    author_email="mihail.zelenyy@phystech.edu",
    url='http://npm.mipt.ru/',
    description="JINR Tools for parsing data and loading to database",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="",
    packages=setuptools.find_packages(),
    entry_points = {
      "console_scripts" : [
          "smart-data-parser = sdp.run:console_app"
      ],
      "gui_scripts" : [
          "smart-data-parser-gui = sdp.run:gui_app"
      ]
    },
    package_data = {
      "sdp" : ["resources/*"],
      "sdp.ui" : ["resources/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/mipt-npm/jinr-database-tools",
        "Documentation": "https://github.com/mipt-npm/jinr-database-tools",
        "Source Code": "https://github.com/mipt-npm/jinr-database-tools",
    },
    install_requires=[
        "SQLAlchemy",
        "psycopg2-binary",
        "jsonschema",
        "json_schema_for_humans",
        "PySide2",
        "qt-material"
    ]
    # test_suite='tests'
)
