# Full starter Rego package for the five Hermes SkandaShield Bots
# Package: skandashield.authz
# Default deny. Load into OPA and query: POST /v1/data/skandashield/authz

package skandashield.authz

import future.keywords.if
import future.keywords.in

# ---------- Default deny ----------
default allow := false
default reason := "denied by default policy"

# ---------- Helper sets ----------
read_only_tools := {
    "neo4j.get_neo4j_schema",
    "neo4j.read_neo4j_cypher",
    "nuclei_scan",
}

write_tools := {
    "neo4j.write_neo4j_cypher",
}

ticket_tools := {
    "jira.create_issue",
    "jira.update_issue",
    "servicenow.create_incident",
}

destructive_cypher_keywords := {"DELETE", "DROP", "DETACH", "REMOVE", "FOREACH"}

trusted_reader_bots := {
    "asset-identity-mapper",
    "vuln-triage",
    "attack-path-synthesizer",
    "anomaly-detector",
    "remediation-guidance",
}

# ---------- Rule 1: Read-only tools allowed for any trusted Bot ----------
allow if {
    input.tool in read_only_tools
    input.bot in trusted_reader_bots
}

reason := "read-only tool allowed for trusted bot" if {
    input.tool in read_only_tools
    input.bot in trusted_reader_bots
}

# ---------- Rule 2: Graph writes – only trusted writers, no destructive keywords ----------
allow if {
    input.tool in write_tools
    input.bot == "attack-path-synthesizer"
    not is_destructive_cypher(input.args.query)
}

reason := "graph write allowed for attack-path-synthesizer (non-destructive)" if {
    input.tool in write_tools
    input.bot == "attack-path-synthesizer"
    not is_destructive_cypher(input.args.query)
}

allow if {
    input.tool in write_tools
    input.bot == "asset-identity-mapper"
    not is_destructive_cypher(input.args.query)
}

reason := "graph write allowed for asset-identity-mapper (non-destructive)" if {
    input.tool in write_tools
    input.bot == "asset-identity-mapper"
    not is_destructive_cypher(input.args.query)
}

# ---------- Rule 3: Ticket / remediation actions require explicit human approval ----------
allow if {
    input.tool in ticket_tools
    input.bot == "remediation-guidance"
    input.context.human_approved == true
}

reason := "ticket creation allowed after human approval" if {
    input.tool in ticket_tools
    input.bot == "remediation-guidance"
    input.context.human_approved == true
}

# ---------- Rule 4: High-severity scan only when justified ----------
allow if {
    input.tool == "nuclei_scan"
    input.bot == "vuln-triage"
    true
}

# ---------- Helpers ----------
is_destructive_cypher(query) if {
    some kw in destructive_cypher_keywords
    contains(upper(query), kw)
}

upper(s) := result if {
    result := upper(s)
} else := s
