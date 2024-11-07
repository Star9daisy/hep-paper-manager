import os
import shutil
from unittest.mock import patch

from typer.testing import CliRunner

import hpm.services.notion.objects.page_properties as pg_props
from hpm.cli import app
from hpm.config import Config
from hpm.services.notion.client import Notion

runner = CliRunner()


def test_init():
    config = Config()

    is_backed_up = False
    if config.app_dir.exists():
        os.rename(config.app_dir, config.app_dir.parent / ".hpm.backup")
        is_backed_up = True

    with patch("hpm.cli.Prompt.ask") as mock_prompt:
        # First time
        mock_prompt.side_effect = [
            os.getenv("NOTION_ACCESS_TOKEN_FOR_HPM"),
            "2",
        ]

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Welcome to HEP Paper Manager" in result.stdout
        assert "Done!" in result.stdout

        # Reinitialize
        mock_prompt.side_effect = [
            "y",
            os.getenv("NOTION_ACCESS_TOKEN_FOR_HPM"),
            "2",
        ]

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Welcome to HEP Paper Manager" in result.stdout
        assert "Done!" in result.stdout

        # No overwrite token and re-choose the database
        mock_prompt.side_effect = [
            "n",
            "2",
        ]

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Welcome to HEP Paper Manager" in result.stdout
        assert "Done!" in result.stdout

    # Clean up
    shutil.rmtree(config.app_dir)

    if is_backed_up:
        os.rename(config.app_dir.parent / ".hpm.backup", config.app_dir)


def test_init_with_token_and_database_id(TEST_PAPERS_DATABASE_ID):
    config = Config()

    is_backed_up = False
    if config.app_dir.exists():
        os.rename(config.app_dir, config.app_dir.parent / ".hpm.backup")
        is_backed_up = True

    token = os.getenv("NOTION_ACCESS_TOKEN_FOR_HPM")
    database_id = TEST_PAPERS_DATABASE_ID

    result = runner.invoke(app, ["init", "-t", token, "-d", database_id, "-f"])
    assert result.exit_code == 0
    assert "Token saved" in result.stdout
    assert "Choose database" in result.stdout

    # Clean up
    shutil.rmtree(config.app_dir)

    if is_backed_up:
        os.rename(config.app_dir.parent / ".hpm.backup", config.app_dir)


def test_demo(TEST_PAGE_ID):
    config = Config()

    is_backed_up = False
    if config.app_dir.exists():
        os.rename(config.app_dir, config.app_dir.parent / ".hpm.backup")
        is_backed_up = True

    token = os.getenv("NOTION_ACCESS_TOKEN_FOR_HPM")
    page_id = TEST_PAGE_ID

    result = runner.invoke(app, ["demo", "-t", token, "-p", page_id])
    assert result.exit_code == 0
    assert "Creating a demo database" in result.stdout
    assert "Created" in result.stdout

    database_id = result.stdout.split("\n")[-2].split("/")[-1]
    notion = Notion(token)
    notion.archive_database(database_id)

    # Clean up
    if is_backed_up:
        os.rename(config.app_dir.parent / ".hpm.backup", config.app_dir)


def test_add_and_update():
    # Set the page size to 1 for testing
    config = Config()
    original_page_size = config.load_config_for_notion_client()["page_size"]
    config.save_config_for_notion_client({"page_size": 1})

    # This paper is already in the database
    result = runner.invoke(app, ["add", "1511.05190"])
    assert result.exit_code == 1
    assert "Already in the database" in result.stdout
    assert "1351444c50e481da9cb2d8061f21097c" in result.stdout

    # This paper is not in the database
    result = runner.invoke(app, ["update", "unknown_id"])
    assert result.exit_code == 1
    assert "Not added to the database yet" in result.stdout

    # This is a new paper
    result = runner.invoke(app, ["add", "1407.5675"])
    assert result.exit_code == 0
    assert "Creating a new page in Notion" in result.stdout

    # Get the page id from the stdout
    page_id = result.stdout.split("\n")[-2].split("-")[-1]

    # Remove "Date", "Published in" information for update test
    notion = Notion()
    notion.update_page(
        page_id,
        properties={
            "Date": pg_props.Date(),
            "Published in": pg_props.Select(),
        },
    )

    result = runner.invoke(app, ["update", "1407.5675"])
    assert result.exit_code == 0
    assert "Updating Date: None -> 2014-07-21" in result.stdout
    assert "Updating Published in: None -> JHEP" in result.stdout

    # Update all papers
    result = runner.invoke(app, ["update", "all"])
    assert result.exit_code == 0

    # Clean up
    notion.archive_page(page_id)
    config.save_config_for_notion_client({"page_size": original_page_size})


def test_version():
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert "HEP Paper Manager" in result.stdout
    assert "Made by Star9daisy" in result.stdout
