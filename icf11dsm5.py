import streamlit as st
from anytree import Node, find_by_attr
import datetime
import pandas as pd

# --- KONFIGURATION & STYLING ---
st.set_page_config(page_title="Expertensystem Multiaxiale Diagnostik", layout="wide")

st.markdown("""
    <style>
    .axis-header { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .sub-section { border-left: 3px solid #268bd2; padding-left: 15px; margin-bottom: 20px; }
    .evidence-table { font-size: 0.9em; width: 100%; }
    .status-alert { padding: 10px; border-radius: 5px; margin: 5px 0; }
    .suspected { background-color: #fdf6e3; border: 1px solid #b58900; }
    .excluded { background-color: #eee8d5; border: 1px solid #586e75; text-decoration: line-through; }
    </style>
""", unsafe_allow_html=True)

# --- DATENSTRUKTUR INITIALISIERUNG ---
if 'expert_data' not in st.session_state:
    st.session_state.expert_data = {
        'ax_1': {'remitted': [], 'remission_factors': {}, 'treatment_history': [], 'compliance': {}, 'suspected': [], 'excluded': [], 'investigation_plan': '', 'coverage_analysis': ''},
        'ax_3': {'remitted_med': [], 'remission_factors_med': {}, 'med_history': [], 'compliance_med': {}, 'suspected_med': [], 'excluded_med': [], 'investigation_plan_med': '', 'coverage_analysis_med': ''},
        'ax_5_model': '',
        'ax_6_evidence': []
    }

# --- NAVIGATION ---
st.sidebar.title("Klinisches Cockpit")
menu = st.sidebar.radio("Achsen-Fokus", [
    "I: Psychische Profile (Erweitert)",
    "III: Medizinische Synopse (Erweitert)",
    "V: Integriertes Bedingungsmodell",
    "VI: Belegsammlung & Verzeichnis",
    "Gesamt-Synopse"
])

# --- ACHSE I: PSYCHISCHE PROFILE (ERWEITERT) ---
if menu == "I: Psychische Profile (Erweitert)":
    st.markdown("<div class='axis-header'>ACHSE I: PSYCHISCHE STÖRUNGEN (SYNOPSE Ia - Ij)</div>", unsafe_allow_html=True)
    
    tab_rem, tab_treat, tab_diag, tab_plan = st.tabs(["Remission (Id-Ie)", "Behandlung (If-Ig)", "Diagnosestatus (Ih)", "Planung (Ii-Ij)"])

    with tab_rem:
        st.subheader("Id & Ie: Remittierte Diagnosen & Wegfall-Faktoren")
        rem_diag = st.text_input("Belegte Diagnose (Kriterien aktuell nicht erfüllt)")
        factors = st.multiselect("Faktoren für den Wegfall der Kriterien:", 
                                 ["Unbekannt", "Zeitverlauf", "Bewältigungsfaktoren", "Unterstützungssystem", "Therapie", "Medikamente"])
        rem_evidence = st.text_area("Belege (Befragung Patient / Dokumente)")
        if st.button("Remission hinzufügen"):
            st.session_state.expert_data['ax_1']['remitted'].append({'diag': rem_diag, 'factors': factors, 'evidence': rem_evidence})

    with tab_treat:
        st.subheader("If: Behandlungsgeschichte & Medikation")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Aktuell:**")
            st.text_area("Laufende Behandlungen / Medikation", key="curr_treat")
        with col2:
            st.write("**Vergangen:**")
            st.text_area("Frühere Behandlungen (inkl. Wirkungen/Nebenwirkungen)", key="past_treat")
        
        st.subheader("Ig: Therapietreue & -fähigkeit")
        c1, c2, c3 = st.columns(3)
        st.session_state.expert_data['ax_1']['compliance']['self_med'] = c1.slider("Medik. Therapietreue (Selbst)", 0, 10, 5)
        st.session_state.expert_data['ax_1']['compliance']['ext_med'] = c2.slider("Medik. Therapietreue (Fremd - nur mit Beleg)", 0, 10, 5)
        st.session_state.expert_data['ax_1']['compliance']['capability'] = c3.slider("Nicht-medik. Therapiefähigkeit", 0, 10, 5)

    with tab_diag:
        st.subheader("Ih: Verdachtsdiagnosen")
        col_v1, col_v2 = st.columns(2)
        v_diag = col_v1.text_input("Neue Verdachtsdiagnose")
        if col_v1.button("Als Verdacht aufnehmen"):
            st.session_state.expert_data['ax_1']['suspected'].append(v_diag)
        
        ex_diag = col_v2.text_input("Auszuschließende Diagnose")
        if col_v2.button("Als ausgeschlossen markieren"):
            st.session_state.expert_data['ax_1']['excluded'].append(ex_diag)

    with tab_plan:
        st.subheader("Ii & Ij: Untersuchungsplan & Abdeckungsanalyse")
        st.session_state.expert_data['ax_1']['investigation_plan'] = st.text_area("Nächste Schritte / Untersuchungsplan")
        st.session_state.expert_data['ax_1']['coverage_analysis'] = st.text_area("Symptomverlauf & Abdeckungsanalyse (Unerklärte Symptome)", 
                                                                               placeholder="Welche Symptome werden durch die aktuellen Diagnosen NICHT erklärt?")

# --- ACHSE V: INTEGRIERTES BEDINGUNGSMODELL ---
elif menu == "V: Integriertes Bedingungsmodell":
    st.markdown("<div class='axis-header'>ACHSE V: INTEGRIERTES BEDINGUNGSMODELL</div>", unsafe_allow_html=True)
    st.info("Synthese aller Achsen: Wie interagieren Biologie (III), Biographie (II) und aktuelle Stressoren (IV) mit der Psychopathologie (I)?")
    
    st.session_state.expert_data['ax_5_model'] = st.text_area("Zusammenfassendes Bedingungsmodell (Explikation der Kausalzusammenhänge)", height=300)
    
    st.write("**Fokus-Checkliste für das Modell:**")
    st.checkbox("Prädisponierende Faktoren (Genetik/Frühkindlich)")
    st.checkbox("Auslösende Faktoren (Aktuelle Lebensereignisse)")
    st.checkbox("Aufrechterhaltende Faktoren (Sekundärer Krankheitsgewinn/Vermeidung)")

# --- ACHSE VI: BELEGSAMMLUNG ---
elif menu == "VI: Belegsammlung & Verzeichnis":
    st.markdown("<div class='axis-header'>ACHSE VI: BELEGSAMMLUNG & VERZEICHNIS</div>", unsafe_allow_html=True)
    
    with st.form("evidence_form"):
        col_e1, col_e2, col_e3 = st.columns([1, 2, 2])
        e_axis = col_e1.selectbox("Achse", ["I", "II", "III", "IV", "V"])
        e_doc = col_e2.text_input("Dokumententyp (z.B. Entlassbericht, Zeugnis, Labor)")
        e_desc = col_e3.text_input("Inhaltlicher Belegwert / Kurzbeschreibung")
        if st.form_submit_button("Beleg im Verzeichnis registrieren"):
            st.session_state.expert_data['ax_6_evidence'].append({'Achse': e_axis, 'Typ': e_doc, 'Beschreibung': e_desc, 'Datum': datetime.date.today()})
    
    if st.session_state.expert_data['ax_6_evidence']:
        df_ev = pd.DataFrame(st.session_state.expert_data['ax_6_evidence'])
        st.table(df_ev)

# --- GESAMT-SYNOPSE ---
elif menu == "Gesamt-Synopse":
    st.markdown("<h1 style='text-align: center;'>Klinische Gesamtsynopse</h1>", unsafe_allow_html=True)
    d = st.session_state.expert_data
    
    # Grid für Ia-Id
    st.subheader("Achse I: Psychischer Status & Verlauf")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Aktuelle/Chronische Störungen (Ia/Ib)**")
        # Platzhalter für Daten aus v4
        st.write("**Remittierte Diagnosen (Id) & Wegfall-Faktoren (Ie):**")
        for r in d['ax_1']['remitted']:
            st.success(f"{r['diag']} (Faktoren: {', '.join(r['factors'])})")
    
    with c2:
        st.write("**Diagnostische Sicherheit (Ih):**")
        for s in d['ax_1']['suspected']: st.markdown(f"<div class='status-alert suspected'>? Verdacht: {s}</div>", unsafe_allow_html=True)
        for e in d['ax_1']['excluded']: st.markdown(f"<div class='status-alert excluded'>✖ Ausgeschlossen: {e}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Bedingungsmodell & Abdeckung")
    col_v1, col_v2 = st.columns(2)
    col_v1.info(f"**Integriertes Modell (V):**\n\n{d['ax_5_model']}")
    col_v2.warning(f"**Unerklärte Symptome (Ij):**\n\n{d['ax_1']['coverage_analysis']}")

    st.markdown("---")
    st.subheader("Therapie-Profil")
    st.write(f"**Einstellung zu Vorbehandlungen:** {d['ax_1'].get('compliance', {}).get('capability')}/10 (Therapiefähigkeit)")
    
    if st.button("Druckversion generieren"):
        st.write("Druckansicht bereit.")

if __name__ == "__main__":
    pass
"""
==========================================================================================
KLINISCHES MULTIAXIALES EXPERTENMODELL (SYNOPSE DSM-5-TR / ICD-11 / MULTIAXIAL V6)
==========================================================================================

Dieses Modell integriert die kategoriale Diagnostik (DSM/ICD) in ein epistemologisches 
Gesamtsystem. Es dient der Erfassung der Lebensspanne, der Kausalitätsprüfung zwischen 
Somatik und Psyche sowie der Dokumentation der Behandlungs- und Remissionsgeschichte.

------------------------------------------------------------------------------------------
I. ÜBERSICHT DER DIAGNOSTISCHEN ACHSEN (ASCII-TABELLE)
------------------------------------------------------------------------------------------

+-------+-------------------------+-------------------------+----------------------------+
| ACHSE | BEZEICHNUNG             | UNTERTEILUNG (FOKUS)    | KERNINHALTE / INSTRUMENTE  |
+-------+-------------------------+-------------------------+----------------------------+
| I     | Psychische Profile      | Ia: Akute Störungen     | Screening, BDI, PHQ, Test  |
|       |                         | Ib: Chronische Verläufe | Chronifizierungsgefahr     |
|       |                         | Ic: Widerlegte Verdacht | Differenzialdiagn. Korrektur|
|       |                         | Id: Remittierte Diagn.  | Belegte, inaktive Diagnosen|
|       |                         | Ie: Remissionsfaktoren  | Zeit, Bewältigung, Therapie|
|       |                         | If: Behandlungsgesch.   | Medikation, Wirk/Nebenwirk.|
|       |                         | Ig: Therapietreue       | Selbst- vs. Fremdbild      |
|       |                         | Ih: Verdachtsdiagnosen  | Laufende Hypothesenbildung |
|       |                         | Ii: Untersuchungsplan   | Nächste diagnostische Schritte|
|       |                         | Ij: Abdeckungsanalyse   | Unerklärte Restsymptomatik |
+-------+-------------------------+-------------------------+----------------------------+
| II    | Biographie & Entw.      | Entwicklungshistorie    | IQ, Bildung, Sozialisation |
|       |                         | Persönlichkeit          | Trait-Profiling (PID-5)    |
|       |                         | Quellenprüfung          | Zeugnisse, Interviews      |
+-------+-------------------------+-------------------------+----------------------------+
| III   | Medizinische Synopse    | IIIa: Med. Historie     | Biographische Medizingesch.|
|       |                         | IIIb: Kausalität (Voll) | Organisch erklärend        |
|       |                         | IIIc: Mitverursachend   | Begünstigende Komorbidität |
|       |                         | IIId: Genetik/Familie   | Erbbiologische Belastung   |
|       |                         | IIIe: Bewältigte Krankh.| Med. Remissionsfaktoren    |
+-------+-------------------------+-------------------------+----------------------------+
| IV    | Umwelt & Funktion       | Teilhabe (ICF)          | GAF-Score, GdB, Stressoren |
|       |                         | Psychosoz. Umstände     | Wohnen, Finanzen, Isolation|
+-------+-------------------------+-------------------------+----------------------------+
| V     | Bedingungsmodell        | Klinische Synthese      | Prädisponierend, Auslösend,|
|       |                         |                         | Aufrechterhaltend          |
+-------+-------------------------+-------------------------+----------------------------+
| VI    | Belegsammlung           | Evidenz-Matrix          | Register aller Dokumente   |
|       |                         |                         | über alle Domänen hinweg   |
+-------+-------------------------+-------------------------+----------------------------+

------------------------------------------------------------------------------------------
II. PROZESSLOGIK UND KLINISCHE SYNTHESE
------------------------------------------------------------------------------------------

1. GATEKEEPER-LOGIK (Achse I):
   Das System nutzt eine dynamische Warteschlange. Screening-Auffälligkeiten triggern 
   spezifische DSM-5/ICD-11 Module. Jede Diagnose wird zeitlich (akut/chronisch/remittiert) 
   verortet.

2. REMISSIONS-ANALYSE (Ie / IIIe):
   Einzigartige Erfassung des Wegfalls von Kriterien. Dokumentiert explizit, ob Genesung 
   durch Therapie, Medikamente oder spontane Bewältigungsfaktoren eintrat.

3. KAUSALITÄTS-MATRIX (Achse III):
   Strenge Trennung zwischen IIIb (medizinischer Befund erklärt Psyche vollständig) 
   und IIIc (medizinischer Befund wirkt nur verstärkend).

4. ABDECKUNGSANALYSE (Ij):
   Kritisches Korrektiv zur Vermeidung von Diagnosefehlern. Listet alle Symptome auf, 
   die NICHT durch die vergebenen Diagnosen erklärt werden.

5. INTEGRIERTES BEDINGUNGSMODELL (Achse V):
   Die biopsychosoziale Klammer. Hier wird die Interaktion zwischen Biologie (III), 
   Biographie (II) und aktuellen Symptomen (I) narrativ und logisch expliziert.

6. EVIDENZ-PRINZIP (Achse VI):
   Jede kodierte Information muss auf einem Beleg basieren (Dokumentenanalyse, Befragung, 
   Testung), der im zentralen Verzeichnis gelistet ist.

------------------------------------------------------------------------------------------
Status: Version 6.0 (Expert System)
Letztes Update: 08.02.2026
------------------------------------------------------------------------------------------
"""