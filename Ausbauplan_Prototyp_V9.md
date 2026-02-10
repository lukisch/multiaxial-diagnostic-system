# Ausbauplan: Multiaxiales Diagnostik-Expertensystem V8 -> V9

**Stand:** 2026-02-10
**Basis:** Review_Multiaxiale_Diagnostik.tex (V3) vs. multiaxial_diagnostic_system.py (V8)
**Quelle 2:** Klinische Dokumente aus _Arztsachen (Fallbezogene Auswertung, Synopse, Literaturrecherche)

---

## Phase 1: Paper-Alignment (Prioritaet KRITISCH) -- ERLEDIGT

### 1.1 Ii/Ij Reihenfolge korrigieren -- DONE
- **Was:** Abdeckungsanalyse wird Ii, Untersuchungsplan wird Ij
- **Wo:** translations.json (DE + EN), multiaxial_diagnostic_system.py (tab_plan Reihenfolge)

### 1.2 HiTOP-Spektren-Radar aus Cross-Cutting-Daten -- DONE
- **Was:** 6 HiTOP-Spektren automatisch aus Cross-Cutting-Ergebnissen berechnen
- **Mapping:**
  - Internalizing = max(Depression, Anxiety, Somatic, Sleep)
  - Thought Disorder = max(Psychosis, Dissociation)
  - Disinhibited Externalizing = max(Substance, Mania)
  - Antagonistic Externalizing = max(Anger)
  - Detachment = max(Detachment/Memory)
  - Somatoform = max(Somatic)

### 1.3 Achse III: Symmetrische Erweiterung (13 Subachsen) -- DONE
- **Was:** Achse III von 3 Tabs auf 13 Subachsen (IIIa-IIIm) erweitern

---

## Phase 1b: Klinische-Dokumente-Integration (Prioritaet KRITISCH) -- ERLEDIGT

### 1b.1 PRO/CONTRA Evidenzbewertung pro Diagnose -- DONE
- **Was:** Jede Diagnose bekommt Konfidenz-Slider (0-100%), Schweregrad-Auswahl, PRO/CONTRA Freitext
- **Wo:** Gate 5 Diagnose-Formular erweitert, Diagnosis-Dataclass mit confidence_pct, severity, evidence_pro, evidence_contra
- **Quelle:** FALLBEZOGENE_AUSWERTUNG Dokument

### 1b.2 Quantitative Symptomabdeckung (~88% Metrik) -- DONE
- **Was:** Strukturierte Symptom-Diagnosen-Matrix mit Abdeckungsprozent pro Symptom
- **Wo:** Achse I Tab Ii (Abdeckungsanalyse) mit Formular + Metriken (Vollstaendig/Partiell/Unzureichend)
- **Quelle:** SYNOPSE_VALIDIERT Dokument

### 1b.3 Priorisierter Untersuchungsplan (Dringend/Wichtig/Verlauf) -- DONE
- **Was:** Strukturierte Untersuchungsplanung mit 3-stufiger Priorisierung und Fachgebiet
- **Wo:** Achse I Tab Ij (Untersuchungsplan) mit Formular + tabellarischer Anzeige
- **Quelle:** FALLBEZOGENE_AUSWERTUNG + SYNOPSE_VALIDIERT

### 1b.4 CAVE Klinische Warnhinweise -- DONE
- **Was:** Kritische Warnungen (Labor-Artefakte, Medikamenten-Interaktionen, Kontraindikationen, etc.)
- **Wo:** Achse VI Belegsammlung (Eingabe) + Synopse (rote Anzeige)
- **Kategorien:** Medikamenten-Interaktion, Labor-Artefakt, Kontraindikation, Zeitliche Fehlzuordnung, Diagnostische Einschraenkung, Sonstiges

### 1b.5 Longitudinaler Symptomverlauf -- DONE
- **Was:** Tracking von Symptomen ueber Zeit (Beginn, aktueller Status, Therapie-Ansprechen)
- **Wo:** Achse VI Belegsammlung (Eingabe) + Synopse (Tabelle)

### 1b.6 IIIm Medikamentenformular erweitert -- DONE
- **Was:** Zusaetzliche Felder: Einheit, Zweck/Indikation, Einnahmezeitpunkt, Wirkungsrating (0-10)
- **Wo:** Achse III Tab IIIm
- **Quelle:** Medikamente Uebersicht PDF

### 1b.7 JSON-Export aktualisiert -- DONE
- **Was:** cave_alerts, symptom_coverage, investigation_plans, symptom_timeline im Export

---

## Phase 2: Strukturerweiterung (Prioritaet HOCH)

### 2.1 Achse V: P1-P4 Strukturierte Kodierung
- **Was:** Freitext-Felder durch strukturierte Eingabe mit Quellenachse-Referenz ersetzen
- **Schema:** Jeder Faktor bekommt: Text + Quellenachse (I-IV) + Evidenzstufe
- **Aufwand:** Mittel

### 2.2 Fehlende Screening-Instrumente
- **Was:** SCOFF (Essstoerungen), EDE-QS, ISI (Insomnie), SSIS hinzufuegen
- **Wo:** Cross-Cutting Screening erweitern oder als Level-2-Module
- **Aufwand:** Mittel

### 2.3 Cultural Formulation Interview (CFI)
- **Was:** Strukturiertes CFI-Modul in Achse IV integrieren
- **Felder:** Kulturelle Identitaet, Kulturelle Konzeptualisierung, Psychosoziale Stressoren, Kulturelle Merkmale der Beziehung Kliniker-Patient
- **Aufwand:** Mittel

### 2.4 Klinische Signifikanz / Schweregrad-Skala
- **Was:** Standardisierte CGI-S artige Schweregrad-Einschätzung pro Diagnose (bereits teils in 1b.1)
- **Erweiterung:** CGI-I (Improvement) + CGI-E (Efficacy) als Verlaufsparameter
- **Aufwand:** Klein

### 2.5 Pathophysiologisches Kausalmodell
- **Was:** 3-Achsen-Modell (Genetisch-Neurobiologisch / Psychisch-Entwicklungsbezogen / Umwelt-Situativ)
- **Wo:** Achse V erweitern oder neuer Tab
- **Quelle:** SYNOPSE_VALIDIERT (Pathophysiologische Zusammenhaenge)
- **Aufwand:** Mittel

### 2.6 Therapieresistenz-Tracking
- **Was:** Dokumentation von Behandlungsversuchen, Ansprechraten, Therapiewechseln
- **Wo:** Achse I (Behandlungshistorie) oder Achse III (IIIf)
- **Quelle:** Medikamente Uebersicht + SYNOPSE_VALIDIERT
- **Aufwand:** Mittel

---

## Phase 3: Fortgeschrittene Features (Prioritaet MITTEL)

### 3.1 Multi-Professionelles Rollenmodell
- **Was:** Login/Rollenwahl (Psychologe, Arzt, Sozialarbeiter, Team) mit achsenspezifischen Zugriffsrechten
- **Mapping:** Psychologe -> Achse I+II, Arzt -> Achse III, Sozialarbeiter -> Achse IV, Team -> Achse V, Alle -> Achse VI
- **Aufwand:** Gross

### 3.2 Automatisierte Abdeckungsanalyse
- **Was:** Symptom-Diagnosen-Matrix die automatisch unerklarte Symptome identifiziert
- **Logik:** Cross-Cutting-Items die getriggert wurden, aber keiner Diagnose zugeordnet sind
- **Aufwand:** Gross

### 3.3 Komorbiditaetsregeln
- **Was:** Automatische Warnungen bei klinisch unueblichen Kombinationen
- **Beispiele:** Bipolar + Unipolare Depression, PTBS ohne Trauma-Kriterium A
- **Aufwand:** Mittel

### 3.4 HSM-Stoerungsmodule (11 Module)
- **Was:** Strukturierte kriterienbasierte Module fuer: Mood, Anxiety, Trauma, Psychotic, Personality, OCDSpectrum, Dissociative, Eating, Neurodevelopmental, SubstanceUse, Somatic
- **Aufwand:** Sehr Gross (pro Modul ca. 100-200 Zeilen)

---

## Phase 4: Zukunft (Prioritaet NIEDRIG)

### 4.1 Kinder/Jugend Cross-Cutting Variante
### 4.2 FHIR-Interoperabilitaet
### 4.3 PDF-Report-Generierung (WeasyPrint + Jinja2)
### 4.4 SQLite-Persistenz
### 4.5 RDoC-Annotationsschicht

---

## Implementierungsreihenfolge

### Sprint 1 -- ERLEDIGT (V9)
1. Ii/Ij Swap (translations.json + Code) -- DONE
2. HiTOP-Radar aus Cross-Cutting-Daten -- DONE
3. Achse III symmetrische Erweiterung (13 Subachsen) -- DONE
4. Version-Bump auf V9 -- DONE
5. PRO/CONTRA Evidenzbewertung + Konfidenz -- DONE
6. Strukturierte Symptomabdeckung mit Metriken -- DONE
7. Priorisierter Untersuchungsplan -- DONE
8. CAVE Warnhinweise (Eingabe + Synopse) -- DONE
9. Symptomverlauf (Eingabe + Synopse) -- DONE
10. IIIm Medikamentenformular erweitert -- DONE
11. JSON-Export mit allen neuen Feldern -- DONE

### Sprint 2 -- NAECHSTER SPRINT
1. Achse V P1-P4 Strukturierung
2. Pathophysiologisches Kausalmodell
3. Therapieresistenz-Tracking
4. CGI-I / CGI-E Verlaufsparameter
