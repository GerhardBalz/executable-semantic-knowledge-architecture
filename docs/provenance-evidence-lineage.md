# Provenance, Evidence, and Result Lineage

ESKA uses **PROV-O and Dublin Core Terms as the provenance vocabulary** and keeps only the execution-specific semantic links in the ESKA core.

This decision is evidence-driven. The executable Pizza reference now spans seven execution modes, composite Workflow execution, generalized Knowledge Service / Agent invocation, semantic invocation adapters, and multiple runtime deployments. Across that diversity, the existing vocabularies are sufficient to express the required trust and lineage relationships.

No parallel ESKA `Evidence`, `ProvenanceRecord`, or `Lineage` hierarchy is currently justified.

## The common lineage chain

For a semantic execution, the expected minimum chain is:

```text
Semantic Capability
        ↑ executesCapability
Execution
    ├── usesSemanticModel
    ├── usesExecutableArtifact
    ├── prov:used source/input evidence
    ├── prov:wasAssociatedWith SoftwareAgent
    ├── prov:endedAtTime
    └── generatesResult / prov:generated
                ↓
              Result
                ├── prov:wasGeneratedBy Execution
                └── prov:wasDerivedFrom source/input lineage

Verification
    ├── verifiesExecution → Execution
    ├── verifiesResult    → Result
    ├── prov:used         → Result
    └── prov:endedAtTime
```

This combines:

- **ESKA** for the semantic execution contract;
- **PROV-O** for activity/entity/agent provenance and derivation;
- **dcterms** for identifiers, source locations, conformance, and semantic relations.

## Semantic execution lineage profile

[`examples/pizza/verify-provenance-lineage.py`](../examples/pizza/verify-provenance-lineage.py) verifies the profile across all **sixteen core Executions**:

```text
1 OWL reasoning execution
2 SHACL validation executions
1 SPARQL rule execution
3 DMN decision executions
3 OpenMath calculation executions
1 semantic Mapping execution
2 overall Workflow executions
3 Workflow child-step executions
```

Every Execution must have:

- exactly one executed Semantic Capability;
- at least one Semantic Model;
- at least one Executable Semantic Knowledge Artifact;
- at least one `prov:used` evidence/input resource;
- an associated `prov:SoftwareAgent`;
- one typed `xsd:dateTime` end time;
- exactly one generated ESKA Result in the current reference cases.

Every Result must:

- be both `eska:Result` and `prov:Entity`;
- be linked bidirectionally to its Execution through `eska:generatesResult` / `prov:generated` and `prov:wasGeneratedBy`;
- have explicit `prov:wasDerivedFrom` lineage;
- recursively trace to at least one immutable source URL of the form:

```text
https://github.com/GerhardBalz/pizza-ontology/blob/<40-hex-commit>/...
```

Every Verification must:

- be both `eska:Verification` and `prov:Activity`;
- identify the Execution and Result it checks;
- explicitly `prov:used` that Result;
- record an `xsd:dateTime` end time.

## Immutable source evidence

Different modes express source lineage differently, but they converge on the same trust property.

### Reasoning

```text
Result
    → prov:wasDerivedFrom
source-owned reasoning-module entity
    → dcterms:source
immutable Pizza Git blob
```

### Validation

```text
ValidationReport
    ├── prov:wasDerivedFrom → Pizza Shapes entity
    └── prov:wasDerivedFrom → Pizza input-data entity
                                  ↓ dcterms:source
                             immutable Git blob
```

### Rule / Decision / Calculation / Mapping

Their Results use direct `prov:wasDerivedFrom` links to the commit-pinned source artifacts that materially determine the Result.

### Workflow

Child Results derive directly from the source input plus the SHACL or Mapping artifact they use. Overall Workflow Results derive from child Results:

```text
Workflow Result
    → prov:wasDerivedFrom
Step Result
    → prov:wasDerivedFrom
immutable source artifacts
```

The verifier follows this chain recursively.

## Tool and software identity

Executions identify the software/tool Agent that performed them through `prov:wasAssociatedWith`.

The reference records versions where they matter for reproducibility, for example:

- ROBOT + HermiT;
- pySHACL;
- RDFLib;
- the canonical DMN evaluator;
- the OpenMath subset evaluator;
- the BPMN Workflow evaluator with pySHACL/RDFLib versions.

This remains ordinary PROV-O `SoftwareAgent` metadata rather than a new ESKA tool hierarchy.

## Role-specific provenance

Some modes require more precise provenance than the generic profile.

Mapping already demonstrates qualified PROV-O usage with `prov:Role` for:

```text
Source Semantic Model
Mapping Semantic Model
Target Semantic Model
```

Workflow adds ordinary composition and dependency relationships:

```text
dcterms:hasPart / dcterms:isPartOf
prov:wasInformedBy
prov:wasDerivedFrom
```

These are retained as refinements rather than promoted into a second provenance model.

## Operational invocation lineage profile

Knowledge Agent invocation adds operational context that is intentionally separate from the semantic execution source profile.

The generalized Agent now creates **five distinct invocation identities** for the blue/green reference cases. Invocation identity is deterministic over:

```text
Semantic Capability
+
Service Deployment
+
invocation input identity
```

This prevents a merged provenance graph from accidentally conflating two executions merely because they use the same semantic mode.

For each invocation, the verifier requires:

```text
Execution
    ├── executesCapability
    ├── prov:used KnowledgeService
    ├── prov:used SemanticInvocationAdapter
    ├── prov:used ServiceDeployment
    ├── prov:used DeploymentEnvironment
    ├── prov:used HTTPDeploymentBinding
    ├── prov:used invocation input
    ├── prov:used architecture model
    ├── prov:used deployment model
    └── prov:wasAssociatedWith KnowledgeAgent
              ↓
            Result
              └── prov:wasDerivedFrom invocation input
```

This distinguishes two independent questions:

```text
What semantic operation produced this Result?
    → Capability / Service / Adapter

Where did this invocation execute?
    → ServiceDeployment / Environment / DeploymentBinding
```

Both remain traceable without putting deployment location into the Semantic Capability or Service contract.

## A defect found by the lineage work

Before this profile was introduced, the five generalized-Agent provenance files used only two Execution IRIs:

```text
...:classification:execution
...:validation:execution
```

The files were valid independently, but merging blue/green or multiple validation invocations would have conflated distinct runtime activities.

The invocation runtime now derives unique provenance IRIs from Capability + concrete deployment + input identity. The regression verifies that all five invocation Executions remain distinct when considered together.

This is an example of why provenance completeness is not merely documentation: the trust-plane verifier exposed an identity defect that ordinary functional tests did not.

## What ESKA does not add

The current evidence does **not** justify new classes such as:

```text
eska:Evidence
eska:ProvenanceRecord
eska:Lineage
eska:SourceArtifact
eska:ToolExecution
```

Nor does it justify duplicating PROV-O properties with ESKA-specific equivalents.

The current principle is:

> **Use ESKA to describe the semantic execution contract; use PROV-O to describe what happened and how entities/activities/agents are related; use dcterms for stable identification and source metadata.**

New ESKA provenance terms should be introduced only when an executable case exposes a semantic requirement that those established vocabularies cannot express clearly.

## Run

The provenance verifier runs as part of the final Pizza reference CI checkpoint after all semantic modes and generalized Agent invocations have produced their provenance graphs.

It can also be run directly after the reference artifacts exist:

```bash
python examples/pizza/verify-provenance-lineage.py
```

Expected summary:

```text
Semantic execution lineage:     16 Executions
Operational invocation lineage:  5 Executions
Immutable source trace:          every semantic Result reaches pizza-ontology@commit
Operational context:             Service + adapter + deployment + environment + binding + input
```
