import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jinrdatabaseloader",
    version="0.0.1",
    author="NPM Group",
    author_email="mihail.zelenyy@phystech.edu",
    url='http://npm.mipt.ru/',
    description="JINR Database Tools",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="",
    packages=setuptools.find_packages(),
    entry_points = {
      "console_scripts" : [
          "jinr-database-loader = jinrdatabaseloader.run:console_app"
      ],
      # "gui_scripts" : [
      #     "jinr-jinrdatabaseloader-gui = jinrdatabaseloader.run:gui_app"
      # ]
    },
    package_data = {
      "jinrdatabaseloader" : ["resources/*"],
      # "jinrdatabaseloader.ui" : ["resources/*", "qml/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # project_urls={
    #     "Bug Tracker": "",
    #     "Documentation": "",
    #     "Source Code": "",
    # },
    install_requires=[
        "SQLAlchemy",
        "psycopg2-binary",
        "jsonschema",
        "json_schema_for_humans",
        # "qt-material"
    ]
    # test_suite='tests'
)
