# Concept Paper: Dimensional Integration in the 6-Axis Model

**Author:** Lukas Geiger
**Date:** February 2026
**Status:** Working document
**Reference:** Review_Multiaxiale_Diagnostik.tex (Version 3)

---

## 1. Motivation

The 6-axis model is primarily based on categorical diagnostics (DSM-5-TR/ICD-11). Categorical systems have well-known limitations:

- **Artificial boundaries:** Cut-off values create binary yes/no decisions for continuous phenomena
- **High comorbidity:** Comorbidity rates of 50%+ more likely reflect artifacts of categorical boundary-setting than genuine co-existence
- **Within-diagnosis heterogeneity:** Two patients with the same MDD diagnosis can have entirely different symptom profiles
- **Information loss:** Subclinical symptoms are not captured

Dimensional alternatives address these problems. This concept paper describes how three dimensional frameworks can be integrated as complementary layers into the 6-axis model without replacing the categorical base structure.

---

## 2. Layer Architecture: Categorical + Dimensional

The model implements a **4-layer architecture**:

```
Layer 4: Network Perspective (Symptom Connectivity)
Layer 3: Research Annotation (RDoC Domains)
Layer 2: Dimensional Overview (HiTOP Spectra)
Layer 1: Categorical Diagnostics (DSM-5-TR / ICD-11)  <-- Base
```

**Principle:** Each higher layer supplements the one below it but does not replace it. The categorical diagnosis remains the primary clinical currency; dimensional layers provide additional information for treatment planning and research.

---

## 3. Layer 2: HiTOP Integration

### 3.1 The HiTOP Model

The **Hierarchical Taxonomy of Psychopathology** (Kotov et al., 2017; updated 2021) organizes psychopathology in an empirical-hierarchical manner:

```
Level 1: General Psychopathology Factor (p-factor)
  |
Level 2: Supra-Spectra
  |-- Internalizing + Somatoform
  |-- Externalizing (Disinhibited + Antagonistic)
  |-- Thought Disorder
  |
Level 3: Six Spectra
  |-- Internalizing (Depression, Anxiety, Trauma)
  |-- Somatoform (Somatic Symptoms, Conversion)
  |-- Thought Disorder (Psychosis, Mania)
  |-- Disinhibited Externalizing (Substance Use, Impulse Control)
  |-- Antagonistic Externalizing (Antisociality, Aggressiveness)
  |-- Detachment (Social Withdrawal, Anhedonia)
  |
Level 4: Subfactors
  |-- e.g., Internalizing -> Distress (MDD, GAD, PTSD)
  |                       -> Fear (Panic, Social Anxiety, Phobias)
  |
Level 5: Syndromes/Dimensions
  |-- e.g., Depressivity, Anhedonia, Panic-Arousal
  |
Level 6: Symptom Components / Traits
```

### 3.2 Mapping: Cross-Cutting Results to HiTOP Spectra

The 13 cross-cutting domains can be directly mapped to HiTOP spectra:

| Cross-Cutting Domain | HiTOP Spectrum | Subfactor |
|---|---|---|
| Depression | Internalizing | Distress |
| Anxiety | Internalizing | Fear |
| Somatic Symptoms | Somatoform | -- |
| Sleep Problems | Internalizing | Distress |
| Anger | Antagonistic Externalizing | -- |
| Mania | Thought Disorder | Mania |
| Psychosis | Thought Disorder | Psychoticism |
| Substance Use | Disinhibited Externalizing | Substance Use |
| Repetitive Thoughts/Behavior | Internalizing | OCD Subfactor |
| Dissociation | Internalizing / Thought Disorder | Context-dependent |
| Personality Functioning | Multiple Spectra | PID-5-dependent |
| Memory | Cognitive (no dedicated HiTOP spectrum) | -- |
| Suicidality | Internalizing | Distress (Cross-sectional) |

### 3.3 PID-5 Trait Domains to HiTOP

The PID-5, already implemented in the system, maps directly to HiTOP spectra:

| PID-5 Domain | HiTOP Spectrum | Convergence |
|---|---|---|
| Negative Affectivity | Internalizing | r = 0.78-0.86 |
| Detachment | Detachment | r = 0.78-0.86 |
| Antagonism | Antagonistic Externalizing | r = 0.78-0.86 |
| Disinhibition | Disinhibited Externalizing | r = 0.78-0.86 |
| Psychoticism | Thought Disorder | r = 0.78-0.86 |
| Anankastia (ICD-11) | No direct HiTOP equivalent | r = 0.34 |

### 3.4 Implementation Proposal

**HiTOP Spectra Profile as Summary Widget:**

After completing all screening instruments, the system computes a 6-dimensional HiTOP spectra profile:

```python
class HiTOPProfile:
    """Dimensional HiTOP spectra profile from cross-cutting results."""

    internalizing: float       # 0.0 - 1.0 (normalized)
    somatoform: float
    thought_disorder: float
    disinhibited_ext: float
    antagonistic_ext: float
    detachment: float
    p_factor: float            # General factor (average)

    def from_cross_cutting(self, cc_results: dict) -> 'HiTOPProfile':
        """Computes HiTOP profile from Cross-Cutting Level-1 results."""
        self.internalizing = normalize(
            cc_results['depression'] + cc_results['anxiety'] +
            cc_results['sleep'] + cc_results['repetitive']
        )
        self.thought_disorder = normalize(
            cc_results['psychosis'] + cc_results['mania']
        )
        # ... etc.
```

**Visualization:** Plotly radar chart analogous to the PID-5 profile, but with 6 HiTOP spectra instead of 5/6 PID-5 domains.

**Clinical Utility:**
- Identify transdiagnostic patterns (e.g., high Internalizing + high Detachment = specific treatment profile)
- Understand comorbidity patterns as dimensional clusters rather than separate diagnoses
- Inform treatment selection at the spectrum level (e.g., SSRIs for high Internalizing)

---

## 4. Layer 3: RDoC Research Annotation

### 4.1 The RDoC Framework

The **Research Domain Criteria** (Insel et al., 2010; NIMH) define:

**Six Domains:**
1. **Negative Valence Systems** -- Fear, Anxiety, Loss
2. **Positive Valence Systems** -- Reward, Motivation, Habits
3. **Cognitive Systems** -- Attention, Perception, Memory
4. **Social Processes** -- Affiliation, Communication, Self-/Other-Perception
5. **Arousal/Regulatory Systems** -- Arousal, Sleep-Wake Regulation
6. **Sensorimotor Systems** -- Motor Planning, Habit Formation

**Seven Units of Analysis:**

| Level | Example | Availability |
|---|---|---|
| Genes | Serotonin transporter polymorphism | Genetic testing |
| Molecules | Cortisol, BDNF | Lab tests |
| Cells | Neuroinflammation markers | Research |
| Circuits | Default Mode Network | fMRI |
| Physiology | HRV, EEG-Alpha | Wearables |
| Behavior | Reaction times, Avoidance | Observation |
| Self-Report | Questionnaire scores | Screening |

### 4.2 RDoC in the 6-Axis Model

RDoC is **primarily a research annotation**, not a clinical diagnostic tool. Integration takes the form of an optional additional layer:

**Mapping Axis I to RDoC Domains:**

| Axis I Diagnosis Group | Primary RDoC Domain(s) |
|---|---|
| Depression | Negative Valence + Positive Valence (Anhedonia) |
| Anxiety Disorders | Negative Valence (Acute Threat, Potential Threat) |
| PTSD | Negative Valence (Acute Threat) + Arousal/Regulatory |
| Psychoses | Cognitive Systems + Social Processes |
| Substance Use | Positive Valence (Reward Learning) + Arousal |
| ADHD | Cognitive Systems (Attention) + Arousal/Regulatory |
| Autism | Social Processes + Sensorimotor |
| Eating Disorders | Positive Valence + Arousal/Regulatory |

**Integration of Biomarker Data:**

When biomarkers are available (e.g., from Axis III), they can be assigned to RDoC units of analysis:

```
Axis III, IIIa (Hypothyroidism)
  -> RDoC: Arousal/Regulatory Systems
  -> Unit of Analysis: Molecules (TSH, T3, T4)
  -> Clinical Relevance: Explains fatigue + cognitive slowing

Axis III, IIIm (Family history of Bipolar)
  -> RDoC: Positive Valence Systems + Arousal
  -> Unit of Analysis: Genes (Family history as proxy)
  -> Clinical Relevance: Elevated risk for mania
```

### 4.3 Implementation Proposal

RDoC is implemented as an **optional annotation panel**:

- Only visible after completion of categorical diagnostics
- Automatic pre-mapping based on Axis I diagnoses
- Manual supplementation by clinicians when biomarkers are available
- Export as structured JSON for research databases

---

## 5. Layer 4: Network Perspective (Symptom Connectivity)

### 5.1 The Network Approach

The **Network Theory of Psychopathology** (Borsboom, 2017) models mental disorders not as latent variables (causing symptoms) but as **networks of causally connected symptoms**:

- Symptoms are **nodes**
- Causal/functional connections are **edges**
- Mental disorders emerge through activation cascades in the network
- **Bridge symptoms** connect different disorder networks (explaining comorbidity)

### 5.2 Relevance for Coverage Analysis

The network perspective is directly relevant to coverage analysis (Axis Ii/IIIi):

**Uncovered Symptoms as Network Bridges:**

A symptom not covered by any current diagnosis could be a **bridge symptom** connecting two disorder networks. Example:

```
Diagnosis: MDD (Axis Ia)
Uncovered Symptom: Irritability (Axis Ii)

Network Interpretation:
  MDD Network <-- Irritability --> PTSD Network
                                   (not yet diagnosed)

  -> Investigation Plan (Ij): Conduct PTSD screening (PCL-5)
```

**Identifying Central Symptoms:**

Symptoms with high **centrality** (many connections) are clinically prioritized:
- **Insomnia** typically has high centrality (connects Depression, Anxiety, Mania, PTSD)
- **Concentration difficulties** connects Depression, ADHD, Anxiety, Psychosis
- Treating central symptoms can trigger cascade-like improvements

### 5.3 Implementation Proposal

```python
class SymptomNetwork:
    """Symptom network based on Cross-Cutting + Level-2 results."""

    nodes: list[Symptom]        # All confirmed symptoms
    edges: list[SymptomEdge]    # Known connections (from literature)
    diagnoses: list[Diagnosis]  # Axis Ia diagnoses

    def find_bridge_symptoms(self) -> list[Symptom]:
        """Identifies bridge symptoms between diagnosis clusters."""
        uncovered = self.get_uncovered_symptoms()  # Axis Ii
        bridges = []
        for symptom in uncovered:
            connected_clusters = self.get_connected_diagnosis_clusters(symptom)
            if len(connected_clusters) >= 2:
                bridges.append(symptom)
        return bridges

    def calculate_centrality(self) -> dict[Symptom, float]:
        """Computes betweenness centrality for treatment prioritization."""
        # Uses networkx betweenness_centrality
        pass
```

**Visualization:** Force-directed graph (e.g., Plotly or D3.js) with:
- Color coding by diagnostic affiliation
- Size proportional to centrality
- Uncovered symptoms highlighted (red)
- Bridge symptoms specially marked

---

## 6. Concrete Example: Case Vignette with 4-Layer Analysis

**Patient:** 35 years old, male, presents with depressed mood, insomnia, irritability, concentration difficulties, social withdrawal.

### Layer 1: Categorical Diagnostics (Axis I)
- **Ia:** Major Depressive Disorder, single episode, moderate (F32.1)
- **Ii (Coverage Analysis):** Irritability + concentration difficulties only partially explained by MDD
- **Ij:** ADHD screening (ASRS) recommended

### Layer 2: HiTOP Profile
```
Internalizing:              0.75  ████████░░  (high)
Somatoform:                 0.10  █░░░░░░░░░  (low)
Thought Disorder:           0.05  █░░░░░░░░░  (minimal)
Disinhibited Externalizing: 0.30  ███░░░░░░░  (slightly elevated)
Antagonistic Externalizing: 0.10  █░░░░░░░░░  (low)
Detachment:                 0.60  ██████░░░░  (moderate-high)
```
**Interpretation:** High Internalizing + moderate Detachment. The profile suggests that social withdrawal is not merely an MDD symptom but an independent dimensional trait. The slightly elevated Disinhibited value (due to concentration difficulties) supports the ADHD hypothesis.

### Layer 3: RDoC Annotation
- Negative Valence: High (Sadness, Hopelessness)
- Positive Valence: Reduced (Anhedonia, reduced motivation)
- Cognitive Systems: Impaired (Concentration) -- RDoC would recommend cognitive tests here
- Arousal/Regulatory: Disturbed (Insomnia)

### Layer 4: Network Analysis
```
[Sadness] --- [Insomnia] --- [Concentration]
      |              |                |
      |         [Irritability]        |
      |              |                |
[Hopelessness]      ???         [ADHD Network?]
      |
[Social Withdrawal]
```
**Bridge Symptom:** Concentration difficulties connects MDD and potential ADHD network.
**Most Central Symptom:** Insomnia (connects 4 other symptoms).
**Treatment Implication:** Prioritizing sleep intervention could trigger cascade-like improvement.

---

## 7. Integration into System Architecture

### 7.1 When Are Dimensional Layers Activated?

| Layer | Activation | Automation Level |
|---|---|---|
| 1: Categorical | Always (mandatory) | Semi-automatic (Gatekeeper) |
| 2: HiTOP | Automatically after Cross-Cutting | Fully automatic |
| 3: RDoC | Optional when biomarkers available | Manual + Pre-mapping |
| 4: Network | Automatically during coverage analysis | Partially automatic |

### 7.2 Data Model (Pydantic)

```python
from pydantic import BaseModel
from enum import Enum

class HiTOPSpectrum(str, Enum):
    INTERNALIZING = "internalizing"
    SOMATOFORM = "somatoform"
    THOUGHT_DISORDER = "thought_disorder"
    DISINHIBITED_EXT = "disinhibited_externalizing"
    ANTAGONISTIC_EXT = "antagonistic_externalizing"
    DETACHMENT = "detachment"

class RDoCDomain(str, Enum):
    NEGATIVE_VALENCE = "negative_valence"
    POSITIVE_VALENCE = "positive_valence"
    COGNITIVE = "cognitive_systems"
    SOCIAL = "social_processes"
    AROUSAL = "arousal_regulatory"
    SENSORIMOTOR = "sensorimotor"

class DimensionalProfile(BaseModel):
    """Complementary dimensional profile to categorical diagnostics."""

    # HiTOP (Layer 2)
    hitop_scores: dict[HiTOPSpectrum, float]  # 0.0-1.0
    hitop_p_factor: float                      # General factor

    # RDoC (Layer 3) - optional
    rdoc_annotations: dict[RDoCDomain, str] | None = None
    biomarker_data: list[dict] | None = None

    # Network (Layer 4)
    bridge_symptoms: list[str] = []
    central_symptoms: list[tuple[str, float]] = []  # (Symptom, Centrality)

class PatientDiagnostics(BaseModel):
    """Complete patient model with all 4 layers."""

    # Layer 1: Categorical (Axes I-VI)
    axis_i: AxisIPsychProfile
    axis_ii: AxisIIBiography
    axis_iii: AxisIIIMedical
    axis_iv: AxisIVEnvironment
    axis_v: AxisVConditionModel
    axis_vi: AxisVIEvidence

    # Layers 2-4: Dimensional
    dimensional: DimensionalProfile | None = None
```

---

## 8. Limitations and Boundaries

### What Dimensional Integration is NOT:

- **Not a replacement** for categorical diagnostics -- Insurance companies, hospitals, and research require categorical codes
- **Not an independent diagnostic decision** -- HiTOP scores do not lead to diagnoses
- **No additional documentation burden** -- HiTOP computation is fully automatic from already collected cross-cutting data

### Open Questions:

1. **Norming:** How are HiTOP spectra scores normed? Population norms do not yet exist comprehensively.
2. **Clinical Validity:** Does the HiTOP profile actually improve treatment selection? Not yet conclusively established empirically.
3. **Network Stability:** Symptom networks are statistically unstable with small samples. For individual cases, literature-based network structures must be used.
4. **RDoC Practicability:** Most RDoC units of analysis (genes, circuits) are not routinely available in clinical practice.

---

## 9. Implementation Recommendations

### Phase 1 (Immediate):
- Implement HiTOP spectra mapping from cross-cutting results
- Radar chart visualization (Plotly)
- No additional data collection burden

### Phase 2 (Medium-term):
- Network visualization for coverage analysis
- Bridge symptom identification
- Literature-based symptom network database

### Phase 3 (Long-term):
- RDoC annotation panel
- Biomarker integration when available
- Longitudinal HiTOP profile trajectories

---

## 10. References

- Borsboom, D. (2017). A network theory of mental disorders. *World Psychiatry*, 16(1), 5-13.
- Insel, T., et al. (2010). Research Domain Criteria (RDoC). *American Journal of Psychiatry*, 167(7), 748-751.
- Kotov, R., et al. (2017). The Hierarchical Taxonomy of Psychopathology (HiTOP). *Journal of Abnormal Psychology*, 126(4), 454-477.
- Kotov, R., et al. (2021). The Hierarchical Taxonomy of Psychopathology (HiTOP): A quantitative nosology based on consensus of evidence. *Annual Review of Clinical Psychology*, 17, 83-108.
- Krueger, R.F., et al. (2018). Progress in achieving quantitative classification of psychopathology. *World Psychiatry*, 17(3), 282-293.
- Ruggero, C.J., et al. (2019). Integrating the HiTOP system into clinical practice. *Journal of Consulting and Clinical Psychology*, 87(12), 1069-1084.
