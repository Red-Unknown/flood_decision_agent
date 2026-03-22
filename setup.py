from setuptools import find_packages, setup


setup(
    name="flood_decision_agent",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.26",
        "pandas>=2.2",
        "scikit-learn>=1.4",
        "loguru>=0.7",
    ],
)

