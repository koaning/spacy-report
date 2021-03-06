from setuptools import setup, find_packages


base_packages = [
    "spacy>=3.3.0",
    "altair>=4.2.0",
    "clumper>=0.2.15",
    "rich>=10.3.0",
    "scikit-learn>=1.0.0",
    "typer>=0.3.0",
    "Jinja2>=3.1.1",
]

dev_packages = [
    "flake8>=3.6.0",
    "pytest>=4.0.2",
    "pre-commit>=2.17.0",
    "interrogate>=1.5.0",
    "black>=21.0.0",
]

setup(
    name="spacy_report",
    version="0.1.1",
    author="Vincent D. Warmerdam",
    packages=find_packages(exclude=["notebooks", "docs"]),
    url="https://koaning.github.io/spacy_report/",
    project_urls={
        "Documentation": "https://github.com/koaning/spacy_report/",
        "Source Code": "https://github.com/koaning/spacy_report/",
        "Issue Tracker": "https://github.com/koaning/spacy_report/issues",
    },
    install_requires=base_packages,
    extras_require={"base": base_packages, "dev": base_packages + dev_packages},
    package_data={"spacy_report": ["templates/*.html", "templates/*.js"]},
)
