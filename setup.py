from setuptools import setup, find_packages

setup(
    name="ollama_chatbox",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "httpx",
        "pytest",
        "pytest-asyncio"
    ],
) 