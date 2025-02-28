from setuptools import setup, find_packages

setup(
    name="llm-jina",
    version="0.3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "llm>=0.20",
        "httpx>=0.27.0",
        "sqlite-utils>=3.36",
        "click>=8.0.0",
        "requests>=2.25.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.900",
            "isort>=5.10.0"
        ]
    },
    entry_points={
        "llm": ["jina = llm_jina"]
    },
    python_requires=">=3.7",
)
