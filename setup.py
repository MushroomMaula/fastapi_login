import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()


setuptools.setup(
    name="fastapi-login",
    version="1.8.0",
    author="Max Rausch-Dupont",
    author_email="maxrd79@gmail.com",
    descritpion="Flask-Login like package for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MushroomMaula/fastapi_login",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "fastapi",
        "passlib",
        "pyjwt",
        "typing_extensions"
    ],
    extra_requires={
        "asymmetric": ["cryptography"]
    },

    zip_safe=False,
    include_package_data=True,
    package_data={"fastapi_login": ["py.typed"]}
)
