// Minimal Neo4j schema for Hermes SkandaShield Bots
// Run once against a fresh database (or use as reference)

// Constraints / Indexes
CREATE CONSTRAINT asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT identity_id IF NOT EXISTS FOR (i:Identity) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT finding_id IF NOT EXISTS FOR (f:Finding) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT path_id IF NOT EXISTS FOR (p:AttackPath) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT anomaly_id IF NOT EXISTS FOR (n:Anomaly) REQUIRE n.id IS UNIQUE;

CREATE INDEX asset_type IF NOT EXISTS FOR (a:Asset) ON (a.type);
CREATE INDEX finding_severity IF NOT EXISTS FOR (f:Finding) ON (f.severity);
CREATE INDEX finding_source IF NOT EXISTS FOR (f:Finding) ON (f.source);
CREATE INDEX path_score IF NOT EXISTS FOR (p:AttackPath) ON (p.score);

// Example node properties (documentation only – Neo4j is schema-optional)
// Asset: id, name, type (host|container|k8s|cloud|app|api), env, internet_facing, criticality, first_seen, last_seen, source
// Identity: id, name, type (user|service|role|group), provider (ad|entra|aws|gcp), privileged
// Finding: id, cve, title, severity, cvss, epss, kev, status, first_seen, last_seen,
//          source ('nuclei'|…), template_id, matched_at  ← nuclei-mcp upsert
// AttackPath: id, score, likelihood, impact, description, status, created_at
// Anomaly: id, type, severity, description, observed_at

// Useful relationship types
// (Asset)-[:HAS_VULN]->(Finding)
// (Identity)-[:CAN_ASSUME|MEMBER_OF|HAS_PERMISSION]->(Identity|Asset)
// (Asset)-[:CONNECTS_TO|CAN_REACH]->(Asset)
// (AttackPath)-[:STARTS_AT]->(Asset|Identity)
// (AttackPath)-[:ENDS_AT]->(Asset)
// (AttackPath)-[:INCLUDES]->(Finding|Asset|Identity)
// (Anomaly)-[:INVOLVES]->(Asset|Identity)
