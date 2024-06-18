from setuptools import setup

setup(
    name="textilels",
    version="0.1.0",
    install_requres=["pygls"],
    # packages=["module"],
    entry_points={"console_scripts": ["textilels=module.textilels:main"]},
)
