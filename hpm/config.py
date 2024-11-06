import shutil
from configparser import ConfigParser
from pathlib import Path

import typer
import yaml


class Config:
    def __init__(self) -> None:
        self.app_dir = Path(typer.get_app_dir("hpm", force_posix=True))
        self.token_file = self.app_dir / "TOKEN"
        self.template_dir = self.app_dir / "templates"
        self.built_in_templates_dir = Path(__file__).parent / "templates"
        self.config_file = self.app_dir / "config.ini"

    def save_config_for_notion_client(self, params: dict) -> None:
        config = ConfigParser()
        config["notion_client"] = params
        with open(self.config_file, "w") as f:
            config.write(f)

    def load_config_for_notion_client(self) -> dict:
        config = ConfigParser()
        config.read(self.config_file)
        return config["notion_client"]

    def clean(self) -> None:
        if self.app_dir.exists():
            shutil.rmtree(self.app_dir)

    def initialize(self) -> None:
        self.clean()

        self.app_dir.mkdir(parents=True)
        self.template_dir.mkdir()

    def is_initialized(self) -> bool:
        return self.app_dir.exists()

    def save_token(self, token: str) -> None:
        self.token_file.write_text(token)

    def load_token(self) -> str:
        return self.token_file.read_text()

    def save_template(self, name: str, template: dict) -> None:
        self.template_file = self.template_dir / f"{name}.yml"
        self.template_file.write_text(yaml.dump(template, sort_keys=False))

    def load_template(self, name: str) -> dict:
        self.template_file = self.template_dir / f"{name}.yml"
        return yaml.safe_load(self.template_file.read_text())

    def load_built_in_template(self, name: str) -> dict:
        template_file = self.built_in_templates_dir / f"{name}.yml"
        return yaml.safe_load(template_file.read_text())
