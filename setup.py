from setuptools import find_packages, setup

setup(
        name = "CRS Newsfetch",
        packages = find_packages(),
        entry_points = { "console_scripts": ["crs_newsfetch=crs_newsfetch.main:main"] },
)
