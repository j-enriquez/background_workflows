import setuptools

# Read long description from README.md
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read dependencies from requirements.txt
with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# Setup configuration
setuptools.setup(
    name="background_workflows",
    version="0.3.0",
    author="Jose Enriquez",
    author_email="joseaenriqueza@hotmail.com",
    description="Background Workflows for task processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j-enriquez/background_workflows",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",  # Python version
        "License :: OSI Approved :: MIT License",  # License type
        "Operating System :: OS Independent",  # OS compatibility
    ],
    install_requires=requirements,  # Install dependencies from requirements.txt
    python_requires='>=3.6',  # Minimum Python version
)
