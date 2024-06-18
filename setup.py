from setuptools import setup

setup(
    name="lsp-textile name",
    version="0.1.0",
    # install_requres=['PyYAML'], 依存するライブラリ（必要な場合）
    packages=["module"],
    entry_points={"console_scripts": ["command_name=module.lsp-textile:main"]},
)
