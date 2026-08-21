// Useful Cypher examples for the Bots

// 1. Upsert an Asset
MERGE (a:Asset {id: $id})
SET a.name = $name,
    a.type = $type,
    a.internet_facing = $internet_facing,
    a.criticality = $criticality,
    a.last_seen = datetime(),
    a.source = $source
ON CREATE SET a.first_seen = datetime()
RETURN a;

// 2. Link a Finding to an Asset
MATCH (a:Asset {id: $assetId})
MERGE (f:Finding {id: $findingId})
SET f.cve = $cve,
    f.title = $title,
    f.severity = $severity,
    f.cvss = $cvss,
    f.epss = $epss,
    f.kev = $kev,
    f.last_seen = datetime()
ON CREATE SET f.first_seen = datetime(), f.status = 'open'
MERGE (a)-[:HAS_VULN]->(f)
RETURN a, f;

// 3. Ranked attack paths that reach critical assets
MATCH path = (start)-[*1..6]->(crown:Asset)
WHERE crown.criticality IN ['critical', 'high']
  AND any(r IN relationships(path) WHERE type(r) IN ['HAS_VULN', 'CAN_REACH', 'CAN_ASSUME', 'MEMBER_OF'])
WITH path, crown,
     reduce(score = 0.0, n IN nodes(path) | score + coalesce(n.epss, 0.1)) AS pathScore
RETURN path, crown.name AS target, pathScore
ORDER BY pathScore DESC
LIMIT 20;

// 4. Choke-point analysis – nodes that appear in many high-score paths
MATCH (p:AttackPath)-[:INCLUDES]->(n)
WHERE p.score > 0.7
WITH n, count(p) AS pathCount
WHERE pathCount > 2
RETURN n, pathCount
ORDER BY pathCount DESC
LIMIT 15;

// 5. Open high-severity findings on internet-facing assets
MATCH (a:Asset {internet_facing: true})-[:HAS_VULN]->(f:Finding)
WHERE f.severity IN ['critical', 'high'] AND f.status = 'open'
RETURN a.name, f.cve, f.title, f.epss, f.kev
ORDER BY f.epss DESC;

// 6. Create a simple AttackPath node (called by synthesizer Bot)
MERGE (p:AttackPath {id: $pathId})
SET p.score = $score,
    p.likelihood = $likelihood,
    p.impact = $impact,
    p.description = $description,
    p.status = 'open',
    p.created_at = datetime()
WITH p
MATCH (start {id: $startId}), (end {id: $endId})
MERGE (p)-[:STARTS_AT]->(start)
MERGE (p)-[:ENDS_AT]->(end)
RETURN p;
