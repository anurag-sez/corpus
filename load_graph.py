"""Build the energy-research knowledge graph in Neo4j Aura from the corpus/ text files.

Entities and relationships were extracted by hand from the 35 corpus documents.
Credentials come from .env (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE).
"""
import os
from neo4j import GraphDatabase


def connect():
    """Read .env and return (driver, database)."""
    for line in open(".env"):
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k, v)
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"],
                                  auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))
    driver.verify_connectivity()
    return driver, os.environ.get("NEO4J_DATABASE", "neo4j")


ORGS = [  # name, type, city, country
    ("Halvorsen Institute of Technology", "University", "Trondheim", "Norway"),
    ("Rhine Valley University", "University", "Karlsruhe", "Germany"),
    ("Southern Peninsula Institute of Science", "Institute", "Chennai", "India"),
    ("Maple Ridge University", "University", "Vancouver", "Canada"),
    ("Lumen Storage Systems", "Company", "Munich", "Germany"),
    ("Fjordgrid AS", "Utility", "Bergen", "Norway"),
    ("Deccan Power Corporation", "Utility", "Hyderabad", "India"),
    ("Pacific Cell Technologies", "Company", "Vancouver", "Canada"),
    ("European Clean Energy Council", "FundingAgency", "Brussels", "Belgium"),
    ("National Science Endowment of India", "FundingAgency", "New Delhi", "India"),
    ("Canadian Innovation Fund", "FundingAgency", "Ottawa", "Canada"),
]

PROJECTS = [  # name, start, end, pi
    ("ALPINE", 2021, 2025, "Ingrid Solberg"),
    ("MONSOON", 2022, 2027, "Priya Raghunathan"),
    ("CASCADE", 2022, 2025, "Daniel Okafor"),
    ("RECLAIM", 2022, 2027, "Markus Weber"),
]

# project, funder, amount, currency
FUNDING = [
    ("ALPINE", "European Clean Energy Council", 4200000, "EUR"),
    ("RECLAIM", "European Clean Energy Council", 3100000, "EUR"),
    ("MONSOON", "National Science Endowment of India", 380000000, "INR"),
    ("CASCADE", "Canadian Innovation Fund", 2800000, "CAD"),
]

# project, org, role
PARTICIPATION = [
    ("ALPINE", "Halvorsen Institute of Technology", "coordinator"),
    ("ALPINE", "Rhine Valley University", "materials (solid-state electrolytes)"),
    ("ALPINE", "Lumen Storage Systems", "manufacturing (cells)"),
    ("ALPINE", "Fjordgrid AS", "pilot operation"),
    ("MONSOON", "Southern Peninsula Institute of Science", "coordinator"),
    ("MONSOON", "Deccan Power Corporation", "utility partner (grid connection, operational data)"),
    ("MONSOON", "Maple Ridge University", "modelling"),
    ("CASCADE", "Maple Ridge University", "coordinator"),
    ("CASCADE", "Pacific Cell Technologies", "software integration"),
    ("CASCADE", "Halvorsen Institute of Technology", "battery degradation models"),
    ("RECLAIM", "Rhine Valley University", "coordinator"),
    ("RECLAIM", "Lumen Storage Systems", "industrial partner (scrap and used cells)"),
]

PEOPLE = [  # name, title/role
    "Ingrid Solberg", "Markus Weber", "Priya Raghunathan", "Daniel Okafor",
    "Elena Voss", "Tomas Berg", "Katarina Novak", "Sofia Lindqvist",
    "Arjun Menon", "Li Wei", "Hannah Brooks", "Rahul Venkatesan",
]

# person, org, kind, role, start, end, current, seq (order of affiliations per person, from the texts)
AFFIL = [
    ("Ingrid Solberg", "Rhine Valley University", "study", "doctoral student", None, 2005, False, 1),
    ("Ingrid Solberg", "Halvorsen Institute of Technology", "employment", "professor", 2008, None, True, 2),
    ("Markus Weber", "Rhine Valley University", "employment", "professor", None, None, True, 1),
    ("Priya Raghunathan", "Southern Peninsula Institute of Science", "employment", "associate professor", None, None, True, 1),
    ("Priya Raghunathan", "Maple Ridge University", "visiting", "visiting scholar", 2019, 2019, False, 2),
    ("Daniel Okafor", "Maple Ridge University", "employment", "professor", None, None, True, 1),
    ("Elena Voss", "Rhine Valley University", "employment", "postdoctoral researcher", 2015, 2019, False, 1),
    ("Elena Voss", "Lumen Storage Systems", "employment", "CTO", 2019, None, True, 2),
    ("Tomas Berg", "Halvorsen Institute of Technology", "study", "doctoral student", None, 2016, False, 1),
    ("Tomas Berg", "Fjordgrid AS", "employment", "lead storage engineer", 2016, None, True, 2),
    ("Katarina Novak", "Rhine Valley University", "employment", "senior researcher", None, None, True, 1),
    ("Sofia Lindqvist", "Halvorsen Institute of Technology", "study", "doctoral student", None, None, True, 1),
    ("Arjun Menon", "Southern Peninsula Institute of Science", "study", "doctoral student", None, None, True, 1),
    ("Li Wei", "Maple Ridge University", "employment", "research scientist", None, None, True, 1),
    ("Hannah Brooks", "Maple Ridge University", "study", "doctoral student", None, 2018, False, 1),
    ("Hannah Brooks", "Pacific Cell Technologies", "employment", "head of software", 2018, None, True, 2),
    ("Rahul Venkatesan", "Deccan Power Corporation", "employment", "project manager", None, None, True, 1),
]

# supervisor, student, year (None = ongoing)
SUPERVISION = [
    ("Markus Weber", "Ingrid Solberg", 2005),
    ("Ingrid Solberg", "Tomas Berg", 2016),
    ("Ingrid Solberg", "Sofia Lindqvist", None),
    ("Daniel Okafor", "Hannah Brooks", 2018),
    ("Priya Raghunathan", "Arjun Menon", None),
]

TECHS = ["Sodium-Ion Battery", "Thermal Management", "Load Forecasting"]

PUBS = [  # id, title, year, venue, project, authors, techs
    ("P22", "Sodium-Ion Cell Degradation Under Variable Grid Loads", 2023,
     "Journal of Energy Storage Engineering", "ALPINE",
     ["Ingrid Solberg", "Sofia Lindqvist", "Tomas Berg"], ["Sodium-Ion Battery"]),
    ("P23", "Sodium-Ion Cathode Stability in Solid-State Electrolytes", 2022,
     "Advanced Electrochemical Materials", "ALPINE",
     ["Katarina Novak", "Ingrid Solberg", "Elena Voss"], ["Sodium-Ion Battery"]),
    ("P24", "Thermal Management Strategies for Stationary Batteries in Hot Climates", 2024,
     "International Journal of Thermal Energy Systems", "MONSOON",
     ["Priya Raghunathan", "Arjun Menon", "Daniel Okafor"], ["Thermal Management"]),
    ("P25", "Probabilistic Load Forecasting with Gradient-Boosted Models", 2023,
     "Transactions on Smart Grid Analytics", "CASCADE",
     ["Daniel Okafor", "Li Wei", "Hannah Brooks"], ["Load Forecasting"]),
    ("P26", "Hydrometallurgical Recovery of Sodium-Ion Cathode Materials", 2024,
     "Journal of Sustainable Materials Processing", "RECLAIM",
     ["Markus Weber", "Katarina Novak"], ["Sodium-Ion Battery"]),
    ("P27", "Forecast-Aware Dispatch of Grid Batteries", 2025,
     "Energy Systems Control Letters", "CASCADE",
     ["Hannah Brooks", "Sofia Lindqvist", "Daniel Okafor"], ["Load Forecasting"]),
]
CITES = [("P22", "P23"), ("P24", "P22"), ("P26", "P23"), ("P27", "P25"), ("P27", "P22")]
PRESENTED_AT_SYMPOSIUM = ["P22", "P25"]

SITES = [  # name, city, country, commissioned, capacity, battery, operators, project, supplier, manager/coordinator, techs
    ("Vestfjord Pilot Site", "Bergen", "Norway", 2024, "2 MWh", "sodium-ion",
     ["Fjordgrid AS", "Halvorsen Institute of Technology"], "ALPINE", "Lumen Storage Systems",
     "Tomas Berg", ["Sodium-Ion Battery"]),
    ("Tiruvallur Test Bed", "Chennai", "India", 2025, "1.5 MWh", "sodium-ion",
     ["Southern Peninsula Institute of Science", "Deccan Power Corporation"], "MONSOON", "Lumen Storage Systems",
     "Rahul Venkatesan", ["Sodium-Ion Battery", "Thermal Management"]),
    ("Fraser Valley Demonstration Site", "British Columbia", "Canada", 2024, "800 kWh", "lithium iron phosphate",
     ["Maple Ridge University", "Pacific Cell Technologies"], "CASCADE", None,
     None, ["Load Forecasting"]),
]

SYMPOSIUM_PARTICIPANTS = [
    ("Ingrid Solberg", "keynote"), ("Elena Voss", "industry panel"),
    ("Daniel Okafor", "presenter"), ("Markus Weber", "invited guest"),
]


LABELS = {"Organization": "name", "Person": "name", "Project": "name", "Publication": "id",
          "Site": "name", "Technology": "name", "Patent": "id", "Event": "name"}


def dicts(keys, rows):
    return [dict(zip(keys.split(), r)) for r in rows]


def build(tx):
    def run(cypher, rows):  # one batched UNWIND query per node/relationship type
        tx.run("UNWIND $rows AS row " + cypher, rows=rows)

    def link(a, b, rel, rows, props=""):
        """MATCH (a:LabelA {key: row.a}), (b:LabelB {key: row.b}) CREATE (a)-[:rel {props}]->(b)"""
        (la, ka), (lb, kb) = a.split(":"), b.split(":")
        run(f"MATCH (a:{la} {{{ka}: row.a}}), (b:{lb} {{{kb}: row.b}}) CREATE (a)-[:{rel} {{{props}}}]->(b)", rows)

    tx.run("MATCH (n) DETACH DELETE n")

    # nodes
    run("CREATE (:Organization {name:row.name, type:row.type, city:row.city, country:row.country})",
        dicts("name type city country", ORGS))
    run("CREATE (:Person {name:row})", PEOPLE)
    run("CREATE (:Project {name:row.name, start:row.start, end:row.end})", dicts("name start end", [p[:3] for p in PROJECTS]))
    run("CREATE (:Technology {name:row})", TECHS)
    run("CREATE (:Publication {id:row.id, title:row.title, year:row.year, venue:row.venue})",
        dicts("id title year venue", [p[:4] for p in PUBS]))
    run("""CREATE (:Site {name:row.name, city:row.city, country:row.country,
                          commissioned:row.year, capacity:row.capacity, battery:row.battery})""",
        dicts("name city country year capacity battery", [x[:6] for x in SITES]))
    tx.run("""CREATE (:Event {name:'Nordic Storage Symposium 2023', city:'Trondheim', country:'Norway',
                              start:date('2023-06-14'), end:date('2023-06-16')})
              CREATE (:Patent {id:'LSS-PAT-2020-114', filed:2020, granted:2022,
                               title:'Layered Sodium-Ion Cell with Composite Electrolyte Interface'})""")

    # projects, funding, people
    link("Person:name", "Project:name", "PRINCIPAL_INVESTIGATOR_OF", [{"a": p[3], "b": p[0]} for p in PROJECTS])
    link("Project:name", "Organization:name", "FUNDED_BY", dicts("a b amount currency", FUNDING), "amount:row.amount, currency:row.currency")
    link("Organization:name", "Project:name", "PARTICIPATES_IN",
         [{"a": o, "b": p, "role": r} for p, o, r in PARTICIPATION], "role:row.role")
    link("Person:name", "Organization:name", "AFFILIATED_WITH", dicts("a b kind role start end current seq", AFFIL),
         "kind:row.kind, role:row.role, start:row.start, end:row.end, current:row.current, seq:row.seq")
    link("Person:name", "Person:name", "SUPERVISED", dicts("a b year", SUPERVISION), "year:row.year")
    link("Project:name", "Technology:name", "FOCUSES_ON",
         dicts("a b", [("ALPINE", TECHS[0]), ("MONSOON", TECHS[0]), ("RECLAIM", TECHS[0]),
                       ("MONSOON", TECHS[1]), ("CASCADE", TECHS[2])]))

    # publications
    link("Publication:id", "Project:name", "PRODUCED_IN", [{"a": p[0], "b": p[4]} for p in PUBS])
    link("Person:name", "Publication:id", "AUTHORED",
         [{"a": au, "b": p[0], "position": i} for p in PUBS for i, au in enumerate(p[5], 1)], "position:row.position")
    link("Publication:id", "Technology:name", "ABOUT", [{"a": p[0], "b": t} for p in PUBS for t in p[6]])
    link("Publication:id", "Publication:id", "CITES", dicts("a b", CITES))

    # event, patent
    ev, pat = "Event:name", "Patent:id"
    link("Organization:name", ev, "HOSTED", [{"a": "Halvorsen Institute of Technology", "b": "Nordic Storage Symposium 2023"}])
    link("Publication:id", ev, "PRESENTED_AT", [{"a": p, "b": "Nordic Storage Symposium 2023"} for p in PRESENTED_AT_SYMPOSIUM])
    link("Person:name", ev, "PARTICIPATED_IN",
         [{"a": p, "b": "Nordic Storage Symposium 2023", "role": r} for p, r in SYMPOSIUM_PARTICIPANTS], "role:row.role")
    pid = "LSS-PAT-2020-114"
    link("Organization:name", pat, "HOLDS", [{"a": "Lumen Storage Systems", "b": pid}])
    link(pat, "Technology:name", "COVERS", [{"a": pid, "b": TECHS[0]}])
    link(pat, "Project:name", "LICENSED_IN", [{"a": pid, "b": "ALPINE"}])
    link(pat, "Publication:id", "BACKGROUND_IN", [{"a": pid, "b": "P23"}])
    link("Person:name", pat, "INVENTOR_OF", [{"a": p, "b": pid} for p in ("Elena Voss", "Katarina Novak")])

    # sites
    link("Site:name", "Project:name", "ESTABLISHED_UNDER", [{"a": x[0], "b": x[7]} for x in SITES])
    link("Organization:name", "Site:name", "OPERATES", [{"a": o, "b": x[0]} for x in SITES for o in x[6]])
    link("Organization:name", "Site:name", "SUPPLIED_CELLS_TO", [{"a": x[8], "b": x[0]} for x in SITES if x[8]])
    link("Person:name", "Site:name", "MANAGES", [{"a": x[9], "b": x[0]} for x in SITES if x[9]])
    link("Site:name", "Technology:name", "USES_TECHNOLOGY", [{"a": x[0], "b": t} for x in SITES for t in x[10]])
    link("Site:name", pat, "BUILT_TO_DESIGN", [{"a": x[0], "b": pid} for x in SITES[:2]])  # docs 28, 29, 32


if __name__ == "__main__":
    driver, db = connect()
    with driver.session(database=db) as s:
        for label, key in LABELS.items():
            s.run(f"CREATE CONSTRAINT {label.lower()}_{key} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{key} IS UNIQUE").consume()
        s.execute_write(build)
        for r in s.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY label"):
            print(r["label"], r["n"])
        print("relationships:", s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"])
    driver.close()
