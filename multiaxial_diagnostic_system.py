"""
==========================================================================================
KLINISCHES MULTIAXIALES EXPERTENSYSTEM (DSM-5-TR / ICD-11 / MULTIAXIAL V9)
==========================================================================================

Computergestütztes 6-Achsen-Diagnostiksystem basierend auf:
- DSM-5-TR Cross-Cutting Symptom Measures (Level 1 & 2)
- Michael B. Firsts 6-Stufen-Gatekeeper-Logik
- ICD-11 / DSM-5-TR Dual-System-Architektur
- ICF / WHODAS 2.0 / GdB Funktionsbeurteilung
- PID-5-BF+M dimensionale Persönlichkeitsdiagnostik
- HiTOP-Spektren (Kotov et al., 2017) aus Cross-Cutting-Daten
- Hierarchische Zustandsmaschine (HSM) als Entscheidungsmotor

V9: Symmetrische Achse III (13 Subachsen), HiTOP-Integration, Ii/Ij-Swap
    Bilingual (Deutsch / English) via translations.json

Technologie: transitions (HSM), Streamlit (UI), anytree (Visualisierung),
             Plotly (PID-5 + HiTOP Radar), Pydantic (Datenvalidierung)

Aufbauend auf V8 / Vorläuferscript icf11dsm5.py (V6 Expert System)
==========================================================================================
"""

import streamlit as st
import datetime
import json
import math
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

try:
    from transitions.extensions import HierarchicalMachine
    HAS_TRANSITIONS = True
except ImportError:
    HAS_TRANSITIONS = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from anytree import Node, RenderTree
    HAS_ANYTREE = True
except ImportError:
    HAS_ANYTREE = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ===================================================================
# TRANSLATION SYSTEM (i18n)
# ===================================================================

_TRANSLATIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations.json")
with open(_TRANSLATIONS_PATH, "r", encoding="utf-8") as _f:
    TRANSLATIONS = json.load(_f)


def t(key: str) -> str:
    """Return translated string for current language."""
    lang = st.session_state.get("lang", "de")
    return TRANSLATIONS.get(lang, TRANSLATIONS["de"]).get(key, key)


# ===================================================================
# DATENMODELLE (Pydantic-artig mit dataclasses)
# ===================================================================

class DiagnosticStatus(Enum):
    ACUTE = "akut"
    CHRONIC = "chronisch"
    REMITTED = "remittiert"
    SUSPECTED = "Verdacht"
    EXCLUDED = "ausgeschlossen"
    REFUTED = "widerlegt"


@dataclass
class Diagnosis:
    code_icd11: str = ""
    code_dsm5: str = ""
    name: str = ""
    status: str = "akut"
    evidence: str = ""
    date_onset: str = ""
    date_remission: str = ""
    remission_factors: list = field(default_factory=list)
    treatment_history: list = field(default_factory=list)
    # NEU: PRO/CONTRA-Evidenzbewertung & Konfidenz (aus FALLBEZOGENE_AUSWERTUNG)
    confidence_pct: int = 0
    severity: str = ""
    evidence_pro: str = ""
    evidence_contra: str = ""


@dataclass
class TreatmentEntry:
    type: str = ""  # Medikation, Psychotherapie, etc.
    name: str = ""
    start_date: str = ""
    end_date: str = ""
    effect: str = ""
    side_effects: str = ""
    compliance_self: int = 5
    compliance_external: int = 5


@dataclass
class PID5Profile:
    negative_affectivity: float = 0.0
    detachment: float = 0.0
    antagonism: float = 0.0
    disinhibition: float = 0.0
    psychoticism: float = 0.0
    anankastia: float = 0.0  # ICD-11 Erweiterung (PID-5-BF+M)


@dataclass
class MedicalCondition:
    name: str = ""
    icd11_code: str = ""
    dsm5_code: str = ""
    causality: str = "beitragend"
    evidence: str = ""
    status: str = "aktiv"
    date_onset: str = ""
    date_remission: str = ""
    remission_factors: list = field(default_factory=list)


@dataclass
class MedicationEntry:
    name: str = ""
    dose: str = ""
    unit: str = ""
    purpose: str = ""
    since: str = ""
    effect: str = ""
    effect_rating: int = 5
    side_effects: str = ""
    interactions: str = ""
    schedule: str = ""


@dataclass
class CaveAlert:
    text: str = ""
    category: str = ""
    axis_ref: str = ""
    date_added: str = ""


@dataclass
class SymptomCoverage:
    symptom: str = ""
    explaining_diagnoses: str = ""
    coverage_pct: int = 0


@dataclass
class InvestigationPlan:
    investigation: str = ""
    fachgebiet: str = ""
    priority: str = ""
    reason: str = ""
    status: str = "offen"


@dataclass
class SymptomTimeline:
    symptom: str = ""
    onset: str = ""
    current_status: str = ""
    therapy_response: str = ""


@dataclass
class HiTOPProfile:
    internalizing: float = 0.0
    thought_disorder: float = 0.0
    disinhibited_externalizing: float = 0.0
    antagonistic_externalizing: float = 0.0
    detachment: float = 0.0
    somatoform: float = 0.0


@dataclass
class FunctioningAssessment:
    gaf_score: int = 0
    whodas_cognition: int = 0
    whodas_mobility: int = 0
    whodas_selfcare: int = 0
    whodas_getting_along: int = 0
    whodas_life_activities: int = 0
    whodas_participation: int = 0
    gdb_score: int = 0
    psychosocial_stressors: list = field(default_factory=list)


@dataclass
class EvidenceEntry:
    axis: str = ""
    document_type: str = ""
    description: str = ""
    date: str = ""
    source: str = ""


@dataclass
class ConditionModel:
    predisposing: list = field(default_factory=list)
    precipitating: list = field(default_factory=list)
    perpetuating: list = field(default_factory=list)
    protective: list = field(default_factory=list)
    narrative: str = ""


@dataclass
class PatientData:
    # Achse I: Psychische Profile
    diagnoses_acute: list = field(default_factory=list)
    diagnoses_chronic: list = field(default_factory=list)
    diagnoses_remitted: list = field(default_factory=list)
    diagnoses_suspected: list = field(default_factory=list)
    diagnoses_excluded: list = field(default_factory=list)
    treatment_history: list = field(default_factory=list)
    compliance_med_self: int = 5
    compliance_med_ext: int = 5
    compliance_therapy: int = 5
    investigation_plan: str = ""
    coverage_analysis: str = ""
    uncovered_symptoms: list = field(default_factory=list)

    # Achse II: Biographie & Entwicklung
    education: str = ""
    iq_estimate: str = ""
    developmental_history: str = ""
    pid5_profile: PID5Profile = field(default_factory=PID5Profile)

    # Achse III: Medizinische Synopse (IIIa-IIIm, symmetrisch zu Achse I)
    med_diagnoses_acute: list = field(default_factory=list)       # IIIa
    med_diagnoses_chronic: list = field(default_factory=list)     # IIIb
    med_diagnoses_contributing: list = field(default_factory=list) # IIIc
    med_diagnoses_remitted: list = field(default_factory=list)    # IIId
    med_remission_factors: list = field(default_factory=list)     # IIIe
    med_treatment_current: str = ""                                # IIIf
    med_treatment_past: str = ""                                   # IIIf
    med_compliance_self: int = 5                                   # IIIg
    med_compliance_ext: int = 5                                    # IIIg
    med_diagnoses_suspected: list = field(default_factory=list)   # IIIh
    med_coverage_analysis: str = ""                                # IIIi
    med_investigation_plan: str = ""                               # IIIj
    medical_conditions: list = field(default_factory=list)        # IIIk (Legacy + Kausalität)
    genetic_factors: str = ""                                      # IIIl
    family_history: str = ""                                       # IIIl
    medications: list = field(default_factory=list)               # IIIm

    # HiTOP-Profil (berechnet aus Cross-Cutting)
    hitop_profile: HiTOPProfile = field(default_factory=HiTOPProfile)

    # Achse IV: Umwelt & Funktion
    functioning: FunctioningAssessment = field(default_factory=FunctioningAssessment)

    # Achse V: Bedingungsmodell
    condition_model: ConditionModel = field(default_factory=ConditionModel)

    # Achse VI: Belegsammlung
    evidence_entries: list = field(default_factory=list)

    # CAVE-Warnhinweise (aus FALLBEZOGENE_AUSWERTUNG-Konzept)
    cave_alerts: list = field(default_factory=list)

    # Strukturierte Symptomabdeckung (aus SYNOPSE_VALIDIERT-Konzept)
    symptom_coverage: list = field(default_factory=list)

    # Priorisierter Untersuchungsplan (aus FALLBEZOGENE_AUSWERTUNG-Konzept)
    investigation_plans: list = field(default_factory=list)

    # Longitudinaler Symptomverlauf (aus SYNOPSE_VALIDIERT-Konzept)
    symptom_timeline: list = field(default_factory=list)

    # Screening-Daten
    crosscutting_level1: dict = field(default_factory=dict)
    crosscutting_triggered: list = field(default_factory=list)
    screening_results: dict = field(default_factory=dict)

    # Gatekeeper-Status
    current_gate: int = 0
    gate_results: dict = field(default_factory=dict)


# ===================================================================
# TRANSLATED DATA FUNCTIONS
# ===================================================================

def get_crosscutting_domains():
    """Return cross-cutting symptom domains with translated strings."""
    return {
        "depression": {
            "label": t("cc_depression_label"),
            "items": [t("cc_depression_item_0"), t("cc_depression_item_1")],
            "threshold": 2,
            "level2_instrument": t("cc_depression_level2")
        },
        "anger": {
            "label": t("cc_anger_label"),
            "items": [t("cc_anger_item_0")],
            "threshold": 2,
            "level2_instrument": t("cc_anger_level2")
        },
        "mania": {
            "label": t("cc_mania_label"),
            "items": [t("cc_mania_item_0"), t("cc_mania_item_1")],
            "threshold": 2,
            "level2_instrument": t("cc_mania_level2")
        },
        "anxiety": {
            "label": t("cc_anxiety_label"),
            "items": [t("cc_anxiety_item_0"), t("cc_anxiety_item_1"), t("cc_anxiety_item_2")],
            "threshold": 2,
            "level2_instrument": t("cc_anxiety_level2")
        },
        "somatic": {
            "label": t("cc_somatic_label"),
            "items": [t("cc_somatic_item_0"), t("cc_somatic_item_1")],
            "threshold": 2,
            "level2_instrument": t("cc_somatic_level2")
        },
        "suicidality": {
            "label": t("cc_suicidality_label"),
            "items": [t("cc_suicidality_item_0")],
            "threshold": 1,
            "level2_instrument": t("cc_suicidality_level2")
        },
        "psychosis": {
            "label": t("cc_psychosis_label"),
            "items": [t("cc_psychosis_item_0"), t("cc_psychosis_item_1")],
            "threshold": 1,
            "level2_instrument": t("cc_psychosis_level2")
        },
        "sleep": {
            "label": t("cc_sleep_label"),
            "items": [t("cc_sleep_item_0")],
            "threshold": 2,
            "level2_instrument": t("cc_sleep_level2")
        },
        "memory": {
            "label": t("cc_memory_label"),
            "items": [t("cc_memory_item_0")],
            "threshold": 2,
            "level2_instrument": t("cc_memory_level2")
        },
        "repetitive": {
            "label": t("cc_repetitive_label"),
            "items": [t("cc_repetitive_item_0"), t("cc_repetitive_item_1")],
            "threshold": 2,
            "level2_instrument": t("cc_repetitive_level2")
        },
        "dissociation": {
            "label": t("cc_dissociation_label"),
            "items": [t("cc_dissociation_item_0")],
            "threshold": 2,
            "level2_instrument": t("cc_dissociation_level2")
        },
        "personality": {
            "label": t("cc_personality_label"),
            "items": [t("cc_personality_item_0"), t("cc_personality_item_1")],
            "threshold": 2,
            "level2_instrument": t("cc_personality_level2")
        },
        "substance": {
            "label": t("cc_substance_label"),
            "items": [t("cc_substance_item_0"), t("cc_substance_item_1"), t("cc_substance_item_2")],
            "threshold": 1,
            "level2_instrument": t("cc_substance_level2")
        }
    }


def get_likert_options():
    """Return translated Likert scale options."""
    return {
        0: t("likert_0"),
        1: t("likert_1"),
        2: t("likert_2"),
        3: t("likert_3"),
        4: t("likert_4")
    }


def get_pid5_domains():
    """Return PID-5 domains with translated strings."""
    return {
        "negative_affectivity": {
            "label": t("pid5_negative_affectivity_label"),
            "items": [t(f"pid5_negative_affectivity_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_negative_affectivity_trait")
        },
        "detachment": {
            "label": t("pid5_detachment_label"),
            "items": [t(f"pid5_detachment_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_detachment_trait")
        },
        "antagonism": {
            "label": t("pid5_antagonism_label"),
            "items": [t(f"pid5_antagonism_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_antagonism_trait")
        },
        "disinhibition": {
            "label": t("pid5_disinhibition_label"),
            "items": [t(f"pid5_disinhibition_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_disinhibition_trait")
        },
        "psychoticism": {
            "label": t("pid5_psychoticism_label"),
            "items": [t(f"pid5_psychoticism_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_psychoticism_trait")
        },
        "anankastia": {
            "label": t("pid5_anankastia_label"),
            "items": [t(f"pid5_anankastia_item_{i}") for i in range(6)],
            "icd11_trait": t("pid5_anankastia_trait")
        }
    }


def get_gatekeeper_steps():
    """Return gatekeeper steps with translated strings."""
    steps = []
    for i in range(8):
        steps.append({
            "id": i,
            "name": t(f"gate{i}_name"),
            "label": t(f"gate{i}_label"),
            "description": t(f"gate{i}_desc")
        })
    return steps


def get_whodas_items():
    """Return WHODAS 2.0 items with translated strings."""
    return [
        {"domain": t(f"whodas_item_{i}_domain"), "item": t(f"whodas_item_{i}_text")}
        for i in range(12)
    ]


def get_whodas_scale():
    """Return translated WHODAS scale."""
    return {i: t(f"whodas_scale_{i}") for i in range(5)}


def get_stressors():
    """Return translated psychosocial stressors list."""
    return [t(f"stressor_{i}") for i in range(12)]


def get_substances():
    """Return translated substance list."""
    return [
        t("gate2_substance_none"), t("gate2_substance_alcohol"),
        t("gate2_substance_cannabis"), t("gate2_substance_opioids"),
        t("gate2_substance_stimulants"), t("gate2_substance_sedatives"),
        t("gate2_substance_hallucinogens"), t("gate2_substance_inhalants"),
        t("gate2_substance_tobacco"), t("gate2_substance_caffeine"),
        t("gate2_substance_other")
    ]


def get_remission_factors():
    """Return translated remission factors list."""
    return [
        t("ax1_rem_factor_unknown"), t("ax1_rem_factor_time"),
        t("ax1_rem_factor_coping"), t("ax1_rem_factor_support"),
        t("ax1_rem_factor_therapy"), t("ax1_rem_factor_medication"),
        t("ax1_rem_factor_lifestyle"), t("ax1_rem_factor_spontaneous")
    ]


def compute_hitop_profile(crosscutting_level1: dict, crosscutting_domains: dict) -> HiTOPProfile:
    """Compute HiTOP spectrum scores from Cross-Cutting Level 1 data.

    Mapping (Kotov et al., 2017):
      Internalizing = max(Depression, Anxiety, Somatic, Sleep)
      Thought Disorder = max(Psychosis, Dissociation)
      Disinhibited Externalizing = max(Substance, Mania)
      Antagonistic Externalizing = max(Anger)
      Detachment = max(Memory [proxy for withdrawal])
      Somatoform = max(Somatic)
    """
    def domain_max(domain_key):
        items = crosscutting_domains.get(domain_key, {}).get("items", [])
        vals = [crosscutting_level1.get(f"{domain_key}_{i}", 0)
                for i in range(len(items))]
        return max(vals) if vals else 0

    return HiTOPProfile(
        internalizing=max(domain_max("depression"), domain_max("anxiety"),
                          domain_max("somatic"), domain_max("sleep")),
        thought_disorder=max(domain_max("psychosis"), domain_max("dissociation")),
        disinhibited_externalizing=max(domain_max("substance"), domain_max("mania")),
        antagonistic_externalizing=domain_max("anger"),
        detachment=domain_max("memory"),
        somatoform=domain_max("somatic"),
    )


def render_hitop_radar(hitop: HiTOPProfile):
    """Render HiTOP spectrum radar chart using Plotly."""
    if not HAS_PLOTLY:
        return
    categories = [
        t("hitop_internalizing"),
        t("hitop_thought_disorder"),
        t("hitop_disinhibited_ext"),
        t("hitop_antagonistic_ext"),
        t("hitop_detachment"),
        t("hitop_somatoform"),
    ]
    values = [
        hitop.internalizing,
        hitop.thought_disorder,
        hitop.disinhibited_externalizing,
        hitop.antagonistic_externalizing,
        hitop.detachment,
        hitop.somatoform,
    ]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure(data=go.Scatterpolar(
        r=values_closed, theta=categories_closed,
        fill='toself', line_color='#dc322f',
        name='HiTOP'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
        showlegend=False, height=400,
        title=t("hitop_title")
    )
    st.plotly_chart(fig, use_container_width=True)


# ===================================================================
# STREAMLIT-ANWENDUNG
# ===================================================================

st.set_page_config(
    page_title="Multiaxiales Diagnostik-Expertensystem v9",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    .axis-header {
        background-color: #002b36;
        color: #93a1a1;
        padding: 12px 16px;
        border-radius: 5px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        font-size: 1.1em;
    }
    .gate-active { color: #268bd2; font-weight: bold; }
    .gate-done { color: #859900; }
    .gate-locked { color: #586e75; }
    .status-alert { padding: 8px 12px; border-radius: 4px; margin: 4px 0; }
    .suspected { background-color: #fdf6e3; border-left: 4px solid #b58900; }
    .excluded { background-color: #eee8d5; border-left: 4px solid #586e75; }
    .critical { background-color: #fdf6e3; border-left: 4px solid #dc322f; }
    .coverage-gap { background-color: #fce4e4; border-left: 4px solid #dc322f;
                    padding: 8px 12px; border-radius: 4px; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialisierung ---
if 'patient' not in st.session_state:
    st.session_state.patient = PatientData()

if 'current_gate' not in st.session_state:
    st.session_state.current_gate = 0

if 'lang' not in st.session_state:
    st.session_state.lang = "de"


def get_patient() -> PatientData:
    return st.session_state.patient


# ===================================================================
# SIDEBAR: Language, Navigation & Gatekeeper-Status
# ===================================================================

st.sidebar.title(t("sidebar_title"))
st.sidebar.markdown("---")

# Language Selector
lang_options = ["Deutsch", "English"]
lang_index = 0 if st.session_state.lang == "de" else 1
lang_choice = st.sidebar.selectbox(
    "🌐 Sprache / Language",
    lang_options,
    index=lang_index,
    key="lang_select"
)
st.session_state.lang = "de" if lang_choice == "Deutsch" else "en"

st.sidebar.markdown("---")

# Gatekeeper-Fortschritt
st.sidebar.subheader(t("gatekeeper_progress"))
gatekeeper_steps = get_gatekeeper_steps()
for step in gatekeeper_steps:
    idx = step["id"]
    if idx < st.session_state.current_gate:
        st.sidebar.markdown(f"<span class='gate-done'>✅ {step['label']}</span>",
                            unsafe_allow_html=True)
    elif idx == st.session_state.current_gate:
        st.sidebar.markdown(f"<span class='gate-active'>🔄 {step['label']}</span>",
                            unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"<span class='gate-locked'>🔒 {step['label']}</span>",
                            unsafe_allow_html=True)

st.sidebar.markdown("---")

# Achsen-Navigation
nav_options = [
    t("nav_gatekeeper"),
    t("nav_axis1"),
    t("nav_axis2"),
    t("nav_axis3"),
    t("nav_axis4"),
    t("nav_axis5"),
    t("nav_axis6"),
    t("nav_synopsis")
]
menu = st.sidebar.radio(t("nav_label"), nav_options)


# ===================================================================
# GATEKEEPER-PROZESS
# ===================================================================

if menu == t("nav_gatekeeper"):
    st.markdown(f"<div class='axis-header'>{t('header_gatekeeper')}</div>",
                unsafe_allow_html=True)

    current = st.session_state.current_gate
    steps = get_gatekeeper_steps()
    if current < len(steps):
        step = steps[current]
        st.info(f"**{step['label']}**\n\n{step['description']}")

    # --- Stufe 0: Intake ---
    if current == 0:
        st.subheader(t("intake_subheader"))
        with st.form("intake_form"):
            col1, col2 = st.columns(2)
            col1.text_input(t("intake_name"), key="intake_name")
            col2.date_input(t("intake_dob"), key="intake_dob",
                            value=datetime.date(1990, 1, 1))
            st.text_area(t("intake_reason"), key="intake_reason")
            if st.form_submit_button(t("intake_submit")):
                st.session_state.current_gate = 1
                st.rerun()

    # --- Stufe 1: Simulationsausschluss ---
    elif current == 1:
        st.subheader(t("gate1_subheader"))
        with st.form("gate1_form"):
            st.write(t("gate1_evaluate"))
            g1_1 = st.selectbox(t("gate1_inconsistency"),
                                [t("gate1_inconsistency_0"), t("gate1_inconsistency_1"),
                                 t("gate1_inconsistency_2"), t("gate1_inconsistency_3")],
                                key="g1_inconsistency")
            g1_2 = st.selectbox(t("gate1_incentive"),
                                [t("gate1_incentive_0"), t("gate1_incentive_1"),
                                 t("gate1_incentive_2"), t("gate1_incentive_3")],
                                key="g1_incentive")
            g1_3 = st.selectbox(t("gate1_cooperation"),
                                [t("gate1_cooperation_0"), t("gate1_cooperation_1"),
                                 t("gate1_cooperation_2")],
                                key="g1_cooperation")
            g1_note = st.text_area(t("gate1_notes"), key="g1_notes")

            if st.form_submit_button(t("gate1_submit")):
                p = get_patient()
                p.gate_results["step1_malingering"] = {
                    "inconsistency": g1_1,
                    "incentive": g1_2,
                    "cooperation": g1_3,
                    "notes": g1_note,
                    "passed": g1_1 != t("gate1_inconsistency_3") and g1_2 != t("gate1_incentive_3")
                }
                if g1_1 == t("gate1_inconsistency_3") or g1_2 == t("gate1_incentive_3"):
                    st.warning(t("gate1_warning"))
                st.session_state.current_gate = 2
                st.rerun()

    # --- Stufe 2: Substanzausschluss ---
    elif current == 2:
        st.subheader(t("gate2_subheader"))
        with st.form("gate2_form"):
            g2_substances = st.multiselect(
                t("gate2_substances_label"),
                get_substances()
            )
            g2_temporal = st.selectbox(
                t("gate2_temporal"),
                [t("gate2_temporal_0"), t("gate2_temporal_1"),
                 t("gate2_temporal_2"), t("gate2_temporal_3")]
            )
            g2_history = st.text_area(t("gate2_history"))

            if st.form_submit_button(t("gate2_submit")):
                p = get_patient()
                p.gate_results["step2_substance"] = {
                    "substances": g2_substances,
                    "temporal_relation": g2_temporal,
                    "history": g2_history,
                    "substance_induced": g2_temporal == t("gate2_temporal_3")
                }
                st.session_state.current_gate = 3
                st.rerun()

    # --- Stufe 3: Medizinischer Ausschluss ---
    elif current == 3:
        st.subheader(t("gate3_subheader"))
        with st.form("gate3_form"):
            g3_conditions = st.text_area(t("gate3_conditions"))
            g3_causality = st.selectbox(
                t("gate3_causality"),
                [t("gate3_causality_0"), t("gate3_causality_1"), t("gate3_causality_2")]
            )
            g3_labs = st.text_area(t("gate3_labs"))

            if st.form_submit_button(t("gate3_submit")):
                p = get_patient()
                p.gate_results["step3_medical"] = {
                    "conditions": g3_conditions,
                    "causality": g3_causality,
                    "labs": g3_labs,
                    "fully_explained": g3_causality == t("gate3_causality_2")
                }
                st.session_state.current_gate = 4
                st.rerun()

    # --- Stufe 4: Cross-Cutting Screening ---
    elif current == 4:
        st.subheader(t("gate4_subheader"))
        st.write(t("gate4_instruction"))

        crosscutting_domains = get_crosscutting_domains()
        likert_options = get_likert_options()

        with st.form("crosscutting_form"):
            responses = {}
            for domain_key, domain in crosscutting_domains.items():
                st.markdown(f"**{domain['label']}** "
                            f"({t('gate4_threshold')}: ≥{domain['threshold']})")
                for i, item_text in enumerate(domain["items"]):
                    val = st.select_slider(
                        item_text,
                        options=list(likert_options.values()),
                        key=f"cc_{domain_key}_{i}"
                    )
                    # Extrahiere numerischen Wert
                    num_val = int(val.split("(")[1].replace(")", ""))
                    responses[f"{domain_key}_{i}"] = num_val
                st.markdown("---")

            if st.form_submit_button(t("gate4_submit")):
                p = get_patient()
                p.crosscutting_level1 = responses

                # Schwellenlogik
                triggered = []
                for domain_key, domain in crosscutting_domains.items():
                    domain_max = 0
                    for i in range(len(domain["items"])):
                        val = responses.get(f"{domain_key}_{i}", 0)
                        domain_max = max(domain_max, val)
                    if domain_max >= domain["threshold"]:
                        triggered.append({
                            "domain": domain_key,
                            "label": domain["label"],
                            "max_score": domain_max,
                            "threshold": domain["threshold"],
                            "level2": domain["level2_instrument"]
                        })

                p.crosscutting_triggered = triggered

                # HiTOP-Spektren berechnen
                p.hitop_profile = compute_hitop_profile(
                    responses, crosscutting_domains)

                st.session_state.current_gate = 5
                st.rerun()

    # --- Stufe 5: Störungsspezifische Module ---
    elif current == 5:
        st.subheader(t("gate5_subheader"))
        p = get_patient()

        if p.crosscutting_triggered:
            st.write(f"**{t('gate5_triggered')}**")
            for tr in p.crosscutting_triggered:
                safety = t("gate5_safety_critical") if tr["threshold"] == 1 and tr["max_score"] >= 1 else ""
                st.markdown(
                    f"<div class='status-alert {'critical' if safety else 'suspected'}'>"
                    f"<b>{tr['label']}</b>: {t('gate5_max_score')} {tr['max_score']} "
                    f"({t('gate4_threshold')} ≥{tr['threshold']}){safety}<br/>"
                    f"→ Level 2: {tr['level2']}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success(t("gate5_no_trigger"))

        # HiTOP-Spektren-Radar anzeigen
        if p.crosscutting_level1:
            st.markdown("---")
            st.subheader(t("hitop_title"))
            st.caption(t("hitop_info"))
            render_hitop_radar(p.hitop_profile)
        else:
            st.info(t("hitop_no_data"))

        st.markdown("---")
        st.write(f"**{t('gate5_diag_assessment')}**")

        with st.form("disorder_module_form"):
            diag_name = st.text_input(t("gate5_diag_name"))
            col1, col2 = st.columns(2)
            diag_icd11 = col1.text_input(t("gate5_icd11_code"))
            diag_dsm5 = col2.text_input(t("gate5_dsm5_code"))
            status_options = [t("gate5_status_acute"), t("gate5_status_chronic"),
                              t("gate5_status_suspected"), t("gate5_status_excluded")]
            diag_status = st.selectbox(t("gate5_status"), status_options)

            # NEU: Konfidenz & Severity (inspiriert durch FALLBEZOGENE_AUSWERTUNG)
            col_c, col_s = st.columns(2)
            diag_confidence = col_c.slider(
                t("diag_confidence"), 0, 100, 50,
                help=t("diag_confidence_help"))
            severity_options = [t("diag_severity_low"), t("diag_severity_medium"),
                                t("diag_severity_high"), t("diag_severity_very_high")]
            diag_severity = col_s.selectbox(t("diag_severity"), severity_options)

            diag_evidence = st.text_area(t("gate5_evidence"))

            # NEU: PRO/CONTRA-Evidenzbewertung
            col_pro, col_con = st.columns(2)
            diag_pro = col_pro.text_area(t("diag_pro_evidence"), height=80)
            diag_contra = col_con.text_area(t("diag_contra_evidence"), height=80)

            if st.form_submit_button(t("gate5_add_diag")):
                diag = Diagnosis(
                    code_icd11=diag_icd11,
                    code_dsm5=diag_dsm5,
                    name=diag_name,
                    status=diag_status.lower(),
                    evidence=diag_evidence,
                    confidence_pct=diag_confidence,
                    severity=diag_severity,
                    evidence_pro=diag_pro,
                    evidence_contra=diag_contra
                )
                if diag_status == t("gate5_status_acute"):
                    p.diagnoses_acute.append(asdict(diag))
                elif diag_status == t("gate5_status_chronic"):
                    p.diagnoses_chronic.append(asdict(diag))
                elif diag_status == t("gate5_status_suspected"):
                    p.diagnoses_suspected.append(asdict(diag))
                elif diag_status == t("gate5_status_excluded"):
                    p.diagnoses_excluded.append(asdict(diag))
                st.rerun()

        # Aktuelle Diagnosen anzeigen
        all_diags = (p.diagnoses_acute + p.diagnoses_chronic +
                     p.diagnoses_suspected + p.diagnoses_excluded)
        if all_diags and HAS_PANDAS:
            df = pd.DataFrame(all_diags)[["name", "code_icd11", "code_dsm5", "status"]]
            st.table(df)

        if st.button(t("gate5_to_gate6")):
            st.session_state.current_gate = 6
            st.rerun()

    # --- Stufe 6: Funktionsniveau ---
    elif current == 6:
        st.subheader(t("gate6_subheader"))
        p = get_patient()

        tab_gaf, tab_whodas, tab_gdb = st.tabs(["GAF", "WHODAS 2.0", "GdB"])

        with tab_gaf:
            p.functioning.gaf_score = st.slider(
                t("gate6_gaf_label"),
                min_value=0, max_value=100, value=p.functioning.gaf_score,
                help=t("gate6_gaf_help")
            )
            st.caption(t("gate6_gaf_note"))

        with tab_whodas:
            st.write(f"**{t('gate6_whodas_title')}**")
            st.write(t("gate6_whodas_instruction"))
            whodas_items = get_whodas_items()
            whodas_scale = get_whodas_scale()
            with st.form("whodas_form"):
                whodas_scores = []
                for i, item in enumerate(whodas_items):
                    val = st.select_slider(
                        f"[{item['domain']}] {item['item']}",
                        options=list(whodas_scale.values()),
                        key=f"whodas_{i}"
                    )
                    num = list(whodas_scale.values()).index(val)
                    whodas_scores.append(num)

                if st.form_submit_button(t("gate6_whodas_submit")):
                    total = sum(whodas_scores)
                    max_score = len(whodas_items) * 4
                    pct = (total / max_score) * 100
                    st.metric(t("gate6_whodas_total"),
                              f"{total}/{max_score} ({pct:.0f}%)")

        with tab_gdb:
            p.functioning.gdb_score = st.slider(
                t("gate6_gdb_label"),
                min_value=0, max_value=100, step=10,
                value=p.functioning.gdb_score,
                help=t("gate6_gdb_help")
            )
            if p.functioning.gdb_score >= 50:
                st.warning(f"{t('gate6_gdb_warning')} (GdB {p.functioning.gdb_score})")

        st.markdown("---")
        st.write(f"**{t('gate6_stressors_label')}**")
        stressors = st.multiselect(
            t("gate6_stressors_select"),
            get_stressors()
        )
        p.functioning.psychosocial_stressors = stressors

        if st.button(t("gate6_to_synopsis")):
            st.session_state.current_gate = 7
            st.rerun()

    # --- Stufe 7: Synopse ---
    elif current >= 7:
        st.subheader(t("gate7_complete"))
        st.success(t("gate7_success"))
        if st.button(t("gate7_reset")):
            st.session_state.current_gate = 0
            st.rerun()


# ===================================================================
# ACHSE I: PSYCHISCHE PROFILE (ERWEITERT)
# ===================================================================

elif menu == t("nav_axis1"):
    st.markdown(f"<div class='axis-header'>{t('header_axis1')}</div>",
                unsafe_allow_html=True)
    p = get_patient()

    tab_diag, tab_rem, tab_treat, tab_plan = st.tabs([
        t("ax1_tab_diag"),
        t("ax1_tab_rem"),
        t("ax1_tab_treat"),
        t("ax1_tab_plan")
    ])

    with tab_diag:
        st.subheader(t("ax1_diag_subheader"))
        st.write(f"**{t('ax1_diag_current')}**")
        for d in p.diagnoses_acute:
            st.success(f"🔴 {t('ax1_acute_prefix')}: {d['name']} ({d.get('code_icd11','')}/{d.get('code_dsm5','')})")
        for d in p.diagnoses_chronic:
            st.info(f"🟡 {t('ax1_chronic_prefix')}: {d['name']} ({d.get('code_icd11','')}/{d.get('code_dsm5','')})")

        st.write(f"**{t('ax1_suspected_header')}**")
        for d in p.diagnoses_suspected:
            st.markdown(
                f"<div class='status-alert suspected'>? {t('ax1_suspected_prefix')}: {d['name']}</div>",
                unsafe_allow_html=True
            )

        st.write(f"**{t('ax1_excluded_header')}**")
        for d in p.diagnoses_excluded:
            st.markdown(
                f"<div class='status-alert excluded'>✖ {t('ax1_excluded_prefix')}: {d['name']}</div>",
                unsafe_allow_html=True
            )

    with tab_rem:
        st.subheader(t("ax1_rem_subheader"))
        with st.form("remission_form"):
            rem_name = st.text_input(t("ax1_rem_name"))
            rem_factors = st.multiselect(
                t("ax1_rem_factors"),
                get_remission_factors()
            )
            rem_evidence = st.text_area(t("ax1_rem_evidence"))
            if st.form_submit_button(t("ax1_rem_submit")):
                p.diagnoses_remitted.append(asdict(Diagnosis(
                    name=rem_name,
                    status="remittiert",
                    evidence=rem_evidence,
                    remission_factors=rem_factors
                )))
                st.rerun()

        for d in p.diagnoses_remitted:
            factors = ", ".join(d.get("remission_factors", []))
            st.success(f"✅ {t('ax1_rem_prefix')}: {d['name']} ({t('ax1_rem_factors_label')}: {factors})")

    with tab_treat:
        st.subheader(t("ax1_treat_subheader"))
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{t('ax1_treat_current')}**")
            st.text_area(t("ax1_treat_current_area"), key="curr_treat_ax1")
        with col2:
            st.write(f"**{t('ax1_treat_past')}**")
            st.text_area(t("ax1_treat_past_area"), key="past_treat_ax1")

        st.subheader(t("ax1_compliance_subheader"))
        c1, c2, c3 = st.columns(3)
        p.compliance_med_self = c1.slider(t("ax1_compliance_med_self"), 0, 10,
                                          p.compliance_med_self)
        p.compliance_med_ext = c2.slider(t("ax1_compliance_med_ext"), 0, 10,
                                         p.compliance_med_ext)
        p.compliance_therapy = c3.slider(t("ax1_compliance_therapy"), 0, 10,
                                         p.compliance_therapy)

    with tab_plan:
        st.subheader(t("ax1_plan_subheader"))

        # ── Ii: STRUKTURIERTE SYMPTOMABDECKUNG ──
        st.subheader(t("ax1_coverage_subheader"))
        st.info(t("ax1_coverage_info"))

        # Strukturierte Symptom-Diagnosen-Zuordnung (aus SYNOPSE_VALIDIERT)
        st.markdown(f"**{t('coverage_structured_title')}**")
        with st.form("coverage_form"):
            col1, col2, col3 = st.columns([3, 3, 1])
            cov_symptom = col1.text_input(t("coverage_symptom"))
            cov_diag = col2.text_input(t("coverage_explaining_diag"))
            cov_pct = col3.number_input(t("coverage_pct"), 0, 100, 85)
            if st.form_submit_button(t("coverage_add")):
                p.symptom_coverage.append(asdict(SymptomCoverage(
                    symptom=cov_symptom,
                    explaining_diagnoses=cov_diag,
                    coverage_pct=cov_pct
                )))
                st.rerun()

        if p.symptom_coverage:
            if HAS_PANDAS:
                df_cov = pd.DataFrame(p.symptom_coverage)
                st.table(df_cov)
            # Gesamt-Abdeckungsmetrik berechnen
            total_pct = sum(c.get("coverage_pct", 0) for c in p.symptom_coverage) / len(p.symptom_coverage) if p.symptom_coverage else 0
            full = sum(1 for c in p.symptom_coverage if c.get("coverage_pct", 0) >= 85)
            partial = sum(1 for c in p.symptom_coverage if 60 <= c.get("coverage_pct", 0) < 85)
            insuff = sum(1 for c in p.symptom_coverage if c.get("coverage_pct", 0) < 60)

            st.metric(t("coverage_total"), f"~{total_pct:.0f}%")
            col_f, col_p, col_i = st.columns(3)
            col_f.metric(t("coverage_full"), f"{full}/{len(p.symptom_coverage)}")
            col_p.metric(t("coverage_partial"), f"{partial}/{len(p.symptom_coverage)}")
            col_i.metric(t("coverage_insufficient"), f"{insuff}/{len(p.symptom_coverage)}")

        # Legacy-Freitext
        p.coverage_analysis = st.text_area(
            t("ax1_coverage_label"),
            value=p.coverage_analysis,
            placeholder=t("ax1_coverage_placeholder")
        )

        st.markdown("---")

        # ── Ij: PRIORISIERTER UNTERSUCHUNGSPLAN ──
        st.subheader(t("ax1_plan_next_steps"))

        with st.form("inv_plan_form"):
            col1, col2 = st.columns(2)
            inv_name = col1.text_input(t("inv_plan_investigation"))
            inv_fach = col2.text_input(t("inv_plan_fachgebiet"))
            col3, col4 = st.columns(2)
            inv_prio = col3.selectbox(t("inv_plan_priority"), [
                t("inv_plan_dringend"), t("inv_plan_wichtig"), t("inv_plan_verlauf")
            ])
            inv_reason = col4.text_input(t("inv_plan_reason"))
            if st.form_submit_button(t("inv_plan_add")):
                p.investigation_plans.append(asdict(InvestigationPlan(
                    investigation=inv_name, fachgebiet=inv_fach,
                    priority=inv_prio, reason=inv_reason
                )))
                st.rerun()

        if p.investigation_plans and HAS_PANDAS:
            df_inv = pd.DataFrame(p.investigation_plans)[
                ["priority", "investigation", "fachgebiet", "reason"]]
            st.table(df_inv)

        # Legacy-Freitext
        p.investigation_plan = st.text_area(
            t("ax1_plan_next_steps"),
            value=p.investigation_plan,
            key="inv_plan_legacy"
        )


# ===================================================================
# ACHSE II: BIOGRAPHIE & PERSÖNLICHKEIT
# ===================================================================

elif menu == t("nav_axis2"):
    st.markdown(f"<div class='axis-header'>{t('header_axis2')}</div>",
                unsafe_allow_html=True)
    p = get_patient()

    tab_bio, tab_pid5 = st.tabs([t("ax2_tab_bio"), t("ax2_tab_pid5")])

    with tab_bio:
        p.education = st.text_area(t("ax2_education"), value=p.education)
        p.iq_estimate = st.text_input(t("ax2_iq"), value=p.iq_estimate)
        p.developmental_history = st.text_area(
            t("ax2_developmental"),
            value=p.developmental_history
        )

    with tab_pid5:
        st.subheader(t("ax2_pid5_subheader"))
        st.write(t("ax2_pid5_instruction"))

        pid5_domains = get_pid5_domains()
        domain_scores = {}
        for domain_key, domain in pid5_domains.items():
            st.markdown(f"**{domain['label']}** ({domain['icd11_trait']})")
            scores = []
            for i, item in enumerate(domain["items"]):
                val = st.slider(item, 0, 3, 0, key=f"pid5_{domain_key}_{i}")
                scores.append(val)
            domain_mean = sum(scores) / len(scores) if scores else 0
            domain_scores[domain_key] = round(domain_mean, 2)
            st.caption(f"{t('ax2_pid5_domain_mean')}: {domain_mean:.2f}")
            st.markdown("---")

        # PID-5 Profil speichern
        p.pid5_profile = PID5Profile(
            negative_affectivity=domain_scores.get("negative_affectivity", 0),
            detachment=domain_scores.get("detachment", 0),
            antagonism=domain_scores.get("antagonism", 0),
            disinhibition=domain_scores.get("disinhibition", 0),
            psychoticism=domain_scores.get("psychoticism", 0),
            anankastia=domain_scores.get("anankastia", 0)
        )

        # Radar-Chart
        if HAS_PLOTLY:
            st.subheader(t("ax2_pid5_radar_title"))
            categories = [d["label"] for d in pid5_domains.values()]
            values = list(domain_scores.values())
            values.append(values[0])  # Kreis schließen
            categories.append(categories[0])

            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='PID-5',
                line_color='#268bd2'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 3])),
                showlegend=False,
                title=t("ax2_pid5_chart_title")
            )
            st.plotly_chart(fig, use_container_width=True)


# ===================================================================
# ACHSE III: MEDIZINISCHE SYNOPSE (IIIa - IIIm, SYMMETRISCH ZU ACHSE I)
# ===================================================================

elif menu == t("nav_axis3"):
    st.markdown(f"<div class='axis-header'>{t('header_axis3')}</div>",
                unsafe_allow_html=True)
    p = get_patient()

    # 13 Subachsen als Tabs (in 2 Reihen organisiert via Expander + Tabs)
    tab_acute, tab_chronic, tab_contrib, tab_rem, tab_remf = st.tabs([
        t("ax3_tab_acute"),
        t("ax3_tab_chronic"),
        t("ax3_tab_contributing"),
        t("ax3_tab_remitted"),
        t("ax3_tab_rem_factors"),
    ])

    # --- IIIa: Akute medizinische Diagnosen ---
    with tab_acute:
        st.subheader(t("ax3_acute_subheader"))
        with st.form("med_acute_form"):
            mc_name = st.text_input(t("ax3_med_diag_name"), key="iiia_name")
            col1, col2 = st.columns(2)
            mc_code = col1.text_input(t("ax3_med_diag_code"), key="iiia_code")
            mc_dsm = col2.text_input(t("ax3_med_diag_dsm_code"), key="iiia_dsm")
            mc_evidence = st.text_area(t("ax3_evidence"), key="iiia_evidence")
            if st.form_submit_button(t("ax3_add_condition")):
                p.med_diagnoses_acute.append(asdict(MedicalCondition(
                    name=mc_name, icd11_code=mc_code, dsm5_code=mc_dsm,
                    status="akut", evidence=mc_evidence
                )))
                st.rerun()
        for d in p.med_diagnoses_acute:
            st.error(f"🔴 {d['name']} ({d.get('icd11_code','')}/{d.get('dsm5_code','')})")

    # --- IIIb: Chronische medizinische Diagnosen (vollständig erklärend) ---
    with tab_chronic:
        st.subheader(t("ax3_chronic_subheader"))
        with st.form("med_chronic_form"):
            mc_name = st.text_input(t("ax3_med_diag_name"), key="iiib_name")
            col1, col2 = st.columns(2)
            mc_code = col1.text_input(t("ax3_med_diag_code"), key="iiib_code")
            mc_dsm = col2.text_input(t("ax3_med_diag_dsm_code"), key="iiib_dsm")
            mc_causality = st.selectbox(
                t("ax3_causality_label"),
                [t("ax3_causality_full"), t("ax3_causality_contributing"),
                 t("ax3_causality_independent")],
                key="iiib_causality"
            )
            mc_evidence = st.text_area(t("ax3_evidence"), key="iiib_evidence")
            if st.form_submit_button(t("ax3_add_condition")):
                p.med_diagnoses_chronic.append(asdict(MedicalCondition(
                    name=mc_name, icd11_code=mc_code, dsm5_code=mc_dsm,
                    status="chronisch", causality=mc_causality,
                    evidence=mc_evidence
                )))
                st.rerun()
        for d in p.med_diagnoses_chronic:
            st.warning(f"🟡 {d['name']} ({d.get('icd11_code','')}) [{d.get('causality','')}]")

    # --- IIIc: Beitragende medizinische Faktoren ---
    with tab_contrib:
        st.subheader(t("ax3_contributing_subheader"))
        with st.form("med_contrib_form"):
            mc_name = st.text_input(t("ax3_med_diag_name"), key="iiic_name")
            mc_code = st.text_input(t("ax3_med_diag_code"), key="iiic_code")
            mc_evidence = st.text_area(t("ax3_evidence"), key="iiic_evidence")
            if st.form_submit_button(t("ax3_add_condition")):
                p.med_diagnoses_contributing.append(asdict(MedicalCondition(
                    name=mc_name, icd11_code=mc_code,
                    status="aktiv", causality="beitragend",
                    evidence=mc_evidence
                )))
                st.rerun()
        for d in p.med_diagnoses_contributing:
            st.info(f"◐ {d['name']} ({d.get('icd11_code','')})")

    # --- IIId: Remittierte medizinische Erkrankungen ---
    with tab_rem:
        st.subheader(t("ax3_remitted_subheader"))
        with st.form("med_remitted_form"):
            mr_name = st.text_input(t("ax3_med_rem_name"), key="iiid_name")
            mr_factors = st.multiselect(t("ax3_med_rem_factors"),
                                        get_remission_factors(), key="iiid_factors")
            mr_evidence = st.text_area(t("ax3_med_rem_evidence"), key="iiid_evidence")
            if st.form_submit_button(t("ax3_med_rem_submit")):
                p.med_diagnoses_remitted.append(asdict(MedicalCondition(
                    name=mr_name, status="remittiert",
                    evidence=mr_evidence, remission_factors=mr_factors
                )))
                st.rerun()
        for d in p.med_diagnoses_remitted:
            factors = ", ".join(d.get("remission_factors", []))
            st.success(f"✅ {d['name']} ({factors})")

    # --- IIIe: Remissionsfaktoren ---
    with tab_remf:
        st.subheader(t("ax3_rem_factors_subheader"))
        st.info("Detaillierte Analyse der Remissionsfaktoren für medizinische Erkrankungen. "
                "Siehe auch IIId für einzelne remittierte Diagnosen.")

    # --- Zweite Reihe Tabs: IIIf-IIIm ---
    tab_treat, tab_compl, tab_susp, tab_cov = st.tabs([
        t("ax3_tab_treatment"),
        t("ax3_tab_compliance"),
        t("ax3_tab_suspected"),
        t("ax3_tab_coverage"),
    ])

    # --- IIIf: Medizinische Behandlungsgeschichte ---
    with tab_treat:
        st.subheader(t("ax3_treatment_subheader"))
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{t('ax3_med_treatment_current')}**")
            p.med_treatment_current = st.text_area(
                t("ax3_med_treatment_current"),
                value=p.med_treatment_current,
                key="iiif_current", label_visibility="collapsed"
            )
        with col2:
            st.write(f"**{t('ax3_med_treatment_past')}**")
            p.med_treatment_past = st.text_area(
                t("ax3_med_treatment_past"),
                value=p.med_treatment_past,
                key="iiif_past", label_visibility="collapsed"
            )

    # --- IIIg: Medizinische Therapietreue ---
    with tab_compl:
        st.subheader(t("ax3_med_compliance_subheader"))
        c1, c2 = st.columns(2)
        p.med_compliance_self = c1.slider(
            t("ax3_med_compliance_self"), 0, 10,
            p.med_compliance_self, key="iiig_self")
        p.med_compliance_ext = c2.slider(
            t("ax3_med_compliance_ext"), 0, 10,
            p.med_compliance_ext, key="iiig_ext")

    # --- IIIh: Verdachtsdiagnosen (medizinisch) ---
    with tab_susp:
        st.subheader(t("ax3_suspected_subheader"))
        with st.form("med_suspected_form"):
            ms_name = st.text_input(t("ax3_med_diag_name"), key="iiih_name")
            ms_code = st.text_input(t("ax3_med_diag_code"), key="iiih_code")
            ms_evidence = st.text_area(t("ax3_evidence"), key="iiih_evidence")
            if st.form_submit_button(t("ax3_add_condition")):
                p.med_diagnoses_suspected.append(asdict(MedicalCondition(
                    name=ms_name, icd11_code=ms_code,
                    status="Verdacht", evidence=ms_evidence
                )))
                st.rerun()
        for d in p.med_diagnoses_suspected:
            st.markdown(
                f"<div class='status-alert suspected'>? {t('ax3_med_suspected_prefix')}: "
                f"{d['name']} ({d.get('icd11_code','')})</div>",
                unsafe_allow_html=True
            )

    # --- IIIi: Medizinische Abdeckungsanalyse ---
    with tab_cov:
        st.subheader(t("ax3_coverage_subheader"))
        st.info(t("ax3_med_coverage_info"))
        p.med_coverage_analysis = st.text_area(
            t("ax3_med_coverage_label"),
            value=p.med_coverage_analysis,
            key="iiii_coverage"
        )

    # --- Dritte Reihe: IIIj-IIIm ---
    tab_plan, tab_caus, tab_gen, tab_med = st.tabs([
        t("ax3_tab_plan"),
        t("ax3_tab_causality"),
        t("ax3_tab_genetics"),
        t("ax3_tab_medication"),
    ])

    # --- IIIj: Medizinischer Untersuchungsplan ---
    with tab_plan:
        st.subheader(t("ax3_plan_subheader"))
        p.med_investigation_plan = st.text_area(
            t("ax3_med_plan_label"),
            value=p.med_investigation_plan,
            key="iiij_plan"
        )

    # --- IIIk: Kausalitätsanalyse ---
    with tab_caus:
        st.subheader(t("ax3_causality_subheader"))
        st.info(t("ax3_causality_iiib_info"))

        # Alle medizinischen Diagnosen sammeln (aus allen Subachsen)
        all_med = (p.med_diagnoses_acute + p.med_diagnoses_chronic +
                   p.med_diagnoses_contributing + p.medical_conditions)

        causality_full_text = t("ax3_causality_full")
        causality_contrib_text = t("ax3_causality_contributing")
        iiib = [c for c in all_med if causality_full_text in c.get("causality", "")]
        iiic = [c for c in all_med if causality_contrib_text in c.get("causality", "")]

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{t('ax3_iiib_header')}**")
            for c in iiib:
                st.error(f"⬤ {c['name']} ({c.get('icd11_code', '')})")
            if not iiib:
                st.caption("—")
        with col2:
            st.write(f"**{t('ax3_iiic_header')}**")
            for c in iiic:
                st.warning(f"◐ {c['name']} ({c.get('icd11_code', '')})")
            if not iiic:
                st.caption("—")

    # --- IIIl: Genetik & Familiäre Belastung ---
    with tab_gen:
        st.subheader(t("ax3_genetics_subheader"))
        p.genetic_factors = st.text_area(t("ax3_genetic"),
                                         value=p.genetic_factors, key="iiil_genetic")
        p.family_history = st.text_area(t("ax3_family_history"),
                                         value=p.family_history, key="iiil_family")

    # --- IIIm: Medikamentenanamnese & Interaktionen ---
    with tab_med:
        st.subheader(t("ax3_medication_subheader"))
        with st.form("medication_form"):
            col1, col2, col3 = st.columns(3)
            med_name = col1.text_input(t("ax3_medication_name"), key="iiim_name")
            med_dose = col2.text_input(t("ax3_medication_dose"), key="iiim_dose")
            med_unit = col3.text_input(t("ax3_medication_unit"), key="iiim_unit")
            col4, col5 = st.columns(2)
            med_purpose = col4.text_input(t("ax3_medication_purpose"), key="iiim_purpose")
            med_since = col5.text_input(t("ax3_medication_since"), key="iiim_since")
            med_schedule = st.text_input(t("ax3_medication_schedule"), key="iiim_schedule")
            med_effect = st.text_input(t("ax3_medication_effect"), key="iiim_effect")
            med_rating = st.slider(t("ax3_medication_rating"), 0, 10, 5, key="iiim_rating")
            med_side = st.text_input(t("ax3_medication_side_effects"), key="iiim_side")
            med_inter = st.text_input(t("ax3_medication_interactions"), key="iiim_inter")
            if st.form_submit_button(t("ax3_medication_add")):
                p.medications.append(asdict(MedicationEntry(
                    name=med_name, dose=med_dose, unit=med_unit,
                    purpose=med_purpose, since=med_since,
                    schedule=med_schedule, effect=med_effect,
                    effect_rating=med_rating,
                    side_effects=med_side, interactions=med_inter
                )))
                st.rerun()

        if p.medications and HAS_PANDAS:
            df = pd.DataFrame(p.medications)[
                ["name", "dose", "unit", "purpose", "since", "schedule",
                 "effect", "effect_rating", "side_effects"]]
            st.table(df)


# ===================================================================
# ACHSE IV: UMWELT & FUNKTION
# ===================================================================

elif menu == t("nav_axis4"):
    st.markdown(f"<div class='axis-header'>{t('header_axis4')}</div>",
                unsafe_allow_html=True)
    st.info(t("ax4_see_gate6"))
    p = get_patient()

    st.subheader(t("ax4_stressors_subheader"))
    stressors = st.multiselect(
        t("ax4_stressors_select"),
        get_stressors(),
        default=p.functioning.psychosocial_stressors
    )
    p.functioning.psychosocial_stressors = stressors

    st.subheader(t("ax4_functioning_summary"))
    col1, col2, col3 = st.columns(3)
    col1.metric("GAF", f"{p.functioning.gaf_score}/100")
    col2.metric("GdB", f"{p.functioning.gdb_score}")
    col3.metric(t("ax4_stressors_count"), f"{len(p.functioning.psychosocial_stressors)}")


# ===================================================================
# ACHSE V: INTEGRIERTES BEDINGUNGSMODELL
# ===================================================================

elif menu == t("nav_axis5"):
    st.markdown(f"<div class='axis-header'>{t('header_axis5')}</div>",
                unsafe_allow_html=True)
    p = get_patient()

    st.info(t("ax5_info"))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("ax5_predisposing"))
        predisposing = st.text_area(
            t("ax5_predisposing_placeholder"),
            value="\n".join(p.condition_model.predisposing),
            key="cm_predisposing"
        )
        p.condition_model.predisposing = [x for x in predisposing.split("\n") if x.strip()]

        st.subheader(t("ax5_precipitating"))
        precipitating = st.text_area(
            t("ax5_precipitating_placeholder"),
            value="\n".join(p.condition_model.precipitating),
            key="cm_precipitating"
        )
        p.condition_model.precipitating = [x for x in precipitating.split("\n") if x.strip()]

    with col2:
        st.subheader(t("ax5_perpetuating"))
        perpetuating = st.text_area(
            t("ax5_perpetuating_placeholder"),
            value="\n".join(p.condition_model.perpetuating),
            key="cm_perpetuating"
        )
        p.condition_model.perpetuating = [x for x in perpetuating.split("\n") if x.strip()]

        st.subheader(t("ax5_protective"))
        protective = st.text_area(
            t("ax5_protective_placeholder"),
            value="\n".join(p.condition_model.protective),
            key="cm_protective"
        )
        p.condition_model.protective = [x for x in protective.split("\n") if x.strip()]

    st.markdown("---")
    p.condition_model.narrative = st.text_area(
        t("ax5_narrative"),
        value=p.condition_model.narrative,
        height=200,
        placeholder=t("ax5_narrative_placeholder")
    )


# ===================================================================
# ACHSE VI: BELEGSAMMLUNG
# ===================================================================

elif menu == t("nav_axis6"):
    st.markdown(f"<div class='axis-header'>{t('header_axis6')}</div>",
                unsafe_allow_html=True)
    p = get_patient()

    with st.form("evidence_form"):
        col1, col2, col3 = st.columns([1, 2, 2])
        e_axis = col1.selectbox(t("ax6_axis_label"), ["I", "II", "III", "IV", "V"])
        e_type = col2.text_input(t("ax6_doc_type"))
        e_desc = col3.text_input(t("ax6_description"))
        e_source = st.text_input(t("ax6_source"))
        if st.form_submit_button(t("ax6_submit")):
            p.evidence_entries.append(asdict(EvidenceEntry(
                axis=e_axis,
                document_type=e_type,
                description=e_desc,
                date=str(datetime.date.today()),
                source=e_source
            )))
            st.rerun()

    if p.evidence_entries and HAS_PANDAS:
        df = pd.DataFrame(p.evidence_entries)
        st.table(df)
    elif p.evidence_entries:
        for e in p.evidence_entries:
            st.write(f"{t('ax6_axis_label')} {e['axis']}: {e['document_type']} - {e['description']}")

    st.markdown("---")

    # --- CAVE Warnhinweise (Eingabe) ---
    st.subheader(f"CAVE / {t('cave_title')}")
    with st.form("cave_form"):
        cave_text = st.text_area(t("cave_text"), key="cave_text_input")
        col1, col2 = st.columns(2)
        cave_cat = col1.selectbox(t("cave_category"), [
            t("cave_cat_interaction"),
            t("cave_cat_lab_artifact"),
            t("cave_cat_contraindication"),
            t("cave_cat_temporal"),
            t("cave_cat_diagnostic"),
            t("cave_cat_other")
        ], key="cave_cat_input")
        cave_axis = col2.selectbox(t("cave_axis_ref"),
                                   ["I", "II", "III", "IV", "V", "VI"],
                                   key="cave_axis_input")
        if st.form_submit_button(t("cave_add")):
            if cave_text.strip():
                p.cave_alerts.append(asdict(CaveAlert(
                    text=cave_text.strip(),
                    category=cave_cat,
                    axis_ref=cave_axis,
                    date_added=str(datetime.date.today())
                )))
                st.rerun()

    if p.cave_alerts:
        for alert in p.cave_alerts:
            st.markdown(
                f"<div class='status-alert critical'>"
                f"<b>[{alert.get('category','')}]</b> {alert.get('text','')} "
                f"({t('cave_axis_ref')}: {alert.get('axis_ref','')})</div>",
                unsafe_allow_html=True
            )
    else:
        st.info(t("cave_empty"))

    st.markdown("---")

    # --- Symptomverlauf (Eingabe) ---
    st.subheader(t("symptom_timeline_title"))
    with st.form("timeline_form"):
        col1, col2 = st.columns(2)
        tl_symptom = col1.text_input(t("symptom_timeline_name"), key="tl_name")
        tl_onset = col2.text_input(t("symptom_timeline_onset"), key="tl_onset")
        col3, col4 = st.columns(2)
        tl_status = col3.text_input(t("symptom_timeline_status"), key="tl_status")
        tl_therapy = col4.text_input(t("symptom_timeline_therapy_response"), key="tl_therapy")
        if st.form_submit_button(t("symptom_timeline_add")):
            if tl_symptom.strip():
                p.symptom_timeline.append(asdict(SymptomTimeline(
                    symptom=tl_symptom.strip(),
                    onset=tl_onset,
                    current_status=tl_status,
                    therapy_response=tl_therapy
                )))
                st.rerun()

    if p.symptom_timeline and HAS_PANDAS:
        df_tl = pd.DataFrame(p.symptom_timeline)
        st.table(df_tl)
    elif p.symptom_timeline:
        for tl in p.symptom_timeline:
            st.write(f"{tl.get('symptom','')}: {tl.get('onset','')} → {tl.get('current_status','')}")


# ===================================================================
# GESAMTSYNOPSE & EXPORT
# ===================================================================

elif menu == t("nav_synopsis"):
    st.markdown(f"<h1 style='text-align: center;'>{t('header_synopsis')}</h1>",
                unsafe_allow_html=True)
    p = get_patient()

    # --- Achse I ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis1_header')}</div>",
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{t('syn_acute_chronic')}**")
        for d in p.diagnoses_acute:
            st.error(f"🔴 {d['name']} ({d.get('code_icd11','')}/{d.get('code_dsm5','')})")
        for d in p.diagnoses_chronic:
            st.warning(f"🟡 {d['name']} ({d.get('code_icd11','')}/{d.get('code_dsm5','')})")
        st.write(f"**{t('syn_remitted')}**")
        for d in p.diagnoses_remitted:
            factors = ", ".join(d.get("remission_factors", []))
            st.success(f"✅ {d['name']} ({t('ax1_rem_factors_label')}: {factors})")
    with col2:
        st.write(f"**{t('syn_diagnostic_certainty')}**")
        for d in p.diagnoses_suspected:
            st.markdown(f"<div class='status-alert suspected'>? {t('ax1_suspected_prefix')}: {d['name']}</div>",
                        unsafe_allow_html=True)
        for d in p.diagnoses_excluded:
            st.markdown(f"<div class='status-alert excluded'>✖ {t('ax1_excluded_prefix')}: {d['name']}</div>",
                        unsafe_allow_html=True)

    # --- Achse II ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis2_header')}</div>",
                unsafe_allow_html=True)
    if HAS_PLOTLY:
        pid5 = p.pid5_profile
        categories = [t("syn_pid5_short_neg"), t("syn_pid5_short_det"),
                      t("syn_pid5_short_ant"), t("syn_pid5_short_dis"),
                      t("syn_pid5_short_psy"), t("syn_pid5_short_ana")]
        values = [pid5.negative_affectivity, pid5.detachment,
                  pid5.antagonism, pid5.disinhibition,
                  pid5.psychoticism, pid5.anankastia]
        values_closed = values + [values[0]]
        categories_closed = categories + [categories[0]]

        fig = go.Figure(data=go.Scatterpolar(
            r=values_closed, theta=categories_closed,
            fill='toself', line_color='#268bd2'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 3])),
            showlegend=False, height=350,
            title=t("syn_pid5_profile_title")
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- HiTOP-Spektren ---
    if p.crosscutting_level1:
        st.markdown("<div class='axis-header'>HiTOP-SPEKTREN</div>",
                    unsafe_allow_html=True)
        render_hitop_radar(p.hitop_profile)

    # --- Achse III ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis3_header')}</div>",
                unsafe_allow_html=True)
    # Alle medizinischen Diagnosen zusammenführen
    all_med_syn = (p.med_diagnoses_acute + p.med_diagnoses_chronic +
                   p.med_diagnoses_contributing + p.medical_conditions)
    if all_med_syn and HAS_PANDAS:
        df = pd.DataFrame(all_med_syn)
        cols = [c for c in ["name", "icd11_code", "causality", "status"] if c in df.columns]
        st.table(df[cols])

    col1, col2 = st.columns(2)
    with col1:
        if p.med_diagnoses_suspected:
            st.write(f"**{t('ax3_suspected_subheader')}**")
            for d in p.med_diagnoses_suspected:
                st.markdown(
                    f"<div class='status-alert suspected'>? {d['name']}</div>",
                    unsafe_allow_html=True)
    with col2:
        if p.medications:
            st.write(f"**{t('ax3_medication_subheader')}**")
            for m in p.medications:
                st.caption(f"💊 {m.get('name','')} {m.get('dose','')}")

    # --- Achse IV ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis4_header')}</div>",
                unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("GAF-Score", f"{p.functioning.gaf_score}/100")
    col2.metric("GdB", f"{p.functioning.gdb_score}")
    col3.metric(t("syn_stressors_prefix"), f"{len(p.functioning.psychosocial_stressors)}")
    if p.functioning.psychosocial_stressors:
        st.write(f"{t('syn_stressors_prefix')}: " + ", ".join(p.functioning.psychosocial_stressors))

    # --- Achse V ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis5_header')}</div>",
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{t('syn_predisposing')}**", ", ".join(p.condition_model.predisposing) or "—")
        st.write(f"**{t('syn_precipitating')}**", ", ".join(p.condition_model.precipitating) or "—")
    with col2:
        st.write(f"**{t('syn_perpetuating')}**", ", ".join(p.condition_model.perpetuating) or "—")
        st.write(f"**{t('syn_protective')}**", ", ".join(p.condition_model.protective) or "—")
    if p.condition_model.narrative:
        st.info(f"**{t('syn_narrative_label')}**\n\n{p.condition_model.narrative}")

    # --- Achse VI ---
    st.markdown(f"<div class='axis-header'>{t('syn_axis6_header')}</div>",
                unsafe_allow_html=True)
    if p.evidence_entries and HAS_PANDAS:
        st.table(pd.DataFrame(p.evidence_entries))

    # --- Abdeckungsanalyse ---
    # --- Strukturierte Abdeckungsanalyse ---
    st.markdown(f"<div class='axis-header'>{t('syn_coverage_header')}</div>",
                unsafe_allow_html=True)
    if p.symptom_coverage:
        if HAS_PANDAS:
            df_cov = pd.DataFrame(p.symptom_coverage)
            st.table(df_cov)
        total_pct = sum(c.get("coverage_pct", 0) for c in p.symptom_coverage) / len(p.symptom_coverage)
        st.metric(t("coverage_total"), f"~{total_pct:.0f}%")
    if p.coverage_analysis:
        st.markdown(
            f"<div class='coverage-gap'><b>{t('syn_unexplained')}</b><br/>"
            f"{p.coverage_analysis}</div>",
            unsafe_allow_html=True
        )
    elif not p.symptom_coverage:
        st.success(t("syn_no_unexplained"))

    # --- CAVE Warnhinweise ---
    if p.cave_alerts:
        st.markdown("<div class='axis-header' style='background-color:#dc322f;color:#fdf6e3;'>"
                    f"CAVE / {t('cave_title')}</div>",
                    unsafe_allow_html=True)
        for alert in p.cave_alerts:
            st.markdown(
                f"<div class='status-alert critical'>"
                f"<b>[{alert.get('category','')}]</b> {alert.get('text','')} "
                f"({t('cave_axis_ref')}: {alert.get('axis_ref','')})</div>",
                unsafe_allow_html=True
            )

    # --- Symptomverlauf ---
    if p.symptom_timeline:
        st.markdown(f"<div class='axis-header'>{t('symptom_timeline_title')}</div>",
                    unsafe_allow_html=True)
        if HAS_PANDAS:
            df_tl = pd.DataFrame(p.symptom_timeline)
            st.table(df_tl)

    # --- Export ---
    st.markdown("---")
    st.subheader(t("syn_export"))
    if st.button(t("syn_export_button")):
        export_data = {
            "export_date": str(datetime.datetime.now()),
            "system_version": t("syn_system_version"),
            "language": st.session_state.lang,
            "axes": {
                "I_psychische_profile": {
                    "acute": p.diagnoses_acute,
                    "chronic": p.diagnoses_chronic,
                    "remitted": p.diagnoses_remitted,
                    "suspected": p.diagnoses_suspected,
                    "excluded": p.diagnoses_excluded,
                    "compliance": {
                        "med_self": p.compliance_med_self,
                        "med_ext": p.compliance_med_ext,
                        "therapy": p.compliance_therapy
                    },
                    "investigation_plan": p.investigation_plan,
                    "coverage_analysis": p.coverage_analysis
                },
                "II_biographie": {
                    "education": p.education,
                    "iq": p.iq_estimate,
                    "developmental_history": p.developmental_history,
                    "pid5_profile": asdict(p.pid5_profile)
                },
                "III_medizinisch": {
                    "IIIa_acute": p.med_diagnoses_acute,
                    "IIIb_chronic": p.med_diagnoses_chronic,
                    "IIIc_contributing": p.med_diagnoses_contributing,
                    "IIId_remitted": p.med_diagnoses_remitted,
                    "IIIf_treatment_current": p.med_treatment_current,
                    "IIIf_treatment_past": p.med_treatment_past,
                    "IIIg_compliance": {
                        "self": p.med_compliance_self,
                        "external": p.med_compliance_ext
                    },
                    "IIIh_suspected": p.med_diagnoses_suspected,
                    "IIIi_coverage": p.med_coverage_analysis,
                    "IIIj_plan": p.med_investigation_plan,
                    "IIIk_conditions_legacy": p.medical_conditions,
                    "IIIl_genetic_factors": p.genetic_factors,
                    "IIIl_family_history": p.family_history,
                    "IIIm_medications": p.medications
                },
                "IV_umwelt_funktion": {
                    "gaf": p.functioning.gaf_score,
                    "gdb": p.functioning.gdb_score,
                    "stressors": p.functioning.psychosocial_stressors
                },
                "V_bedingungsmodell": asdict(p.condition_model),
                "VI_belegsammlung": p.evidence_entries
            },
            "screening": {
                "crosscutting_level1": p.crosscutting_level1,
                "triggered_domains": p.crosscutting_triggered,
                "hitop_profile": asdict(p.hitop_profile)
            },
            "gatekeeper": p.gate_results,
            "cave_alerts": p.cave_alerts,
            "symptom_coverage": p.symptom_coverage,
            "investigation_plans": p.investigation_plans,
            "symptom_timeline": p.symptom_timeline
        }
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False,
                              default=str)
        st.download_button(
            label=t("syn_download"),
            data=json_str,
            file_name=f"diagnostic_export_{datetime.date.today()}.json",
            mime="application/json"
        )
        st.json(export_data)


# ===================================================================
# FOOTER
# ===================================================================

st.sidebar.markdown("---")
st.sidebar.caption(
    f"{t('footer_line1')}\n\n"
    f"{t('footer_line2')}\n\n"
    f"{t('footer_line3')}\n\n"
    f"{t('footer_date_prefix')}: {datetime.date.today()}"
)
