# Multiaxial Diagnostic Expert System (V9)

A computer-assisted 6-axis psychiatric diagnostic system integrating DSM-5-TR, ICD-11, and ICF in a unified expert system.

## Overview

This system addresses the structural gap left by the abolition of the multiaxial system in DSM-5 (2013). It provides a comprehensive, multi-professional diagnostic framework with innovations that go beyond any previous classification system.

### The 6-Axis Model

| Axis | Name | Sub-axes | Primary Profession |
|------|------|----------|-------------------|
| I | Mental Health Profiles | Ia-Ij (10 sub-axes) | Psychologist / Psychiatrist |
| II | Biography & Development | Personality (PID-5), Education, IQ | Psychologist |
| III | Medical Synopsis | IIIa-IIIm (13 sub-axes, symmetric to Axis I) | Physician |
| IV | Environment & Functioning | ICF, WHODAS 2.0, GAF, GdB, CFI | Social Worker |
| V | Integrated Condition Model | 3P/4P Case Formulation | Interdisciplinary Team |
| VI | Evidence Collection & Clinical Safety | Evidence Matrix, CAVE Alerts, Symptom Timeline | All Professions |

### Key Innovations

- **Quantitative Coverage Analysis** (Ii/IIIi): Percentage-based symptom-diagnosis matrix identifying unexplained symptoms
- **Symmetric Axis I/III Architecture**: Identical structural tools for psychologists and physicians
- **PRO/CONTRA Evidence Evaluation**: Structured evidence for/against each diagnosis with confidence estimation
- **CAVE Clinical Alerts**: Cross-axis risk management (drug interactions, lab artifacts, contraindications)
- **Prioritized Investigation Plan**: 3-tier system (Urgent / Important / Monitoring)
- **Longitudinal Symptom Timeline**: Tracking onset, status, and therapy response over time
- **HiTOP Spectra**: Automatically computed from Cross-Cutting screening results
- **6-Step Gatekeeper Logic**: Implementing First's (2024) gold-standard differential diagnosis sequence
- **11 Disorder Modules**: Complete screening-to-diagnosis coverage via hierarchical state machine

## Tech Stack

- **UI**: Streamlit
- **Decision Engine**: `transitions` (Hierarchical State Machine)
- **Visualization**: Plotly (PID-5 + HiTOP radar charts)
- **Data Validation**: Python dataclasses
- **Internationalization**: Bilingual (German/English) via `translations.json`

## Installation

```bash
pip install streamlit plotly pandas transitions anytree
```

## Usage

```bash
streamlit run multiaxial_diagnostic_system.py
```

## Project Structure

```
multiaxial_diagnostic_system.py   # Main application (V9, ~2080 lines)
translations.json                 # Bilingual i18n (DE/EN)
Review_Multiaxiale_Diagnostik.tex # Scientific paper (V5, LaTeX)
Konzept_Dimensionale_Integration.md  # Dimensional integration concept
Ausbauplan_Prototyp_V9.md        # Development roadmap
```

## Scientific Paper

The accompanying paper *"An Integrated Multiaxial Model for Computer-Assisted Psychiatric Diagnosis"* (V5) is included as LaTeX source. It covers the theoretical foundation, clinical rationale, and validation strategy.

### Citing This Work

> Geiger, L. (2026). Ein integriertes multiaxiales Modell zur computergestuetzten psychiatrischen Diagnostik: Synthese von DSM-5-TR, ICD-11 und ICF in einem 6-Achsen-Expertensystem. Working Paper, Version 5.

## Development Roadmap

See [Ausbauplan_Prototyp_V9.md](Ausbauplan_Prototyp_V9.md) for the full roadmap.

**Completed (Sprint 1 / V9):**
- Ii/Ij swap (coverage before investigation)
- HiTOP spectra from Cross-Cutting data
- Symmetric Axis III (13 sub-axes)
- PRO/CONTRA evidence evaluation with confidence
- Quantitative coverage analysis with metrics
- Prioritized investigation plan (3-tier)
- CAVE clinical alerts
- Longitudinal symptom timeline
- Extended medication form (IIIm)
- Full JSON export

**Next (Sprint 2):**
- Axis V P1-P4 structured coding
- Pathophysiological causal model
- Therapy resistance tracking
- CGI-I / CGI-E outcome parameters

## License

All rights reserved. Academic use with attribution permitted.

## Author

**Lukas Geiger** -- Independent Researcher, Bernau im Schwarzwald, Germany

*AI-assisted development: Claude Opus 4.6 (Anthropic), Gemini (Google DeepMind), Copilot (Microsoft)*
