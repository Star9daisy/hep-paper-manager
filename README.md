# HEP Paper Manager (HPM)

![workflow](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/workflow.svg)
[![PyPI - Version](https://img.shields.io/pypi/v/hep-paper-manager)](https://pypi.org/project/hep-paper-manager/)
[![Downloads](https://static.pepy.tech/badge/hep-paper-manager)](https://pepy.tech/project/hep-paper-manager)
[![codecov](https://codecov.io/gh/Star9daisy/hep-paper-manager/branch/main/graph/badge.svg?token=6VWJi5ct6c)](https://app.codecov.io/gh/Star9daisy/hep-paper-manager)
[![GitHub](https://img.shields.io/github/license/star9daisy/hep-paper-manager)](https://github.com/Star9daisy/hep-paper-manager/blob/main/LICENSE)

HPM is a command-line tool that helps add papers from Inspire HEP to Notion
database according to its ArXiv ID.

Features:
- Retrieve papers by arXiv ID.
- Customizable paper template.
- Interactive CLI for easy setup and usage.

## Installation
```
pip install hep-paper-manager
```

## Try to add a paper to a demo database

Before we start, please make sure you have installed this app successfully.

In this step-by-step guide, we will together add "[1511.05190] Jet image -- deep
learning edition"([link](https://inspirehep.net/literature/1405106)) to a demo
database.

### Step 1: Create an integration in Notion
1. Open [My Integrations](https://www.notion.so/my-integrations).
2. Click `+ New integration`.
3. Enter a name for your integration.
4. Select your workspace.
4. Click `show` and `copy` the integration secret as your token.

To learn more about integrations, please check the official guide
[here](https://developers.notion.com/docs/create-a-notion-integration).

![Create an integration](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/1-create_an_integration.gif)

### Step 2: Create a blank page and link the integration to it
1. Click the `+` button next to your workspace name to create a new blank page.
2. In the three-dot menu in the upper right, find `Connect to`.
3. Select the integration you created in the previous step.

![Create a blank page and link the integration](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/2-create_a_blank_page.gif)

### Step 3: Create a demo database via `hpm`
Open your terminal, and input:
```bash
hpm demo -t <token> -p <page_id>
```

![Create a demo database](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/3-create_a_demo_database.gif)

You should see a database is created and connected to the integration.

![Check the demo database](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/4-check_the_demo_database.gif)

### Step 4: Initialize the `hpm` app
Use the token to initialize the `hpm` app.
```bash
hpm init -t <token>
```

![Initialize hpm](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/5-initialize_hpm.gif)

### Step 5: Add the paper to the database
Use `hpm add` to add it into the demo database.
```bash
hpm add 1511.05190
```

![Add the paper to the database](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/6-add_paper_1511.05190.gif)


Go back and check the database page. The paper is right there!

![Check the database page](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/7-check_the_paper.gif)

Try to add more papers as you like!

## Modify the default paper template
You can use `hpm info` to find the app directory. The default paper template is
located at `{app_dir}/templates/paper.yml`:

```yaml
database_id: <your database_id>
properties:
  id: null
  url: URL
  type: null
  source: null
  title: Title
  authors.name: Authors
  created_date: Date
  published_place: Published in
  published_date: Published
  eprint: ArXiv ID
  citation_count: Citations
  abstract: Abstract
  doi: DOI
  bibtex: BibTeX
```

The keys in the `properties` section are the paper information retrieved from
Inspire HEP. Their values correspond to the Notion page properties. Modify them
as you like. `null` means that information will not be recorded in the database.


## Other commands

- `hpm update [<arxiv_id>|all]`: Update one paper according to its ArXiv ID or all papers in the database.

![Update the paper](https://raw.githubusercontent.com/Star9daisy/hep-paper-manager/refs/heads/main/assets/8-update_paper.gif)

- `hpm info`: Show all file paths related to this app.
- `hpm clean`: Remove all files related to this app.


## Updates
### v0.4.0
- Refactor the codebase and reorganize the file structure.

### v0.3.0
- Refactor the codebase by only allowing adding papers by arXiv ID.

### v0.2.2
- Fix the error when `hpm add` some conference papers that may have no publication info.

### v0.2.1
- Fix the bug that `hpm add` only checks the first 100 pages in the database.
- Fix the checkmark style.

### v0.2.0
- Refactor the codebase by introducing `notion_database`.
- Add `hpm update` to update one paper in the database.
- Add `hpm info` to show the information of this app.

### v0.1.4
- Update print style.
- Add friendly error message when the `database_id` is not specified.
### v0.1.3
- Update `hpm add` to check if the paper already exists in the database.
- You can now create a database with more properties then the template.
### v0.1.2
- Update paper from Inspire engine to include url, bibtex, and source.
### v0.1.1
- Add `hpm init` for interactive setup.
- Add `hpm add` for adding a paper to a Notion database.
- Introduce the default `Inspire` engine and `paper.yml` template.
