# setup.py  (プロジェクトルート)
from setuptools import setup, find_packages

setup(
    name="factchecker",
    version="0.1.0",
    packages=find_packages(),  # factchecker/ 以下を自動認識
)
