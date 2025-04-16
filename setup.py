from setuptools import setup, find_packages

setup(
    name="voice_cloning",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "torch>=1.7.0",
        "torchaudio>=0.7.0",
        "librosa>=0.8.0",
        "soundfile>=0.10.3",
        "scipy>=1.5.0",
        "tqdm>=4.45.0",
        "matplotlib>=3.3.0",
        "pyworld>=0.3.0",
        "praat-parselmouth>=0.4.3",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
    ],
) 