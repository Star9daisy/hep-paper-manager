# HEP Paper Manager (HPM)

![workflow](https://imgur.com/u8SVtjE.png)

HPM is a command-line tool that helps adds Inspire literature to a
Notion database. 

It has features as following:
- Retrieve HEP papers by Inspire ID, or Arxiv ID, or DOI.
- Customizable paper template for creating pages in a Notion database.
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
4. Copy the integration secret as your token.

Check the official guide for integrations [here](https://developers.notion.com/docs/create-a-notion-integration).

![integration](https://imgur.com/RXib1zV.gif)

### Step 1: Create a Notion database
A database is the place where we'll put all papers of interest in. Create an
empty page and make it a database.

![database](https://imgur.com/jLBqKYg.gif)

Each item represents a paper. Below is what we want to record for each
paper:
| Property   | Type         | Comment                                         |
| ---------- | ------------ | ----------------------------------------------- |
| Date       | Date         | When the paper appears in the Inspire.          |
| Citations  | Number       | More citations, more likely to be a good paper. |
| Title      | Title        |                                                 |
| Type       | Select       | An article, a thesis, or a conference paper.    |
| Journal    | Select       | The journal where the paper is published.       |
| Authors    | Multi-select |                                                 |
| Link       | URL          | The Inspire link to the paper.                  |
| Abstract   | Text         |                                                 |
| Bibtex     | Text         |                                                 |
| Inspire ID | Text         |                                                 |
| Arxiv ID   | Text         |                                                 |
| DOI        | Text         |                                                 |

The "Type" above is what we call a "property" in Notion. You can add a new
property by clicking `+` in the database page. Or click an existing property
to modify its type.
![FeqCkhW](https://github.com/Star9daisy/hep-paper-manager/assets/47071425/81630270-ea99-41d6-a4a2-33ddbe0c4b88)

Open a blank page, it should look like this:
![blank page](https://imgur.com/qPGOU7C.png)

To complete the database setup, we need to add the integration to the database.
![add integration](https://imgur.com/CBCgY81.gif)

### Step 2: Set up `hpm`
To let `hpm` add papers for you, we need to install and initialize it first.
```bash
pip install hep-paper-manager
hpm init
```
![hpm init](https://imgur.com/uxBkbW6.gif)

If you want to change the default template, use `hpm info` to find the location
of the template file. Then modify the template file directly.

![hpm info](https://imgur.com/QuVPVK4.png)

   
### Step 3: Add the paper to the database
Usually, we search for papers on Inspire. The Inspire ID is the number in the
URL.
![inpsire](https://imgur.com/E3meDtH.gif)

In the command line, we use `hpm add` to add the paper to the database.
```bash
hpm add 1405106
```

Let's go back and check the database page. The paper is right there!
![database](https://imgur.com/r9bWdlm.png)

Of course, you can also add papers by Arxiv ID or DOI.
```bash
hpm add 1511.05190 --id-type arxiv
hpm add "10.1007/JHEP07(2016)069" --id-type doi
```
![other id](https://imgur.com/j4zi8ws.png)

You can now add more papers to your Notion database.

### Step 4: Update the paper
After a while, the paper may have newer information like citation number. You
can update the paper in the database by `hpm update`.
```bash
hpm update 1405106
```

Just like `hpm add`, you can also update papers by Arxiv ID or DOI.
```bash
hpm update 1511.05190 --id-type arxiv
hpm update "10.1007/JHEP07(2016)069" --id-type doi
```

Note, the columns in the database but not in the template will not be updated.
So you can add more columns to the database without worrying about losing
information.

## Engines
- `Inspire`: It fetches papers from the [Inspire HEP](https://inspirehep.net/).
   It serves the default engine for `hpm`. `InspirePaper` has the following
   properties:
   - date: str
   - citations: int
   - title: str
   - type: str
   - journal: str
   - authors: list[str]
   - link: str
   - abstract: str
   - bibtex: str
   - inspire_id: str
   - arxiv_id: str
   - doi: str


## Templates
Template saves the mapping from paper properties to Notion database properties.
You can adjust the properties within the template.

Below is the default template for `Inspire` engine which holds all properties
of `InspirePaper`:
- `paper.yml`
  ```yaml
  engine: Inspire
  database_id: <database_id>
  properties:
    date: Date
    citations: Citations
    title: Title
    type: Type
    journal: Journal
    authors: Authors
    link: Link
    abstract: Abstract
    bibtex: Bibtex
    inspire_id: Inspire ID
    arxiv_id: Arxiv ID
    doi: DOI
  ```
  These properties match the properties of the InpspirePaper class. You can
  modify the template to fit your needs. 

  ! Remember the last three lines are necessary. You can't remove them.

## Updates
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
