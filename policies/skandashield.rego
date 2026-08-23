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
}

# nuclei_scan is intentionally NOT in the generic read_only set — dedicated rules below
nuclei_tools := {"nuclei_scan"}

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

# Only these bots may invoke Nuclei
nuclei_allowed_bots := {
	"vuln-triage",
	"asset-identity-mapper",
}

# Severities allowed without human_approved (gateway should pass context)
nuclei_safe_severities := {"info", "low", "medium"}
nuclei_elevated_severities := {"high", "critical"}

# ---------- Rule 1: Read-only graph tools for any trusted Bot ----------
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
	not is_destructive_cypher(object.get(input, ["args", "query"], ""))
}

reason := "graph write allowed for attack-path-synthesizer (non-destructive)" if {
	input.tool in write_tools
	input.bot == "attack-path-synthesizer"
	not is_destructive_cypher(object.get(input, ["args", "query"], ""))
}

allow if {
	input.tool in write_tools
	input.bot == "asset-identity-mapper"
	not is_destructive_cypher(object.get(input, ["args", "query"], ""))
}

reason := "graph write allowed for asset-identity-mapper (non-destructive)" if {
	input.tool in write_tools
	input.bot == "asset-identity-mapper"
	not is_destructive_cypher(object.get(input, ["args", "query"], ""))
}

# ---------- Rule 3: Ticket / remediation actions require explicit human approval ----------
allow if {
	input.tool in ticket_tools
	input.bot == "remediation-guidance"
	object.get(input, ["context", "human_approved"], false) == true
}

reason := "ticket creation allowed after human approval" if {
	input.tool in ticket_tools
	input.bot == "remediation-guidance"
	object.get(input, ["context", "human_approved"], false) == true
}

# ---------- Rule 4a: nuclei_scan — safe severities, allow-listed bots ----------
allow if {
	input.tool in nuclei_tools
	input.bot in nuclei_allowed_bots
	nuclei_severities_ok_safe
	not nuclei_requires_human
}

reason := "nuclei_scan allowed for triage/mapper with safe severity" if {
	input.tool in nuclei_tools
	input.bot in nuclei_allowed_bots
	nuclei_severities_ok_safe
	not nuclei_requires_human
}

# ---------- Rule 4b: nuclei_scan — elevated severity or production scope needs human_approved ----------
allow if {
	input.tool in nuclei_tools
	input.bot in nuclei_allowed_bots
	nuclei_requires_human
	object.get(input, ["context", "human_approved"], false) == true
}

reason := "nuclei_scan elevated/production allowed after human approval" if {
	input.tool in nuclei_tools
	input.bot in nuclei_allowed_bots
	nuclei_requires_human
	object.get(input, ["context", "human_approved"], false) == true
}

# ---------- Nuclei helpers ----------

# severity list from args (default empty => treat as safe)
nuclei_requested_severities := sevs if {
	sevs := {lower(s) | s := input.args.severity[_]}
} else := sevs if {
	sevs := {lower(s) | s := input.args.severities[_]}
} else := set()

nuclei_severities_ok_safe if {
	count(nuclei_requested_severities) == 0
}

nuclei_severities_ok_safe if {
	count(nuclei_requested_severities) > 0
	nuclei_requested_severities_subset_safe
}

nuclei_requested_severities_subset_safe if {
	every s in nuclei_requested_severities {
		s in nuclei_safe_severities
	}
}

nuclei_has_elevated_severity if {
	some s in nuclei_requested_severities
	s in nuclei_elevated_severities
}

# Gateway may set context.scope = "production" | "staging" | "lab"
nuclei_requires_human if {
	nuclei_has_elevated_severity
}

nuclei_requires_human if {
	object.get(input, ["context", "scope"], "lab") == "production"
}

# Explicit deny reason for wrong bot calling nuclei
reason := "nuclei_scan denied: bot not in nuclei_allowed_bots" if {
	input.tool in nuclei_tools
	not input.bot in nuclei_allowed_bots
}

reason := "nuclei_scan denied: elevated severity or production scope requires human_approved" if {
	input.tool in nuclei_tools
	input.bot in nuclei_allowed_bots
	nuclei_requires_human
	object.get(input, ["context", "human_approved"], false) != true
}

# ---------- Helpers ----------
is_destructive_cypher(query) if {
	some kw in destructive_cypher_keywords
	contains(upper(query), kw)
}

upper(s) := u if {
	u := upper(s)
} else := s

lower(s) := l if {
	l := lower(s)
} else := s
