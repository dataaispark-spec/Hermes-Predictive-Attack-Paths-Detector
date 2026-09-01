// Neo4j schema — Hermes SkandaShield Bots (+ AI agent attack paths)
// Run against a fresh DB or use as reference

// --- Classic constraints ---
CREATE CONSTRAINT asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT identity_id IF NOT EXISTS FOR (i:Identity) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT finding_id IF NOT EXISTS FOR (f:Finding) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT path_id IF NOT EXISTS FOR (p:AttackPath) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT anomaly_id IF NOT EXISTS FOR (n:Anomaly) REQUIRE n.id IS UNIQUE;

// --- AI agent / MITRE ---
CREATE CONSTRAINT agent_id IF NOT EXISTS FOR (ag:Agent) REQUIRE ag.id IS UNIQUE;
CREATE CONSTRAINT mcp_id IF NOT EXISTS FOR (m:MCPServer) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT tool_id IF NOT EXISTS FOR (t:Tool) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT agent_path_id IF NOT EXISTS FOR (ap:AgentAttackPath) REQUIRE ap.id IS UNIQUE;
CREATE CONSTRAINT technique_id IF NOT EXISTS FOR (t:Technique) REQUIRE t.id IS UNIQUE;

CREATE INDEX asset_type IF NOT EXISTS FOR (a:Asset) ON (a.type);
CREATE INDEX finding_severity IF NOT EXISTS FOR (f:Finding) ON (f.severity);
CREATE INDEX path_score IF NOT EXISTS FOR (p:AttackPath) ON (p.score);
CREATE INDEX agent_path_score IF NOT EXISTS FOR (ap:AgentAttackPath) ON (ap.score);
CREATE INDEX technique_framework IF NOT EXISTS FOR (t:Technique) ON (t.framework);

// Node property notes:
// Agent: id, name, exposure, privileges, internet_facing, tools[], last_seen
// MCPServer: id, name, risk, tools[]
// Tool: id, name, risk_level, allows_write, allows_exec
// AgentAttackPath: id, score, likelihood, impact, description, status, domain='ai_agent',
//                  attck_ids[], atlas_ids[], created_at
// Technique: id (T1059 | AML.T0051), framework (ATT&CK|ATLAS), name
// AttackPath (classic): may also carry attck_ids[] for hybrid paths

// Relationships:
// (Agent)-[:USES_MCP]->(MCPServer)-[:EXPOSES]->(Tool)
// (Agent)-[:CAN_INVOKE]->(Tool)
// (Agent)-[:TRUSTS|CAN_MESSAGE]->(Agent)
// (AgentAttackPath)-[:INVOLVES_AGENT]->(Agent)
// (AgentAttackPath)-[:USES_TECHNIQUE]->(Technique)
// (AgentAttackPath)-[:ENDS_AT]->(Asset)
// (AttackPath)-[:USES_TECHNIQUE]->(Technique)
// (Asset)-[:HAS_VULN]->(Finding)
