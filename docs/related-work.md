# Related Work and ESKA Positioning

Executable Semantic Knowledge Architecture (ESKA) sits at the intersection of several established research and engineering traditions: formal semantic knowledge representation, executable knowledge, Semantic Web services, ontology-driven execution, provenance and verification, and agent-accessible knowledge.

This document positions ESKA against those traditions. Its purpose is not to claim invention of executable knowledge or semantic execution. It identifies what is inherited, what is closely related, and what the current ESKA reference architecture appears to add as a synthesis and generalization.

## Positioning in one sentence

> **ESKA is not primarily an architecture for making knowledge executable. It is an architecture for keeping knowledge semantic while it becomes executable.**

The defining invariant is therefore:

> **Execution must not sever semantics.**

ESKA requires concrete execution and results to remain machine-traceable to the formal semantic knowledge and Semantic Capability that give the execution its meaning.

## Prior-art qualification

A Web, GitHub, and scholarly-oriented search performed on **2026-08-11** did not identify an independent earlier use of the exact full phrase **“Executable Semantic Knowledge Architecture”** beyond this project.

That is evidence about terminology, not a legal novelty determination. It does not establish patentability, trademark availability, or absence of unindexed prior use.

The shorter term **“Executable Knowledge Architecture” (EKA)** is already independently established and must not be claimed as original to ESKA. In particular:

- Mike Olsen published an **Executable Knowledge Architecture** framework in January 2025;
- Xiaoqi (Yasen) Zhao independently uses **Executable Knowledge Architecture (EKA)** for an ontology-, knowledge-graph-, and enterprise-architecture-oriented framework, formally described in May 2026.

The phrase **“Executable Semantic Model”** is also independently used by EnPraxis for a governed semantic core connected to runtime reasoning, orchestration, governance, agents, APIs, and applications.

## Conceptual lineage

```text
Formal semantic knowledge
RDF / OWL / SHACL / rules / decisions
            │
            ├───────────────┐
            ▼               ▼
Executable knowledge   Semantic Web services
EKM / knowledge        OWL-S / WSMO
computing / executable capability + grounding
ontologies             │
            │           │
            └─────┬─────┘
                  ▼
        Provenance / verification
               PROV-O
                  │
                  ▼
       Agent-accessible knowledge
       TWA / ontology-to-tools
                  │
                  ▼
                 ESKA
```

This is a convergence rather than a single predecessor chain. Different predecessors contribute different architectural ideas.

## Historical and contemporary neighbors

| Period | Work | Relevant contribution | Relationship to ESKA |
| --- | --- | --- | --- |
| 2004 | [OWL-S](https://www.w3.org/Submission/OWL-S/) | Ontology of services with Profile, Process Model, and Grounding; supports automated software-agent discovery, invocation, composition, and monitoring. | Direct ancestor of separating semantic service meaning from concrete invocation details. |
| 2005 | [WSMO](https://www.w3.org/submissions/WSMO/) | Ontology-backed Web Service descriptions with Capability, preconditions, assumptions, postconditions, effects, choreography, orchestration, Goals, and Mediators. | Direct ancestor of semantic Capability, applicability conditions, and operational realization. |
| 2005 | [Towards Executable Enterprise Models](https://eapad.dk/readings/journals/jea/towards-executable-enterprise-models-ontology-and-semantic-web-meet-enterprise-architecture/) | Proposed ontology- and Semantic-Web-based active or executable enterprise architectures. | Early architectural precedent for connecting formal enterprise models to execution. |
| 2006 | [SEBASTIAN Executable Knowledge Modules](https://pmc.ncbi.nlm.nih.gov/articles/PMC1560495/) | Reusable machine-executable knowledge modules declare input requirements, conclusions, and execution logic and are exposed through a standards-based Web service. | Strong domain-specific precedent for executable knowledge artifacts, service exposure, and machine-interpretable results. |
| 2011 | [OTTER](https://www.scitepress.org/PublishedPapers/2011/37193/) | Combines Enterprise Architecture, OWL ontology reasoning, and Service Component Architecture so ontology-backed EA models participate in service development and execution. | Concrete executable-enterprise-architecture implementation predecessor. |
| 2014 | [Terziyan et al., Knowledge Computing](https://journals.uran.ua/eejet/article/view/21830) | Explicitly introduces executable knowledge through an extension of RDF with executable properties and instructions for computational execution and self-management. | Important prior use and formalization of the *executable knowledge* concept. |
| 2023–24 | [OMG API4KP](https://www.omg.org/spec/API4KP/) | Standardizes APIs and ontologies for knowledge assets, knowledge platforms, operations, languages, and knowledge representation/reasoning terminology. | Close knowledge-platform and knowledge-asset standardization neighbor. |
| 2024 | [The World Avatar](https://www.nature.com/articles/s41467-023-44599-9) | Dynamic Semantic-Web knowledge graph with autonomous agents described as executable knowledge components; ontologies describe resources and agents; provenance is recorded. | One of the closest implemented system-level precedents for semantic knowledge + execution + agents + provenance. |
| 2025 | [Mike Olsen, Executable Knowledge Architecture](https://molsen.ca/writing/executable-knowledge-architecture/) | Expert intent is translated into inspectable executable artifacts, with verification, reproducibility, and governance as central concerns. | Strong verification/provenance neighbor; formal semantic representation is not its primary abstraction. |
| 2025 | [Boldachev, Executable Ontologies](https://arxiv.org/abs/2509.09775) | Semantic event models are directly interpreted as executable algorithms through a dataflow runtime. | Very close on semantic/execution continuity, but centered on one execution paradigm. |
| 2026 | [Ontology-to-tools compilation](https://arxiv.org/abs/2602.03439) | Ontological constraints are compiled into executable MCP tool interfaces and validators that constrain LLM-agent actions at runtime. | Strong precedent for agent-accessible executable semantics and semantic contracts controlling tool use. |
| 2026 | [EnPraxis, Executable Semantic Model](https://enpraxis.ai/blog/executable-semantic-model/) | A governed semantic core drives retrieval, reasoning, orchestration, governance, evaluation, agents, APIs, and applications; ontology and graph formats are treated as projections. | Very close contemporary semantic-runtime architecture, with a different source-of-truth boundary. |
| 2026 | [Xiaoqi Zhao, Executable Knowledge Architecture](https://www.linkedin.com/pulse/eka-now-formalized-introducing-chapter-0-pizzaowl-ontology-zhao-zjjxc) | Formal EKA framing connects ontology engineering, knowledge graphs, executable intelligence, and enterprise architecture. | Closest naming and semantic-engineering neighbor to ESKA. |
| 2026 | [Knowledge-Centric Information Systems](https://arxiv.org/abs/2607.02609) | Positions organizational knowledge as executable infrastructure used by humans, agents, workflows, and models, with provenance and operational delivery as architectural concerns. | Parallel convergence at the knowledge-architecture level. |

## Foundations ESKA deliberately reuses

ESKA builds on existing semantic and provenance standards rather than treating the neighboring work above as a replacement vocabulary.

Formal semantics come from the semantic artifacts themselves: OWL axioms, SHACL constraints, SPARQL rules, DMN decisions, OpenMath calculations, semantic mappings, BPMN workflows, and related source vocabularies.

For provenance, ESKA reuses [PROV-O](https://www.w3.org/TR/prov-o/) instead of introducing a parallel provenance model:

```text
Execution    ⊆ prov:Activity
Verification ⊆ prov:Activity
Result       ⊆ prov:Entity
```

This reuse is part of the architecture: ESKA should own only semantics that are genuinely specific to executable semantic knowledge architecture.

## Closest architectural precedents

### OWL-S and WSMO: capability versus realization

OWL-S and WSMO are foundational precedents for the idea that software agents should discover and invoke functionality from machine-interpretable semantic descriptions rather than from undocumented endpoint knowledge.

OWL-S separates what a service does and how it behaves from its concrete Grounding. WSMO models a Web Service Capability separately from its interfaces, choreography, and orchestration.

ESKA generalizes that architectural separation beyond Web services:

```text
SemanticCapability
    what the ability means
        ↓
KnowledgeService / ServiceOperation
    stable operational exposure
        ↓
AccessBinding
    concrete access contract
        ↓
SemanticInvocationAdapter
    request/result representation

separate runtime concern:

ServiceDeployment
        ↓
DeploymentBinding
```

The separation is therefore not claimed as new. ESKA's contribution is applying the same semantic-continuity discipline consistently across multiple executable-semantic modes and keeping deployment location outside stable semantic meaning.

### Executable knowledge modules and Knowledge Computing

SEBASTIAN demonstrates that knowledge can be modular, machine executable, service-accessible, versioned, and reusable independently from consuming applications.

Terziyan et al. go further conceptually by explicitly naming **executable knowledge** and extending an RDF-based knowledge model with executable properties.

These are clear predecessors to ESKA's use of the term *Executable Semantic Knowledge Artifact*. ESKA differs by not defining a single universal representation or executable property. Instead, execution is polymorphic according to semantic type.

### The World Avatar: executable knowledge components and agents

The World Avatar is particularly important because it combines:

- Semantic Web ontologies;
- a dynamic knowledge graph;
- autonomous computational agents;
- ontological descriptions of agents;
- agent discovery/composition;
- execution that changes the graph or external world;
- recorded provenance.

This is one of the strongest system-level precedents for ESKA.

ESKA abstracts the executable unit differently. A software agent is only one possible operational actor. The semantic knowledge being operationalized may instead be an ontology, constraint, rule, decision, calculation, mapping, or workflow, with the corresponding operation determined by that artifact's semantics.

### Executable Ontologies: direct semantic execution

Boldachev's executable-ontology approach is especially close to ESKA's semantic-continuity principle because semantic models directly control process execution.

The main distinction is scope. Executable Ontologies define a specific event-semantic/dataflow execution architecture. ESKA intentionally avoids one universal execution runtime and instead tests whether one cross-mode semantic contract can survive materially different execution technologies.

### Ontology-to-tools: semantic control of agents

The World Avatar ontology-to-tools work compiles an ontology T-Box into executable MCP interfaces and validators. The generated tool contract constrains what an LLM agent can create or modify and returns structured feedback for repair.

This strongly supports ESKA's premise that agent accessibility can be derived from machine-interpretable semantic contracts rather than reconstructed from free-form prompts.

ESKA differs by keeping the deterministic architecture independent from LLM use and by modeling the discovered Semantic Capability, invocation representation, execution, result, and verification as separate concerns.

## The two independent EKA frameworks

### Mike Olsen — Executable Knowledge Architecture

Olsen's EKA addresses a verification problem in professional AI use:

```text
expert intent
    ↓
AI translation
    ↓
executable artifact
    ↓
human verification
    ↓
reproducible result
```

The strongest overlap with ESKA is the insistence that execution be inspectable, reproducible, and verifiable rather than treating an AI answer as an oracle result.

The primary difference is where semantics live. Olsen's executable artifact is normally code derived from expert intent. ESKA requires formal machine-interpretable semantics to remain explicit and traceable through execution rather than relying on expert intent plus generated code as the central representation.

### Xiaoqi Zhao — Executable Knowledge Architecture

Zhao's EKA is the closest terminology and semantic-engineering neighbor. It explicitly connects ontology engineering, knowledge graphs, enterprise architecture, and executable intelligence, and it uses the Pizza ontology as an educational vehicle.

That makes it important prior work for ESKA to acknowledge directly.

The current ESKA distinction is not the phrase *Executable Knowledge Architecture*. It is the more specific cross-mode architecture and semantic-continuity contract:

```text
SemanticModel
        ↓
ExecutableSemanticKnowledgeArtifact
        ↓
SemanticCapability
        ↓
ApplicabilityCondition
        ↓
Execution
        ↓
Result
        ↓
Verification
```

ESKA should therefore position itself as adjacent to Zhao's EKA, not as its renaming or replacement.

## EnPraxis Executable Semantic Model

EnPraxis's ESM is a close contemporary neighbor because it explicitly makes a governed semantic core operational. Its stated stack connects business meaning to reasoning, orchestration, governance, evaluation, agents, APIs, retrieval, and applications.

A significant architectural difference is source ownership. EnPraxis treats RDF, OWL, SKOS, SHACL, graph schemas, API contracts, prompts, and similar artifacts as downstream projections of its canonical Executable Semantic Model.

ESKA instead permits source-owned formal semantic artifacts to remain authoritative in their native semantic form and requires the execution architecture not to become their accidental owner.

For ESKA:

```text
domain semantic source
        ↓ immutable identity
formal semantic artifact
        ↓ operationalized as
SemanticCapability / Execution
        ↓
Result / Verification / PROV-O lineage
```

That distinction is central to the Pizza reference, where `pizza-ontology` owns the semantic artifacts and ESKA owns the execution architecture.

## ESKA's cross-mode hypothesis

The most distinctive implemented ESKA hypothesis is that **execution is polymorphic**:

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
Workflow    → execute
Capability  → invoke
```

An ontology need not be converted into imperative code to become operational. A SHACL shape is executable by validation; a DMN model by decision evaluation; an OpenMath expression by calculation; a mapping by transformation.

ESKA therefore asks a different question from many executable-model approaches:

> Can materially different semantic artifacts participate in execution while retaining one common machine-interpretable contract for meaning, applicability, execution, result, verification, and provenance?

The current Pizza reference provides executable evidence for seven materially different semantic modes without changing `model/eska-core.ttl`.

## Comparison of the closest neighbors

Legend: **●** central, **◐** present or partial, **○** not central to the referenced work.

| Work | Formal semantics | Executable knowledge | Semantic capability / conditions | Explicit result / verification | Provenance | Agent/service accessibility | Multiple execution modes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OWL-S | ● | ◐ | ● | ◐ | ○ | ● | ○ |
| WSMO | ● | ◐ | ● | ◐ | ○ | ● | ○ |
| SEBASTIAN EKM | ◐ | ● | ◐ | ● | ◐ | ● | ◐ |
| Terziyan Knowledge Computing | ● | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| API4KP | ● | ● | ● | ◐ | ◐ | ● | ● |
| The World Avatar | ● | ● | ● | ◐ | ● | ● | ◐ |
| Olsen EKA | ○ | ● | ◐ | ● | ● | ◐ | ◐ |
| Executable Ontologies | ● | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| Ontology-to-tools | ● | ● | ● | ● | ◐ | ● | ○ |
| EnPraxis ESM | ● | ● | ● | ● | ● | ● | ● |
| Zhao EKA | ● | ● | ● | ◐ | ◐ | ● | ◐ |
| ESKA | ● | ● | ● | ● | ● | ● | ● |

The table is qualitative positioning, not a benchmark. A circle does not mean a work is incapable of a feature; it means the feature is not a central architectural concern in the cited material.

## What ESKA should and should not claim

ESKA should **not** claim invention of:

- executable knowledge;
- executable ontologies;
- ontology-driven execution;
- semantic service discovery or invocation;
- semantic capability modeling;
- provenance-aware knowledge systems;
- agent-accessible ontologies or knowledge graphs;
- the term Executable Knowledge Architecture.

The defensible ESKA contribution is the combination of the following architectural properties:

1. **Polymorphic execution semantics** — executable means reason, validate, evaluate, decide, calculate, transform, execute, or invoke according to semantic type rather than simply “generate/run code.”
2. **One cross-mode semantic contract** — materially different execution technologies share `SemanticModel → ExecutableSemanticKnowledgeArtifact → SemanticCapability → ApplicabilityCondition → Execution → Result → Verification`.
3. **Semantic continuity as an invariant** — concrete execution remains linked to the semantic artifact and Capability that explain what the execution means.
4. **Provenance through execution** — results remain traceable through PROV-O to immutable semantic source artifacts.
5. **Meaning separated from operational realization** — Capability, Service/Operation, access binding, invocation representation, and Deployment are different architectural concerns.
6. **Agent accessibility from explicit contracts** — a deterministic agent can discover and invoke compatible capabilities without reconstructing their meaning from prompts.
7. **Explicit semantic-source ownership** — the execution architecture must not become the accidental owner of domain semantics.

These are **observed differentiators from the reviewed related work**, not claims of exhaustive worldwide novelty.

## Proposed contribution statement

A conservative project-level contribution statement is:

> **Executable Semantic Knowledge Architecture (ESKA) synthesizes established ideas from formal semantic knowledge representation, executable knowledge, Semantic Web services, provenance, verification, and agent-accessible knowledge into a technology-neutral reference architecture whose defining invariant is semantic continuity between formal knowledge and its execution.**

The shorter architectural thesis is:

> **ESKA keeps execution connected to meaning.**

## Research boundary

This related-work review is intentionally architectural rather than exhaustive. It prioritizes works that materially overlap with at least two of ESKA's concerns: formal semantics, executable knowledge, capability contracts, runtime execution, provenance/verification, and agent/service accessibility.

Future related-work additions should strengthen or falsify the contribution statement. They should not cause ESKA core vocabulary to grow merely because a neighboring architecture has more concepts.