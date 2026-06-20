## Changes

<!-- Describe what this PR does and why -->

-

## Checklist

- [ ] `py scripts/validate_structure.py` passes (if ontology/structure changes)
- [ ] Relationships explicit: typed party/location roles declare a generic
      parent via `rdfs:subPropertyOf`; entity references modeled as object
      properties, not bare `*Ref`/`*Id` scalars (review any `⚠` validator hints)
- [ ] Ontology version bumped + old version archived (if ontology content changed)
- [ ] DCO sign-off on all commits (`git commit -s`)
- [ ] No secrets, credentials, or PII in ontology labels, comments, or fixtures
- [ ] No proprietary or client-specific content
