// Example queries — AI agent attack paths + MITRE

// Top agent paths by score
MATCH (ap:AgentAttackPath)
RETURN ap.id AS id, ap.score AS score, ap.description AS description,
       ap.attck_ids AS attck, ap.atlas_ids AS atlas
ORDER BY ap.score DESC LIMIT 20;

// Paths involving a critical-privilege agent
MATCH (ap:AgentAttackPath)-[:INVOLVES_AGENT]->(ag:Agent)
WHERE ag.privileges = 'critical'
RETURN ap, ag;

// All techniques used by agent paths
MATCH (ap:AgentAttackPath)-[:USES_TECHNIQUE]->(t:Technique)
RETURN t.id, t.framework, count(ap) AS path_count
ORDER BY path_count DESC;

// Hybrid: agent path that also touches a classic asset (when linked)
MATCH (ap:AgentAttackPath)-[:ENDS_AT]->(a:Asset)
RETURN ap.id, a.name, a.criticality, ap.score
ORDER BY ap.score DESC;

// Prompt-injection related techniques
MATCH (t:Technique)
WHERE t.id IN ['AML.T0051', 'AML.T0054', 'T1059']
OPTIONAL MATCH (ap)-[:USES_TECHNIQUE]->(t)
RETURN t.id, collect(DISTINCT ap.id) AS paths;
