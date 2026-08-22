package skandashield.authz_test

import data.skandashield.authz

# Read-only tool allowed
test_read_allowed if {
    authz.allow with input as {
        "bot": "vuln-triage",
        "tool": "neo4j.read_neo4j_cypher",
        "args": {},
        "context": {},
    }
}

# Ticket without approval denied
test_ticket_denied_without_approval if {
    not authz.allow with input as {
        "bot": "remediation-guidance",
        "tool": "jira.create_issue",
        "args": {},
        "context": {"human_approved": false},
    }
}

# Ticket with approval allowed
test_ticket_allowed_with_approval if {
    authz.allow with input as {
        "bot": "remediation-guidance",
        "tool": "jira.create_issue",
        "args": {},
        "context": {"human_approved": true},
    }
}

# Destructive cypher denied
test_destructive_write_denied if {
    not authz.allow with input as {
        "bot": "attack-path-synthesizer",
        "tool": "neo4j.write_neo4j_cypher",
        "args": {"query": "MATCH (n) DETACH DELETE n"},
        "context": {},
    }
}
