from setuptools import setup, find_packages

setup(
    name="claude-model-changer",
    version="1.0.0",
    description="Manage Claude Code model env profiles — switch between env presets",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "claude-model-change=claude_model_changer.cli:main",
        ],
    },
)
