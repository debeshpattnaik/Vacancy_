from setuptools import setup, find_packages

setup(
    name="legal-vacancy-tracker",
    version="0.1.0",
    description="A tracker for legal vacancies in India",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32,<3",
        "beautifulsoup4>=4.12,<5",
        "lxml>=5,<7",
        "html5lib>=1.1,<2",
        "urllib3>=2.0,<3",
        "rich>=13.0,<14",
        "click>=8.1,<9",
        "jinja2>=3.1,<4",
        "python-dotenv>=1.0,<2",
    ],
    entry_points={
        "console_scripts": [
            "legal-vacancy-tracker=app.tracker:main",
        ],
    },
)
