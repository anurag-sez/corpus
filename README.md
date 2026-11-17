# Energy Research Knowledge Graph (Neo4j Aura)

Builds a knowledge graph from the 35 text documents in `corpus/` (organizations, people, projects, publications, sites, patent, technologies, event), then answers the 10 questions in `queries.txt` with Cypher.

## Files

| File | Purpose |
|---|---|
| `corpus/` | Source documents |
| `queries.txt` | The 10 questions |
| `load_graph.py` | Wipes the database and rebuilds the graph (entities extracted by hand from the corpus) |
| `run_queries.py` | Runs one Cypher query per question and writes `results.csv` |
| `results.csv` | Output: Question, Cypher Query, Answer, Execution Time (ms) |

## Graph model

- **Nodes:** Organization (University, Institute, Company, Utility, FundingAgency), Person, Project, Publication, Site, Technology, Patent, Event
- **Key relationships:** `PARTICIPATES_IN {role}`, `FUNDED_BY {amount, currency}`, `PRINCIPAL_INVESTIGATOR_OF`, `AFFILIATED_WITH {kind, role, start, end, current, seq}`, `SUPERVISED`, `AUTHORED`, `CITES`, `PRODUCED_IN`, `ABOUT`, `OPERATES`, `SUPPLIED_CELLS_TO`, `ESTABLISHED_UNDER`, `USES_TECHNOLOGY`, `BUILT_TO_DESIGN`, `HOLDS`, `COVERS`, `INVENTOR_OF`, `HOSTED`, `PRESENTED_AT`

Modelling choices: a person's country is that of their current affiliation; study and visiting stays are `AFFILIATED_WITH` with `kind` = `study` / `visiting`, ordered by `seq`.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install neo4j
```

Create `.env` (git-ignored) with your Aura credentials:

```
NEO4J_URI=neo4j+s://<id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j
```

```bash
.venv/bin/python load_graph.py    # WARNING: deletes all existing data in the database
.venv/bin/python run_queries.py   # writes results.csv
```