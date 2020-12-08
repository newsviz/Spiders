# Automatically created by: shub deploy

from setuptools import setup

setup(
    name="project",
    version="1.0",
    packages=[
        "newsbot",
    ],
    entry_points={"scrapy": ["settings = newsbot.settings"]},
)
