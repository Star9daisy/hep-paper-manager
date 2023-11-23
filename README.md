# HEP Paper Manager (HPM)

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
![properties](https://imgur.com/FeqCkhW.gif)

Open a blank page, it should look like this:
![blank page](https://imgur.com/qPGOU7C.png)

To complete the database setup, we need to add the integration to the database.
![add integration](https://imgur.com/CBCgY81.gif)

### Step 2: Set up `hpm`
To let `hpm` add papers for you, we need to install and initialize it first.
```bash
pip install hpm
hpm init
```
![hpm init](https://imgur.com/MxoTz7I.gif)

   
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