# Development Roadmap: Multiaxial Diagnostic Expert System V8 -> V9

**Date:** 2026-02-10
**Basis:** Review_Multiaxiale_Diagnostik.tex (V3) vs. multiaxial_diagnostic_system.py (V8)
**Source 2:** Clinical documents from _Arztsachen (Case-based evaluation, Synopsis, Literature review)

---

## Phase 1: Paper Alignment (Priority CRITICAL) -- COMPLETED

### 1.1 Correct Ii/Ij Order -- DONE
- **What:** Coverage analysis becomes Ii, investigation plan becomes Ij
- **Where:** translations.json (DE + EN), multiaxial_diagnostic_system.py (tab_plan order)

### 1.2 HiTOP Spectra Radar from Cross-Cutting Data -- DONE
- **What:** Automatically compute 6 HiTOP spectra from cross-cutting results
- **Mapping:**
  - Internalizing = max(Depression, Anxiety, Somatic, Sleep)
  - Thought Disorder = max(Psychosis, Dissociation)
  - Disinhibited Externalizing = max(Substance, Mania)
  - Antagonistic Externalizing = max(Anger)
  - Detachment = max(Detachment/Memory)
  - Somatoform = max(Somatic)

### 1.3 Axis III: Symmetric Extension (13 Sub-axes) -- DONE
- **What:** Extend Axis III from 3 tabs to 13 sub-axes (IIIa-IIIm)

---

## Phase 1b: Clinical Document Integration (Priority CRITICAL) -- COMPLETED

### 1b.1 PRO/CONTRA Evidence Evaluation per Diagnosis -- DONE
- **What:** Each diagnosis gets a confidence slider (0-100%), severity selection, PRO/CONTRA free text
- **Where:** Gate 5 diagnosis form extended, Diagnosis dataclass with confidence_pct, severity, evidence_pro, evidence_contra
- **Source:** CASE-BASED EVALUATION document

### 1b.2 Quantitative Symptom Coverage (~88% Metric) -- DONE
- **What:** Structured symptom-diagnosis matrix with coverage percentage per symptom
- **Where:** Axis I Tab Ii (Coverage Analysis) with form + metrics (Complete/Partial/Insufficient)
- **Source:** SYNOPSIS_VALIDATED document

### 1b.3 Prioritized Investigation Plan (Urgent/Important/Monitoring) -- DONE
- **What:** Structured investigation planning with 3-tier prioritization and specialty
- **Where:** Axis I Tab Ij (Investigation Plan) with form + tabular display
- **Source:** CASE-BASED EVALUATION + SYNOPSIS_VALIDATED

### 1b.4 CAVE Clinical Alerts -- DONE
- **What:** Critical warnings (lab artifacts, drug interactions, contraindications, etc.)
- **Where:** Axis VI Evidence Collection (input) + Synopsis (red display)
- **Categories:** Drug interaction, Lab artifact, Contraindication, Temporal misattribution, Diagnostic limitation, Other

### 1b.5 Longitudinal Symptom Timeline -- DONE
- **What:** Tracking symptoms over time (onset, current status, therapy response)
- **Where:** Axis VI Evidence Collection (input) + Synopsis (table)

### 1b.6 Extended Medication Form (IIIm) -- DONE
- **What:** Additional fields: Unit, Purpose/Indication, Time of intake, Efficacy rating (0-10)
- **Where:** Axis III Tab IIIm
- **Source:** Medication overview PDF

### 1b.7 JSON Export Updated -- DONE
- **What:** cave_alerts, symptom_coverage, investigation_plans, symptom_timeline in export

---

## Phase 1c: Design Philosophy & Process Documentation -- COMPLETED

### 1c.1 Design Philosophy in Paper -- DONE
- **What:** New section 1.1 "Design Philosophy: Skeleton, Living Document, Maximum Freedom"
- **Three Principles:** Skeleton principle (structure without mandatory fields), Living document (growing patient record), Report as snapshot
- **Where:** Paper after introduction, before architecture section

### 1c.2 Axis II: Formative Experiences & Core Conflicts -- DONE
- **What:** New tabs in Axis II: Formative Experiences (description, life stage, impact), Core Conflicts (conflict, description)
- **Where:** multiaxial_diagnostic_system.py (4 tabs instead of 2), translations.json (DE + EN), Synopsis, Export, Paper

### 1c.3 Axis IV: Contact Persons & Treatment Network -- DONE
- **What:** Structured contact register (name, role, institution, phone, notes)
- **Where:** multiaxial_diagnostic_system.py Axis IV, translations.json, Synopsis, Export, Paper

### 1c.4 Axis VI: Assessment Field in Evidence Matrix -- DONE
- **What:** New field "Clinical Assessment" in evidence form
- **Use case:** Lab report received -> physician documents assessment + axis reference

### 1c.5 Axis VI: Contact & Observation Protocol -- DONE
- **What:** Structured protocol (date, contact type, person, content, axis reference)
- **Contact types:** Phone call, Conversation, Observation, Home visit, Collateral history, E-mail/Letter, Other
- **Where:** multiaxial_diagnostic_system.py Axis VI, translations.json, Synopsis, Export, Paper

### 1c.6 Paper V4 -> V5 Update -- DONE
- **What:** Design philosophy section, Axis II/IV/VI expanded, Table 1 updated, 9 instead of 8 innovations, Abstract/Summary/English Translation updated
- **Result:** 30-page PDF

---

## Phase 2: Structural Extensions (Priority HIGH)

### 2.1 Axis V: P1-P4 Structured Coding
- **What:** Replace free-text fields with structured input with source-axis reference
- **Schema:** Each factor gets: Text + Source axis (I-IV) + Evidence level
- **Effort:** Medium

### 2.2 Missing Screening Instruments
- **What:** Add SCOFF (eating disorders), EDE-QS, ISI (insomnia), SSIS
- **Where:** Extend cross-cutting screening or as Level-2 modules
- **Effort:** Medium

### 2.3 Cultural Formulation Interview (CFI)
- **What:** Integrate structured CFI module in Axis IV
- **Fields:** Cultural identity, Cultural conceptualization, Psychosocial stressors, Cultural features of the clinician-patient relationship
- **Effort:** Medium

### 2.4 Clinical Significance / Severity Scale
- **What:** Standardized CGI-S-like severity rating per diagnosis (partly in 1b.1 already)
- **Extension:** CGI-I (Improvement) + CGI-E (Efficacy) as outcome parameters
- **Effort:** Small

### 2.5 Pathophysiological Causal Model
- **What:** 3-axis model (Genetic-Neurobiological / Psychological-Developmental / Environmental-Situational)
- **Where:** Extend Axis V or new tab
- **Source:** SYNOPSIS_VALIDATED (Pathophysiological relationships)
- **Effort:** Medium

### 2.6 Therapy Resistance Tracking
- **What:** Documentation of treatment attempts, response rates, therapy changes
- **Where:** Axis I (treatment history) or Axis III (IIIf)
- **Source:** Medication overview + SYNOPSIS_VALIDATED
- **Effort:** Medium

---

## Phase 3: Advanced Features (Priority MEDIUM)

### 3.1 Multi-Professional Role Model
- **What:** Login/role selection (Psychologist, Physician, Social Worker, Team) with axis-specific access rights
- **Mapping:** Psychologist -> Axis I+II, Physician -> Axis III, Social Worker -> Axis IV, Team -> Axis V, All -> Axis VI
- **Effort:** Large

### 3.2 Automated Coverage Analysis
- **What:** Symptom-diagnosis matrix that automatically identifies unexplained symptoms
- **Logic:** Cross-cutting items that were triggered but not assigned to any diagnosis
- **Effort:** Large

### 3.3 Comorbidity Rules
- **What:** Automatic warnings for clinically unusual combinations
- **Examples:** Bipolar + Unipolar Depression, PTSD without Trauma Criterion A
- **Effort:** Medium

### 3.4 HSM Disorder Modules (11 Modules)
- **What:** Structured criteria-based modules for: Mood, Anxiety, Trauma, Psychotic, Personality, OCDSpectrum, Dissociative, Eating, Neurodevelopmental, SubstanceUse, Somatic
- **Effort:** Very large (approx. 100-200 lines per module)

---

## Phase 4: Future (Priority LOW)

### 4.1 Child/Adolescent Cross-Cutting Variant
### 4.2 FHIR Interoperability
### 4.3 PDF Report Generation (WeasyPrint + Jinja2)
### 4.4 SQLite Persistence
### 4.5 RDoC Annotation Layer

---

## Implementation Order

### Sprint 1 -- COMPLETED (V9)
1. Ii/Ij Swap (translations.json + Code) -- DONE
2. HiTOP Radar from Cross-Cutting Data -- DONE
3. Axis III Symmetric Extension (13 sub-axes) -- DONE
4. Version bump to V9 -- DONE
5. PRO/CONTRA Evidence Evaluation + Confidence -- DONE
6. Structured Symptom Coverage with Metrics -- DONE
7. Prioritized Investigation Plan -- DONE
8. CAVE Alerts (input + synopsis) -- DONE
9. Symptom Timeline (input + synopsis) -- DONE
10. IIIm Medication Form Extended -- DONE
11. JSON Export with all new fields -- DONE

### Sprint 2 -- NEXT SPRINT
1. Axis V P1-P4 Structuring
2. Pathophysiological Causal Model
3. Therapy Resistance Tracking
4. CGI-I / CGI-E Outcome Parameters
