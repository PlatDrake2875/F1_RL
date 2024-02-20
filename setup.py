from setuptools import setup, find_packages

setup(
    name='f1_env',
    version='0.0.1',
    install_requires=['gymnasium', 'numpy', 'pygame', 'opencv-python'],  # Add any other dependencies F1_Env needs
    packages=find_packages(),
)
