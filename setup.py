"""Package installation configuration."""

from setuptools import find_packages, setup

setup(
    name='langchain-opensearch-rag',
    version='0.1.0',
    description='LangChain RAG application with OpenSearch',
    author='euphonie',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=[
        'langchain>=0.1.0',
        'opensearch-py>=2.0.0',
        'gradio>=4.0.0',
        'python-dotenv>=1.0.0',
        'pydantic>=2.0.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'ruff>=0.1.0',
            'mypy>=1.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
