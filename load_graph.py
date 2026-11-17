"""Build the energy-research knowledge graph in Neo4j Aura from the corpus/ text files.

Entities and relationships were extracted by hand from the 35 corpus documents.
Credentials come from .env (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE).
"""
import os
from neo4j import GraphDatabase


def load_env(path=".env"):
    for line in open(path):
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k, v)


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


def build(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    for n, t, city, country in ORGS:
        tx.run("CREATE (:Organization {name:$n,type:$t,city:$city,country:$country})", n=n, t=t, city=city, country=country)
    for n in PEOPLE:
        tx.run("CREATE (:Person {name:$n})", n=n)
    for n, s, e, pi in PROJECTS:
        tx.run("""CREATE (pr:Project {name:$n,start:$s,end:$e}) WITH pr
                  MATCH (p:Person {name:$pi}) CREATE (p)-[:PRINCIPAL_INVESTIGATOR_OF]->(pr)""", n=n, s=s, e=e, pi=pi)
    for proj, f, amt, cur in FUNDING:
        tx.run("""MATCH (p:Project {name:$p}),(o:Organization {name:$f})
                  CREATE (p)-[:FUNDED_BY {amount:$a,currency:$c}]->(o)""", p=proj, f=f, a=amt, c=cur)
    for proj, org, role in PARTICIPATION:
        tx.run("""MATCH (p:Project {name:$p}),(o:Organization {name:$o})
                  CREATE (o)-[:PARTICIPATES_IN {role:$r}]->(p)""", p=proj, o=org, r=role)
    for person, org, kind, role, s, e, cur, seq in AFFIL:
        tx.run("""MATCH (p:Person {name:$p}),(o:Organization {name:$o})
                  CREATE (p)-[:AFFILIATED_WITH {kind:$k,role:$r,start:$s,end:$e,current:$c,seq:$q}]->(o)""",
               p=person, o=org, k=kind, r=role, s=s, e=e, c=cur, q=seq)
    for sup, stu, y in SUPERVISION:
        tx.run("""MATCH (a:Person {name:$a}),(b:Person {name:$b})
                  CREATE (a)-[:SUPERVISED {year:$y}]->(b)""", a=sup, b=stu, y=y)
    for t in TECHS:
        tx.run("CREATE (:Technology {name:$n})", n=t)
    for proj, t in [("ALPINE", "Sodium-Ion Battery"), ("MONSOON", "Sodium-Ion Battery"),
                    ("RECLAIM", "Sodium-Ion Battery"), ("MONSOON", "Thermal Management"),
                    ("CASCADE", "Load Forecasting")]:
        tx.run("MATCH (p:Project {name:$p}),(t:Technology {name:$t}) CREATE (p)-[:FOCUSES_ON]->(t)", p=proj, t=t)

    for pid, title, y, venue, proj, authors, techs in PUBS:
        tx.run("""MATCH (pr:Project {name:$proj})
                  CREATE (pub:Publication {id:$id,title:$t,year:$y,venue:$v})-[:PRODUCED_IN]->(pr)""",
               id=pid, t=title, y=y, v=venue, proj=proj)
        for i, a in enumerate(authors, 1):
            tx.run("""MATCH (p:Person {name:$a}),(pub:Publication {id:$id})
                      CREATE (p)-[:AUTHORED {position:$i}]->(pub)""", a=a, id=pid, i=i)
        for t in techs:
            tx.run("MATCH (pub:Publication {id:$id}),(t:Technology {name:$t}) CREATE (pub)-[:ABOUT]->(t)", id=pid, t=t)
    for a, b in CITES:
        tx.run("MATCH (a:Publication {id:$a}),(b:Publication {id:$b}) CREATE (a)-[:CITES]->(b)", a=a, b=b)

    tx.run("""MATCH (h:Organization {name:'Halvorsen Institute of Technology'})
              CREATE (e:Event {name:'Nordic Storage Symposium 2023',city:'Trondheim',country:'Norway',
                               start:date('2023-06-14'),end:date('2023-06-16')})
              CREATE (h)-[:HOSTED]->(e)""")
    for pid in PRESENTED_AT_SYMPOSIUM:
        tx.run("MATCH (p:Publication {id:$id}),(e:Event) CREATE (p)-[:PRESENTED_AT]->(e)", id=pid)
    for person, role in SYMPOSIUM_PARTICIPANTS:
        tx.run("MATCH (p:Person {name:$p}),(e:Event) CREATE (p)-[:PARTICIPATED_IN {role:$r}]->(e)", p=person, r=role)

    tx.run("""CREATE (pt:Patent {id:'LSS-PAT-2020-114',title:'Layered Sodium-Ion Cell with Composite Electrolyte Interface',
                                 filed:2020,granted:2022})
              WITH pt
              MATCH (l:Organization {name:'Lumen Storage Systems'}),(t:Technology {name:'Sodium-Ion Battery'}),
                    (a:Project {name:'ALPINE'}),(v:Person {name:'Elena Voss'}),(k:Person {name:'Katarina Novak'})
              CREATE (l)-[:HOLDS]->(pt), (pt)-[:COVERS]->(t), (pt)-[:LICENSED_IN]->(a),
                     (v)-[:INVENTOR_OF]->(pt), (k)-[:INVENTOR_OF]->(pt)""")
    tx.run("""MATCH (pub:Publication {id:'P23'}),(pt:Patent) CREATE (pt)-[:BACKGROUND_IN]->(pub)""")

    for name, city, country, yr, cap, batt, ops, proj, supplier, mgr, techs in SITES:
        tx.run("""MATCH (p:Project {name:$proj})
                  CREATE (s:Site {name:$n,city:$city,country:$country,commissioned:$y,capacity:$cap,battery:$b})
                  CREATE (s)-[:ESTABLISHED_UNDER]->(p)""",
               n=name, city=city, country=country, y=yr, cap=cap, b=batt, proj=proj)
        for o in ops:
            tx.run("MATCH (s:Site {name:$s}),(o:Organization {name:$o}) CREATE (o)-[:OPERATES]->(s)", s=name, o=o)
        if supplier:
            tx.run("MATCH (s:Site {name:$s}),(o:Organization {name:$o}) CREATE (o)-[:SUPPLIED_CELLS_TO]->(s)", s=name, o=supplier)
        if mgr:
            tx.run("MATCH (s:Site {name:$s}),(p:Person {name:$p}) CREATE (p)-[:MANAGES]->(s)", s=name, p=mgr)
        for t in techs:
            tx.run("MATCH (s:Site {name:$s}),(t:Technology {name:$t}) CREATE (s)-[:USES_TECHNOLOGY]->(t)", s=name, t=t)
    # patent-specific design links (corpus docs 28, 29, 32)
    tx.run("""MATCH (pt:Patent),(s:Site) WHERE s.name IN ['Vestfjord Pilot Site','Tiruvallur Test Bed']
              CREATE (s)-[:BUILT_TO_DESIGN]->(pt)""")


if __name__ == "__main__":
    load_env()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))
    driver.verify_connectivity()
    with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as s:
        for c, p in [("Organization", "name"), ("Person", "name"), ("Project", "name"),
                     ("Publication", "id"), ("Site", "name"), ("Technology", "name"),
                     ("Patent", "id"), ("Event", "name")]:
            s.run(f"CREATE CONSTRAINT {c.lower()}_{p} IF NOT EXISTS FOR (n:{c}) REQUIRE n.{p} IS UNIQUE").consume()
        s.execute_write(build)
        for r in s.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY label"):
            print(r["label"], r["n"])
        print("relationships:", s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"])
    driver.close()
