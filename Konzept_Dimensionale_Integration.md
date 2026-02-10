# Konzeptpapier: Dimensionale Integration im 6-Achsen-Modell

**Autor:** Lukas Geiger
**Datum:** Februar 2026
**Status:** Arbeitsdokument
**Bezug:** Review_Multiaxiale_Diagnostik.tex (Version 3)

---

## 1. Motivation

Das 6-Achsen-Modell basiert primaer auf kategorialer Diagnostik (DSM-5-TR/ICD-11). Kategoriale Systeme haben bekannte Limitierungen:

- **Kuenstliche Grenzen:** Cutoff-Werte erzeugen binaere Ja/Nein-Entscheidungen bei kontinuierlichen Phaenomenen
- **Hohe Komorbiditaet:** Die Rate von 50%+ Komorbiditaeten reflektiert eher Artefakte der kategorialen Grenzziehung als genuine Koexistenz
- **Heterogenitaet innerhalb von Diagnosen:** Zwei Patienten mit derselben MDD-Diagnose koennen voellig unterschiedliche Symptomprofile haben
- **Informationsverlust:** Subklinische Symptome werden nicht erfasst

Dimensionale Alternativen adressieren diese Probleme. Dieses Konzeptpapier beschreibt, wie drei dimensionale Frameworks als ergaenzende Schichten in das 6-Achsen-Modell integriert werden koennen, ohne die kategoriale Grundstruktur zu ersetzen.

---

## 2. Schichtenarchitektur: Kategorial + Dimensional

Das Modell implementiert eine **4-Schichten-Architektur**:

```
Schicht 4: Netzwerk-Perspektive (Symptom-Konnektivitaet)
Schicht 3: Forschungsannotation (RDoC-Domaenen)
Schicht 2: Dimensionale Uebersicht (HiTOP-Spektren)
Schicht 1: Kategoriale Diagnostik (DSM-5-TR / ICD-11)  <-- Basis
```

**Prinzip:** Jede hoehere Schicht ergaenzt die darunterliegende, ersetzt sie aber nicht. Die kategoriale Diagnose bleibt die primaere klinische Waehrung; dimensionale Schichten liefern Zusatzinformationen fuer Behandlungsplanung und Forschung.

---

## 3. Schicht 2: HiTOP-Integration

### 3.1 Das HiTOP-Modell

Die **Hierarchical Taxonomy of Psychopathology** (Kotov et al., 2017; aktualisiert 2021) organisiert Psychopathologie empirisch-hierarchisch:

```
Ebene 1: Genereller Psychopathologie-Faktor (p-Faktor)
  |
Ebene 2: Supra-Spektren
  |-- Internalizing + Somatoform
  |-- Externalizing (Disinhibited + Antagonistic)
  |-- Thought Disorder
  |
Ebene 3: Sechs Spektren
  |-- Internalizing (Depression, Angst, Trauma)
  |-- Somatoform (somatische Symptome, Konversion)
  |-- Thought Disorder (Psychose, Manie)
  |-- Disinhibited Externalizing (Substanzgebrauch, Impulskontrolle)
  |-- Antagonistic Externalizing (Antisozialitaet, Aggressivitaet)
  |-- Detachment (soziale Zurueckgezogenheit, Anhedonie)
  |
Ebene 4: Subfaktoren
  |-- z.B. Internalizing -> Distress (MDD, GAD, PTBS)
  |                       -> Fear (Panik, Soziale Angst, Phobien)
  |
Ebene 5: Syndrome/Dimensionen
  |-- z.B. Depressivitaet, Anhedonie, Panik-Arousal
  |
Ebene 6: Symptom-Komponenten / Traits
```

### 3.2 Mapping: Cross-Cutting-Ergebnisse auf HiTOP-Spektren

Die 13 Cross-Cutting-Domaenen lassen sich direkt auf HiTOP-Spektren abbilden:

| Cross-Cutting-Domaene | HiTOP-Spektrum | Subfaktor |
|---|---|---|
| Depression | Internalizing | Distress |
| Angst | Internalizing | Fear |
| Somatische Symptome | Somatoform | -- |
| Schlafprobleme | Internalizing | Distress |
| Aerger | Antagonistic Externalizing | -- |
| Manie | Thought Disorder | Mania |
| Psychose | Thought Disorder | Psychoticism |
| Substanzgebrauch | Disinhibited Externalizing | Substance Use |
| Repetitive Gedanken/Verhalten | Internalizing | OCD-Subfaktor |
| Dissoziation | Internalizing / Thought Disorder | Kontexabhaengig |
| Persoenlichkeitsfunktion | Mehrere Spektren | PID-5-abhaengig |
| Gedaechtnis | Cognitive (kein eigenes HiTOP-Spektrum) | -- |
| Suizidalitaet | Internalizing | Distress (Querschnitt) |

### 3.3 PID-5-Trait-Domaenen auf HiTOP

Das bereits im System implementierte PID-5 mappt direkt auf HiTOP-Spektren:

| PID-5-Domaene | HiTOP-Spektrum | Konvergenz |
|---|---|---|
| Negative Affektivitaet | Internalizing | r = 0.78-0.86 |
| Distanziertheit | Detachment | r = 0.78-0.86 |
| Antagonismus | Antagonistic Externalizing | r = 0.78-0.86 |
| Enthemmung | Disinhibited Externalizing | r = 0.78-0.86 |
| Psychotizismus | Thought Disorder | r = 0.78-0.86 |
| Anankastie (ICD-11) | Kein direktes HiTOP-Aequivalent | r = 0.34 |

### 3.4 Implementierungsvorschlag

**HiTOP-Spektren-Profil als Zusammenfassungs-Widget:**

Nach Abschluss aller Screening-Instrumente berechnet das System ein 6-dimensionales HiTOP-Spektren-Profil:

```python
class HiTOPProfile:
    """Dimensionales HiTOP-Spektren-Profil aus Cross-Cutting-Ergebnissen."""

    internalizing: float       # 0.0 - 1.0 (normalisiert)
    somatoform: float
    thought_disorder: float
    disinhibited_ext: float
    antagonistic_ext: float
    detachment: float
    p_factor: float            # Genereller Faktor (Durchschnitt)

    def from_cross_cutting(self, cc_results: dict) -> 'HiTOPProfile':
        """Berechnet HiTOP-Profil aus Cross-Cutting Level-1-Ergebnissen."""
        self.internalizing = normalize(
            cc_results['depression'] + cc_results['anxiety'] +
            cc_results['sleep'] + cc_results['repetitive']
        )
        self.thought_disorder = normalize(
            cc_results['psychosis'] + cc_results['mania']
        )
        # ... etc.
```

**Visualisierung:** Plotly-Radardiagramm analog zum PID-5-Profil, aber mit 6 HiTOP-Spektren statt 5/6 PID-5-Domaenen.

**Klinischer Nutzen:**
- Transdiagnostische Muster erkennen (z.B. hohes Internalizing + hohes Detachment = spezifisches Behandlungsprofil)
- Komorbiditaetsmuster als dimensionale Cluster statt separate Diagnosen verstehen
- Behandlungsauswahl auf Spektren-Ebene informieren (z.B. SSRIs fuer hohes Internalizing)

---

## 4. Schicht 3: RDoC-Forschungsannotation

### 4.1 Das RDoC-Framework

Die **Research Domain Criteria** (Insel et al., 2010; NIMH) definieren:

**Sechs Domaenen:**
1. **Negative Valence Systems** -- Furcht, Angst, Verlust
2. **Positive Valence Systems** -- Belohnung, Motivation, Gewohnheiten
3. **Cognitive Systems** -- Aufmerksamkeit, Wahrnehmung, Gedaechtnis
4. **Social Processes** -- Affiliation, Kommunikation, Selbst-/Fremdwahrnehmung
5. **Arousal/Regulatory Systems** -- Erregung, Schlaf-Wach-Regulation
6. **Sensorimotor Systems** -- Motorische Planung, Gewohnheitsbildung

**Sieben Analyseebenen (Units of Analysis):**

| Ebene | Beispiel | Verfuegbarkeit |
|---|---|---|
| Gene | Serotonin-Transporter-Polymorphismus | Gentests |
| Molekuele | Cortisol, BDNF | Labortests |
| Zellen | Neuroinflammation-Marker | Forschung |
| Schaltkreise | Default Mode Network | fMRI |
| Physiologie | HRV, EEG-Alpha | Wearables |
| Verhalten | Reaktionszeiten, Vermeidung | Beobachtung |
| Selbstbericht | Fragebogen-Scores | Screening |

### 4.2 RDoC im 6-Achsen-Modell

RDoC ist **primaer eine Forschungsannotation**, kein klinisches Diagnosewerkzeug. Die Integration erfolgt als optionale Zusatzebene:

**Mapping Achse I auf RDoC-Domaenen:**

| Achse-I-Diagnosegruppe | Primaere RDoC-Domaene(n) |
|---|---|
| Depression | Negative Valence + Positive Valence (Anhedonie) |
| Angststoerungen | Negative Valence (Acute Threat, Potential Threat) |
| PTBS | Negative Valence (Acute Threat) + Arousal/Regulatory |
| Psychosen | Cognitive Systems + Social Processes |
| Substanzgebrauch | Positive Valence (Reward Learning) + Arousal |
| ADHS | Cognitive Systems (Attention) + Arousal/Regulatory |
| Autismus | Social Processes + Sensorimotor |
| Essstoerungen | Positive Valence + Arousal/Regulatory |

**Integration von Biomarker-Daten:**

Wenn Biomarker verfuegbar sind (z.B. aus Achse III), koennen diese den RDoC-Analyseebenen zugeordnet werden:

```
Achse III, IIIa (Hypothyreose)
  -> RDoC: Arousal/Regulatory Systems
  -> Analyseebene: Molekuele (TSH, T3, T4)
  -> Klinische Relevanz: Erklaert Fatigue + kognitive Verlangsamung

Achse III, IIIm (Familienanamnese Bipolar)
  -> RDoC: Positive Valence Systems + Arousal
  -> Analyseebene: Gene (Familienbelastung als Proxy)
  -> Klinische Relevanz: Erhoehtes Risiko fuer Manie
```

### 4.3 Implementierungsvorschlag

RDoC wird als **optionales Annotations-Panel** implementiert:

- Erst sichtbar nach Abschluss der kategorialen Diagnostik
- Automatisches Pre-Mapping basierend auf Achse-I-Diagnosen
- Manuelle Ergaenzung durch Kliniker bei verfuegbaren Biomarkern
- Export als strukturiertes JSON fuer Forschungsdatenbanken

---

## 5. Schicht 4: Netzwerk-Perspektive (Symptom-Konnektivitaet)

### 5.1 Der Netzwerk-Ansatz

Die **Network Theory of Psychopathology** (Borsboom, 2017) modelliert psychische Stoerungen nicht als latente Variablen (die Symptome verursachen), sondern als **Netzwerke kausal verbundener Symptome**:

- Symptome sind **Knoten**
- Kausale/funktionale Verbindungen sind **Kanten**
- Psychische Stoerungen entstehen durch Aktivierungskaskaden im Netzwerk
- **Bruecken-Symptome** verbinden verschiedene Stoerungsnetzwerke (erklaert Komorbiditaet)

### 5.2 Relevanz fuer die Abdeckungsanalyse

Die Netzwerk-Perspektive ist direkt relevant fuer die Abdeckungsanalyse (Achse Ii/IIIi):

**Unabgedeckte Symptome als Netzwerk-Bruecken:**

Ein Symptom, das durch keine aktuelle Diagnose abgedeckt wird, koennte ein **Bruecken-Symptom** sein, das zwei Stoerungsnetzwerke verbindet. Beispiel:

```
Diagnose: MDD (Achse Ia)
Unabgedecktes Symptom: Reizbarkeit (Achse Ii)

Netzwerk-Interpretation:
  MDD-Netzwerk <-- Reizbarkeit --> PTBS-Netzwerk
                                   (noch nicht diagnostiziert)

  -> Untersuchungsplan (Ij): PTBS-Screening (PCL-5) durchfuehren
```

**Zentrale Symptome identifizieren:**

Symptome mit hoher **Zentralitaet** (viele Verbindungen) sind klinisch priorisiert:
- **Schlaflosigkeit** hat typischerweise hohe Zentralitaet (verbindet Depression, Angst, Manie, PTBS)
- **Konzentrationsstoerung** verbindet Depression, ADHS, Angst, Psychose
- Die Behandlung zentraler Symptome kann kaskadenartige Verbesserungen ausloesen

### 5.3 Implementierungsvorschlag

```python
class SymptomNetwork:
    """Symptom-Netzwerk basierend auf Cross-Cutting + Level-2-Ergebnissen."""

    nodes: list[Symptom]        # Alle bestaetigten Symptome
    edges: list[SymptomEdge]    # Bekannte Verbindungen (aus Literatur)
    diagnoses: list[Diagnosis]  # Achse-Ia-Diagnosen

    def find_bridge_symptoms(self) -> list[Symptom]:
        """Identifiziert Bruecken-Symptome zwischen Diagnose-Clustern."""
        uncovered = self.get_uncovered_symptoms()  # Achse Ii
        bridges = []
        for symptom in uncovered:
            connected_clusters = self.get_connected_diagnosis_clusters(symptom)
            if len(connected_clusters) >= 2:
                bridges.append(symptom)
        return bridges

    def calculate_centrality(self) -> dict[Symptom, float]:
        """Berechnet Betweenness-Zentralitaet fuer Behandlungspriorisierung."""
        # Verwendet networkx betweenness_centrality
        pass
```

**Visualisierung:** Force-directed Graph (z.B. Plotly oder D3.js) mit:
- Farbkodierung nach diagnostischer Zugehoerigkeit
- Groesse proportional zur Zentralitaet
- Unabgedeckte Symptome hervorgehoben (rot)
- Bruecken-Symptome speziell markiert

---

## 6. Konkretes Beispiel: Fallvignette mit 4-Schichten-Analyse

**Patient:** 35-jaehrig, maennlich, praesentiert mit depressiver Stimmung, Schlaflosigkeit, Reizbarkeit, Konzentrationsstoerungen, sozialem Rueckzug.

### Schicht 1: Kategoriale Diagnostik (Achse I)
- **Ia:** Major Depressive Disorder, einzelne Episode, mittelschwer (F32.1)
- **Ii (Abdeckungsanalyse):** Reizbarkeit + Konzentrationsstoerung nur teilweise durch MDD erklaert
- **Ij:** ADHS-Screening (ASRS) empfohlen

### Schicht 2: HiTOP-Profil
```
Internalizing:            0.75  ████████░░  (hoch)
Somatoform:               0.10  █░░░░░░░░░  (niedrig)
Thought Disorder:          0.05  █░░░░░░░░░  (minimal)
Disinhibited Externalizing: 0.30  ███░░░░░░░  (leicht erhoet)
Antagonistic Externalizing: 0.10  █░░░░░░░░░  (niedrig)
Detachment:                0.60  ██████░░░░  (mittel-hoch)
```
**Interpretation:** Hohes Internalizing + mittleres Detachment. Das Profil suggeriert, dass sozialer Rueckzug nicht nur MDD-Symptom ist, sondern ein eigenstaendiges dimensionales Merkmal. Der leicht erhoehte Disinhibited-Wert (durch Konzentrationsstoerung) stuetzt die ADHS-Hypothese.

### Schicht 3: RDoC-Annotation
- Negative Valence: Hoch (Traurigkeit, Hoffnungslosigkeit)
- Positive Valence: Erniedrigt (Anhedonie, reduzierte Motivation)
- Cognitive Systems: Beeintraechtigt (Konzentration) -- RDoC wuerde hier kognitive Tests empfehlen
- Arousal/Regulatory: Gestoert (Schlaflosigkeit)

### Schicht 4: Netzwerk-Analyse
```
[Traurigkeit] --- [Schlaflosigkeit] --- [Konzentration]
      |                   |                    |
      |              [Reizbarkeit]             |
      |                   |                    |
[Hoffnungslosigkeit]     ???            [ADHS-Netzwerk?]
      |
[Sozialer Rueckzug]
```
**Bruecken-Symptom:** Konzentrationsstoerung verbindet MDD- und potenzielles ADHS-Netzwerk.
**Zentralstes Symptom:** Schlaflosigkeit (verbindet 4 andere Symptome).
**Behandlungsimplikation:** Priorisierung von Schlaf-Intervention koennte kaskadenartige Verbesserung ausloesen.

---

## 7. Integration in die Systemarchitektur

### 7.1 Wann werden dimensionale Schichten aktiviert?

| Schicht | Aktivierung | Automatisierungsgrad |
|---|---|---|
| 1: Kategorial | Immer (Pflicht) | Semi-automatisch (Gatekeeper) |
| 2: HiTOP | Automatisch nach Cross-Cutting | Vollautomatisch |
| 3: RDoC | Optional bei Biomarker-Verfuegbarkeit | Manuell + Pre-Mapping |
| 4: Netzwerk | Automatisch bei Abdeckungsanalyse | Teilautomatisch |

### 7.2 Datenmodell (Pydantic)

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
    """Ergaenzendes dimensionales Profil zu kategorialer Diagnostik."""

    # HiTOP (Schicht 2)
    hitop_scores: dict[HiTOPSpectrum, float]  # 0.0-1.0
    hitop_p_factor: float                      # Genereller Faktor

    # RDoC (Schicht 3) - optional
    rdoc_annotations: dict[RDoCDomain, str] | None = None
    biomarker_data: list[dict] | None = None

    # Netzwerk (Schicht 4)
    bridge_symptoms: list[str] = []
    central_symptoms: list[tuple[str, float]] = []  # (Symptom, Zentralitaet)

class PatientDiagnostics(BaseModel):
    """Vollstaendiges Patientenmodell mit allen 4 Schichten."""

    # Schicht 1: Kategorial (Achsen I-VI)
    axis_i: AxisIPsychProfile
    axis_ii: AxisIIBiography
    axis_iii: AxisIIIMedical
    axis_iv: AxisIVEnvironment
    axis_v: AxisVConditionModel
    axis_vi: AxisVIEvidence

    # Schichten 2-4: Dimensional
    dimensional: DimensionalProfile | None = None
```

---

## 8. Abgrenzung und Limitierungen

### Was dimensionale Integration NICHT ist:

- **Kein Ersatz** fuer kategoriale Diagnostik -- Versicherungen, Krankenhaeuser und Forschung benoetigen kategoriale Codes
- **Keine eigene diagnostische Entscheidung** -- HiTOP-Scores fuehren nicht zu Diagnosen
- **Kein zusaetzlicher Dokumentationsaufwand** -- Die HiTOP-Berechnung erfolgt automatisch aus bereits erhobenen Cross-Cutting-Daten

### Offene Fragen:

1. **Normierung:** Wie werden HiTOP-Spektren-Scores normiert? Bevoelkerungsnormen existieren noch nicht flaechendeckend.
2. **Klinische Validitaet:** Verbessert das HiTOP-Profil tatsaechlich die Behandlungsauswahl? Empirisch noch nicht abschliessend geklaert.
3. **Netzwerk-Stabilitaet:** Symptom-Netzwerke sind statistisch instabil bei kleinen Stichproben. Fuer Einzelfaelle muss auf Literatur-basierte Netzwerkstrukturen zurueckgegriffen werden.
4. **RDoC-Praktikabilitaet:** Die meisten RDoC-Analyseebenen (Gene, Schaltkreise) sind klinisch nicht routinemaessig verfuegbar.

---

## 9. Empfehlungen fuer die Implementierung

### Phase 1 (Sofort):
- HiTOP-Spektren-Mapping aus Cross-Cutting-Ergebnissen implementieren
- Radardiagramm-Visualisierung (Plotly)
- Kein zusaetzlicher Erhebungsaufwand

### Phase 2 (Mittelfristig):
- Netzwerk-Visualisierung fuer Abdeckungsanalyse
- Bruecken-Symptom-Identifikation
- Literatur-basierte Symptom-Netzwerk-Datenbank

### Phase 3 (Langfristig):
- RDoC-Annotations-Panel
- Biomarker-Integration bei Verfuegbarkeit
- Longitudinale HiTOP-Profil-Verlaeufe

---

## 10. Referenzen

- Borsboom, D. (2017). A network theory of mental disorders. *World Psychiatry*, 16(1), 5-13.
- Insel, T., et al. (2010). Research Domain Criteria (RDoC). *American Journal of Psychiatry*, 167(7), 748-751.
- Kotov, R., et al. (2017). The Hierarchical Taxonomy of Psychopathology (HiTOP). *Journal of Abnormal Psychology*, 126(4), 454-477.
- Kotov, R., et al. (2021). The Hierarchical Taxonomy of Psychopathology (HiTOP): A quantitative nosology based on consensus of evidence. *Annual Review of Clinical Psychology*, 17, 83-108.
- Krueger, R.F., et al. (2018). Progress in achieving quantitative classification of psychopathology. *World Psychiatry*, 17(3), 282-293.
- Ruggero, C.J., et al. (2019). Integrating the HiTOP system into clinical practice. *Journal of Consulting and Clinical Psychology*, 87(12), 1069-1084.
