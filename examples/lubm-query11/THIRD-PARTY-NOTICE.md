# Third-party provenance — LUBM UBA implementation backend

This ESKA example does **not** vendor the LUBM UBA generator source.

GitHub Actions checks out the public implementation repository at a pinned commit:

```text
repository  rvesse/lubm-uba
commit      48686cd616f564c8fc360dc5abbcc294678655c4
```

## Role

The pinned repository is used only as a replaceable data-generation implementation backend.

It is not treated as:

- LUBM semantic authority;
- the ontology identity;
- the query oracle;
- Lehigh benchmark governance.

The authoritative benchmark definition, query semantics and expected-answer evidence remain the Lehigh SWAT LUBM materials cited in `README.md` and `benchmark-contract.json`.

## Provenance

The pinned repository's README states that it is the original LUBM UBA generator rewritten/refactored for a stronger CLI and scalability while keeping generated-data behavior identical. It also describes `compareOutput.sh` as a check between original and rewritten generated output.

The original generator source files retain Lehigh SWAT attribution to Yuanbo Guo and declare GNU General Public License version 2 or, at the recipient's option, any later version.

## Repository license boundary

The ESKA repository's own license does not relicense the externally checked-out generator.

Anyone reusing or redistributing that third-party implementation must comply with its own licensing terms.
