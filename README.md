# HEP Paper Manager (HPM)

HPM is a command-line tool that adds High Energy Physics (HEP) papers to a Notion database. It leverages the Inspire engine to source these academic papers, creating a streamlined process for HEP researchers.

## Features
- Fetch HEP papers via the Inspire engine.
- Directly add fetched papers to your Notion database.
- Interactive CLI for easy setup and usage.

## Installation
```
pip install hep-paper-manager
```

## Usage
> Before using `hpm`, check this [link](https://developers.notion.com/docs/create-a-notion-integration) to create an integration with the Notion API to let `hpm` work with your database.

1. Use `hpm init` to set up HPM:
   ```
   hpm init
   ```
   During this process, you will be asked to input your Notion API key and choose a paper template. You'll also be shown related directories where you can modify the default paper template or introduce your own templates.
2. Use `hpm add` to fetch and add a paper to your Notion database:
   ```
   hpm add <template> <parameter>
   ```
   `<parameter>` is a comma-separated string like `"param1,param2"` to pass to the get method of the chosen engine. For the default Inspire engine, it refers to the arxiv ID of the paper.

## Example: Add "[1511.05190] Jet image -- deep learning edition" to a Notion database
1. First create a database in Notion:
   ```
   Arxiv ID: Text
   Citations: Number
   Title: Title
   Journal: Select
   Authors: Multi-select
   Abstract: Text
   URL: URL
   Bibtex: Text
   Source: Select
   ```
   ![database](https://imgur.com/RjIKM7I.png)
   Tip: Consider adding Authors as a Relation property. This allows you to concentrate on specific authors or professors of interest. Just add the integration to the related professors' database. hpm will locate authors based on the page Title property in the related database and fetched names.

2. Then set up `hpm` with `hpm init`:
   ![hpm init](https://imgur.com/qm0uPH1.png)

3. Before adding our paper to a database, review the default `paper.yml` template and insert the database ID:
   ![paper.yml](https://imgur.com/zjzqYiT.png)
   The database ID is in the database URL. For the database just created: "https://www.notion.so/star9daisy/d91282815e5143818ae36ff05132d3b7?v=1ed0289b07ae4e1c8edeeb6eaf1d722f&pvs=4", "d91282815e5143818ae36ff05132d3b7" is the database ID.
   
   Remember to structure your database as shown above and add the integration to the database!

4. Now let's add the paper into the database:
  ![hpm add](https://imgur.com/twxP8cv.png)
   The database in Notion should now look like the following:
  ![database](https://imgur.com/DjJBOuG.png)

## Engines
- `Inspire`: It fetches papers from the [Inspire HEP](https://inspirehep.net/). It serves the default engine for `hpm`.
  - Parameters: `arxiv_id`
  - Returns: `Paper(title, authors, abstract, journal, citations, url, bibtex, source)`

## Templates
You can adjust the properties within the template. On the left is the returned value from the engine and on the right is the property name in the Notion database.
- `paper.yml`
  ```yaml
  engine: Inspire
  database: <database_id>
  properties:
    arxiv_id: Arxiv ID
    citations: Citations
    title: Title
    journal: Journal
    authors: Authors
    abstract: Abstract
    url: URL
    bibtex: Bibtex
    source: Source
  ```

## Updates
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