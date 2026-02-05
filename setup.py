import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-session-refresh",
    version="0.0.1",
    author="Anderson Lima",
    author_email="amilnosredna@gmail.com",
    description="A simple Django middleware to refresh user sessions periodically to prevent timeout during active use.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amilnosredna/django-session-refresh/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache 2.0",
        "Operating System :: OS Independent",
        "Framework :: Django 5+",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.12',
)
