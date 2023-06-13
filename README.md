# HEP Paper Manager (HPM)

HPM allows users to add papers from a search engine to a Notion database. Although it was initially designed to add papers from the Inspire engine, users can add any information as a page to a Notion database.

## Quick Start

To use HPM, first create an integration with the Notion API. Check out this [link](https://www.notion.so/help/create-integrations-with-the-notion-api) for a guide. After creating the integration, you can find your token on the website below:

![integration](https://i.imgur.com/wgBLRjU.png)

To enable this integration, add it in the three dots menu in the upper right corner:

![add_connection](https://i.imgur.com/3gT1cZ6.png)

HPM requires this token as well. Set this token using the command `hpm auth`:

```
$ hpm auth secret_xxx
Token saved in /Users/star9daisy/.hpm/auth.yml
```

To start adding a page to the database, we need the database ID to modify the default paper.yml file in `$HOME/.hpm/templates/`. The database ID can be found in the database URL, like https://www.notion.so/star9daisy/database_id.

```yml
engine: Inspire
database: <add your database ID here>
properties:
  arxiv_id: Arxiv ID
  citations: Citations
  title: Title
  journal: Journal
  authors: Authors
  abstract: Abstract
```

Set the database properties:

```
Arxiv ID: Text
Citations: Number
Title: Title
Journal: Select
Authors: Relation
Abstract: Text
```

![database](https://i.imgur.com/OggfaJG.png)

The Authors property relates to another database. You need to add the integration to that database too:

![related database](https://i.imgur.com/GF5GIIX.png)

Finally, use `hpm add` to add a paper from Inspire to the database:

```
$ hpm add paper 1511.05190
Page created successfully!

```

![add paper](https://i.imgur.com/ei01Qc0.png)

## Commands

`hpm auth <token>`

Authenticate HPM operations on your database with a Notion token. You need to first create an integration with the Notion API. Learn more at [https://www.notion.so/help/create-integrations-with-the-notion-api](https://www.notion.so/help/create-integrations-with-the-notion-api).

`hpm add <template> <parameters>`

Add a page according to a template. A template format is like the one below:

The parameters are a comma-separated string like `"param1,param2"`, then they’ll be resolved as a list of parameters, unpacked to be passed to the `get` method of an engine.

## Engines

`Inspire`

Retrieve paper information from Inspire HEP according to an arxiv ID.