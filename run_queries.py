"""Run one Cypher query per question in queries.txt and write results.csv
(Question, Cypher Query, Answer, Execution Time)."""
import csv, json, os, time
from neo4j import GraphDatabase
from load_graph import load_env

QUERIES = [
# 1 Consortium roles
"""MATCH (o:Organization)-[r:PARTICIPATES_IN]->(p:Project {name:'ALPINE'})
MATCH (p)-[f:FUNDED_BY]->(a:Organization)
RETURN o.name AS organization, r.role AS role, a.name AS funding_agency
ORDER BY (r.role = 'coordinator') DESC, o.name""",
# 2 Publication output
"""MATCH (p:Project)
OPTIONAL MATCH (pub:Publication)-[:PRODUCED_IN]->(p)
OPTIONAL MATCH (au:Person)-[a:AUTHORED]->(pub)
OPTIONAL MATCH (au)-[:AFFILIATED_WITH {current:true}]->(org:Organization)
WITH p, pub, a, au, collect(org.name) AS affs
ORDER BY p.name, pub.year, a.position
WITH p, pub, collect(au.name + ' (' + CASE WHEN size(affs)=0 THEN 'n/a' ELSE affs[0] END + ')') AS authors
RETURN p.name AS project, pub.title AS publication, pub.year AS year, authors
ORDER BY project, year""",
# 3 Academic lineage
"""MATCH (s:Person) WHERE EXISTS { (:Person)-[:SUPERVISED]->(s) }
MATCH path = (root:Person)-[:SUPERVISED*1..]->(s)
WHERE NOT EXISTS { (:Person)-[:SUPERVISED]->(root) }
WITH s, path, nodes(path) AS ns
OPTIONAL MATCH (gp:Person)-[:SUPERVISED*2]->(s)
RETURN s.name AS doctoral_researcher,
       [n IN ns | n.name] AS supervision_chain_root_to_researcher,
       gp.name AS academic_grandparent
ORDER BY doctoral_researcher""",
# 4 Mobility
"""MATCH (p:Person)-[r:AFFILIATED_WITH]->(o:Organization)
WITH p, r, o ORDER BY p.name, r.seq
WITH p, collect({org:o.name, kind:r.kind, start:r.start, end:r.end}) AS affs
WHERE size(affs) > 1
RETURN p.name AS researcher,
       [i IN range(0, size(affs)-2) |
          affs[i].org + ' (' + affs[i].kind + ') -> ' + affs[i+1].org + ' (' + affs[i+1].kind + ')'] AS moves
ORDER BY researcher""",
# 5 Funding overview
"""MATCH (a:Organization {type:'FundingAgency'})
OPTIONAL MATCH (pr:Project)-[f:FUNDED_BY]->(a)
OPTIONAL MATCH (c:Organization)-[:PARTICIPATES_IN]->(pr) WHERE c.type IN ['Company','Utility']
RETURN a.name AS funding_agency, pr.name AS project, f.amount AS amount, f.currency AS currency,
       collect(DISTINCT c.name + ' (' + c.type + ')') AS companies_and_utilities
ORDER BY funding_agency, project""",
# 6 International reach
"""MATCH (p:Person)-[:AFFILIATED_WITH {current:true}]->(o:Organization)
MATCH (p)-[:AUTHORED]->(:Publication)<-[:AUTHORED]-(co:Person)-[:AFFILIATED_WITH {current:true}]->(co_o:Organization)
WHERE co <> p AND co_o.country <> o.country
WITH p, o.country AS own_country, collect(DISTINCT co_o.country) AS countries
RETURN p.name AS researcher, own_country, size(countries) AS distinct_foreign_countries, countries
ORDER BY distinct_foreign_countries DESC, researcher""",
# 7 Citation influence
"""MATCH (target:Publication) WHERE target.year = 2022 AND target.title CONTAINS 'Cathode Stability'
MATCH path = (citing:Publication)-[:CITES*1..]->(target)
RETURN citing.title AS citing_publication, citing.year AS year,
       min(length(path)) AS hops,
       CASE WHEN min(length(path)) = 1 THEN 'direct' ELSE 'indirect' END AS citation_type
ORDER BY hops, year""",
# 8 Collaboration horizon
"""MATCH (hit:Organization {name:'Halvorsen Institute of Technology'})
CALL (hit) {
  MATCH (hit)-[:PARTICIPATES_IN]->(p:Project)<-[:PARTICIPATES_IN]-(o:Organization)
  WHERE o <> hit
  RETURN o, 1 AS hops, collect(DISTINCT p.name) AS via
  UNION
  MATCH (hit)-[:PARTICIPATES_IN]->(p1:Project)<-[:PARTICIPATES_IN]-(m:Organization)-[:PARTICIPATES_IN]->(p2:Project)<-[:PARTICIPATES_IN]-(o:Organization)
  WHERE m <> hit AND o <> hit AND o <> m AND NOT EXISTS { (hit)-[:PARTICIPATES_IN]->(:Project)<-[:PARTICIPATES_IN]-(o) }
  RETURN o, 2 AS hops, collect(DISTINCT p1.name + ' -> ' + m.name + ' -> ' + p2.name) AS via
}
RETURN o.name AS organization, hops, via AS reached_through_projects
ORDER BY hops, organization""",
# 9 IP to field
"""MATCH (l:Organization {name:'Lumen Storage Systems'})-[:HOLDS]->(pt:Patent)-[:COVERS]->(t:Technology)
MATCH (s:Site)-[:USES_TECHNOLOGY]->(t)
MATCH (s)-[:BUILT_TO_DESIGN]->(pt)
MATCH (s)-[:ESTABLISHED_UNDER]->(p:Project)
OPTIONAL MATCH (op:Organization)-[:OPERATES]->(s)
OPTIONAL MATCH (inv:Person)-[:INVENTOR_OF]->(pt)
RETURN s.name AS site, pt.id AS patent, p.name AS project,
       collect(DISTINCT op.name) AS operators, collect(DISTINCT inv.name) AS inventors""",
# 10 Collaborator recommendation
"""MATCH (a:Person)-[:AUTHORED]->(:Publication)<-[:AUTHORED]-(c:Person)-[:AUTHORED]->(:Publication)<-[:AUTHORED]-(b:Person)
WHERE a.name < b.name AND a <> b AND c <> a AND c <> b
  AND NOT EXISTS { (a)-[:AUTHORED]->(:Publication)<-[:AUTHORED]-(b) }
MATCH (a)-[:AUTHORED]->(:Publication)-[:ABOUT]->(t:Technology)<-[:ABOUT]-(:Publication)<-[:AUTHORED]-(b)
RETURN a.name AS researcher_a, b.name AS researcher_b,
       collect(DISTINCT c.name) AS common_coauthors, collect(DISTINCT t.name) AS shared_technology_areas
ORDER BY researcher_a, researcher_b""",
]


def questions():
    text = open("queries.txt").read().strip()
    return [q.strip() for q in text.split("\n\n") if q.strip()]


if __name__ == "__main__":
    load_env()
    qs = questions()
    assert len(qs) == len(QUERIES), (len(qs), len(QUERIES))
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))
    with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as s, \
            open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Question", "Cypher Query", "Answer", "Execution Time (ms)"])
        for q, cy in zip(qs, QUERIES):
            t0 = time.perf_counter()
            res = s.run(cy)
            rows = [r.data() for r in res]
            ms = (time.perf_counter() - t0) * 1000
            w.writerow([q, cy, json.dumps(rows, ensure_ascii=False, default=str), f"{ms:.1f}"])
            print(f"{ms:7.1f} ms  {len(rows):2d} rows  {q[:50]}")
    driver.close()
