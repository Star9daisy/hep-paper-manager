# HEP Paper Manager (HPM)

![workflow](https://s2.loli.net/2024/08/13/8NGUdRiV7DFl5WH.png)

HPM is a command-line tool that helps adds literature from Inspire HEP to a
Notion database according to its arXiv ID.

It has features as following:
- Retrieve papers by arXiv ID.
- Customizable paper template.
- Interactive CLI for easy setup and usage.

## Installation
```
pip install hep-paper-manager
```

## Let's add a paper to a Notion database!
In this step-by-step guide, we will together add "[1511.05190] Jet image -- deep
learning edition"([link](https://inspirehep.net/literature/1405106)) to a Notion
database.

### Step 0: Create an integration in Notion
1. Open [My Integrations](https://www.notion.so/my-integrations).
2. Click `+ New integration`.
3. Enter a name for your integration.
4. Select your workspace.
4. Click `show` and `copy` the integration secret as your token.

Check the official guide for integrations
[here](https://developers.notion.com/docs/create-a-notion-integration).

![Create an integration](https://s2.loli.net/2024/08/13/zya7foBb9t4sdF1.gif)

### Step 1: Create a Notion database
A database is the place where we'll put all papers. Each item (or page)
represents a paper.

1. Follow the gif to create a database.

   ![create a database](https://s2.loli.net/2024/08/13/1juSdLEIJhN64KW.gif)

2. Add the following properties by clicking `+` on the right:

  | Property             | Type         |
  | -------------------- | ------------ |
  | Title                | Title        |
  | Authors              | Multi-select |
  | Date                 | Date         |
  | Published in         | Select       |
  | ArXiv ID             | Text         |
  | DOI                  | Text         |
  | Number of citations  | Number       |
  | Number of references | Number       |
  | Number of pages      | Number       |
  | Abstract             | Text         |
  | Bibtex               | Text         |
  | URL                  | URL          |

   ![Add properties](https://s2.loli.net/2024/08/13/bcNFe3rWhfd4P1A.gif)

After you finish it, open any page to check all properties, which should look
like this:

![An empty page](https://s2.loli.net/2024/08/13/A5ghwXqle6dDZma.png)

! Remember to remove the first empty three pages after the properties are
checked since we want to keep this database nice and clean.

![Remove empty pages](https://s2.loli.net/2024/08/14/Os47fTja6WbdFMx.gif)

3. Connect to the integration.
   ![Connect to integration](https://s2.loli.net/2024/08/13/kBcjlYVtd1eOyLo.gif)

### Step 2: Set up `hpm`
1. Install `hep-paper-manager`.
   ```bash
   pip install hep-paper-manager
   ```
   ![pip install](https://s2.loli.net/2024/08/14/PasNi7Rpn6mBt2u.gif)

2. Initialize it to add the token.
   ```bash
   hpm init
   ```
   ![hpm init](https://s2.loli.net/2024/08/14/vwLU36dPgY7syoC.gif)


### Step 3: Add the paper to the database
1. Search Inspire for the paper "jet image -- deep learning edition" and copy the
   arXiv ID:
   ![search inspire](https://s2.loli.net/2024/08/14/fP5M8yQlz7NZEgX.gif)

2. Use `hpm add` to add it to the database.
   ```bash
   hpm add 1511.05190
   ```

   ![hpm add](https://s2.loli.net/2024/08/14/O5dHaPDwBNC8MIF.gif)

3. Go back and check the database page. The paper is right there!
   ![new paper in database](https://s2.loli.net/2024/08/14/sD68Td791afcAJe.png)


Try to add more papers as you like!

### Step 4: Update the paper
After a while, the paper may have newer information like citation number. You
can update the paper in the database by `hpm update`.
```bash
hpm update 1511.05190
```

Or update all the paper at once without any id.
```bash
hpm update
```

Note, the columns in the database but not in the template will not be updated.
So you can add more columns to the database without worrying about `hpm`
overwriting your data.

## Engines
- `Inspire`: It fetches papers from the [Inspire HEP](https://inspirehep.net/).
   It serves the default engine for `hpm`. `InspirePaper` has the following
   properties:
    - `title`: str
    - `authors`: list[str]
    - `date`: str
    - `journal`: str | None
    - `arxiv_id`: str
    - `doi`: str | None
    - `n_citations`: int
    - `n_references`: int
    - `n_pages`: int | None
    - `abstract`: str
    - `bibtex`: str
    - `url`: str


## Templates
Template saves the mapping from paper properties to Notion database properties.
You can adjust the properties within the template. The template file is at
`$HOME/.hpm/paper.yml`.

Below is the default template for `Inspire` engine which holds all properties
of `InspirePaper`:
- `paper.yml`
  ```yaml
  database_id: <database_id>
  properties:
    title: Title
    authors: Authors
    date: Date
    journal: Published in
    arxiv_id: ArXiv ID
    doi: DOI
    n_citations: Number of citations
    n_references: Number of references
    n_pages: Number of pages
    abstract: Abstract
    bibtex: Bibtex
    url: URL
  ```

## Updates
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
