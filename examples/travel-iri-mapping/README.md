# Travel ontology identity across physical backends

This example is an independent proving ground for ESKA #79.

It tests one architectural claim:

> A semantic ontology identity can remain stable while its physical retrieval backend and serialization change.

## Historical basis

Protégé documentation distinguishes the **ontology name/identity** from the **physical document location** for the historical Travel ontology.

The documented ontology identity is:

```text
http://www.owl-ontologies.com/travel.owl
```

Protégé examples loaded Travel from physical locations including:

```text
http://protege.cim3.net/file/pub/ontologies/travel/travel.owl
http://protege.stanford.edu/junitOntologies/testset/travel.owl
```

Protégé's import documentation explicitly explains that the Stanford document can contain an ontology named `http://www.owl-ontologies.com/travel.owl` even though the document itself was retrieved from a different URL. It also describes the resulting strict-import mismatch and Protégé's pragmatic import/fix-up behavior.

Primary references:

- https://protegewiki.stanford.edu/wiki/Importing_Ontologies_in_P41
- https://protegewiki.stanford.edu/wiki/How_Owl_Imports_Work
- https://protegewiki.stanford.edu/wiki/How_Owl_2.0_Imports_Work
- https://protegewiki.stanford.edu/wiki/ProtegeOWL_API_Basics
- https://protegewiki.stanford.edu/wiki/BuildingSemanticWebApplications

The Protégé API documentation also uses the globally identified resource `http://www.owl-ontologies.com/travel.owl#Destination`, and the Semantic Web application documentation describes Travel as containing concepts such as `Activity` and `Destination`.

## Authority boundary

The files in `backends/` are **clean-room minimal test slices**. They are not copies, repairs, successors, or authoritative republished versions of the historical Protégé Travel ontology.

They preserve only:

- the historical ontology identity needed for the test;
- two historically documented resource identities, `travel:Activity` and `travel:Destination`.

No claim is made that the local slices reproduce the full historical ontology semantics.

## Physical backends

The same semantic identity is represented through two deliberately different physical arrangements:

```text
backend A
  backends/a/travel.ttl
  Turtle

backend B
  backends/b/nested/reference.rdf
  RDF/XML
```

`catalog-a.json` and `catalog-b.json` both map:

```text
http://www.owl-ontologies.com/travel.owl
```

to their respective physical artifact.

The semantic identity does not become either repository path.

## Normalized result

Both backends must produce exactly:

```json
{
  "semanticIdentity": "http://www.owl-ontologies.com/travel.owl",
  "selectedClasses": [
    "http://www.owl-ontologies.com/travel.owl#Activity",
    "http://www.owl-ontologies.com/travel.owl#Destination"
  ]
}
```

## Required controls

The verifier demonstrates:

1. semantic identity → backend A → normalized result R;
2. semantic identity → backend B → normalized result R;
3. backend A and B differ physically and by serialization while R remains identical;
4. an unmapped semantic identity fails deterministically;
5. a physical backend that declares the wrong ontology identity fails deterministically.

Run:

```bash
python -m pip install -r examples/travel-iri-mapping/requirements.txt
python examples/travel-iri-mapping/verify.py
```

## ESKA mapping

`architecture.ttl` uses only existing ESKA and PROV-O semantics:

- historical Travel identity → `eska:SemanticModel`;
- identity-aware access → `eska:SemanticCapability`;
- catalog configuration → `eska:ExecutableSemanticKnowledgeArtifact`;
- each lookup → `eska:Execution`;
- normalized observation → `eska:Result`;
- backend/identity equivalence checks → `eska:Verification`;
- physical files → PROV-O runtime entities used by the executions.

No new ESKA vocabulary is introduced.

## Architectural result

A successful run demonstrates:

```text
stable semantic identity
        ↓
replaceable mapping/catalog
        ↓
physical Turtle backend ─┐
                         ├─ same normalized semantic Result
physical RDF/XML backend ┘
        ↓
Verification
```

Physical location and serialization are execution details. They do not become the ontology's semantic authority.
