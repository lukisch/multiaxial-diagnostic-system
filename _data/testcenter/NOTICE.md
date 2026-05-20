# Licensing Notice for Diagnostic Instruments

The test definitions in `tests/` contain item content from validated psychiatric
screening instruments. Each instrument is published under its own license by
its original authors. This repository reproduces item content for clinical and
research use in accordance with each instrument's terms.

**The MIT license of this repository applies to the software code only
(scoring engine, web application, templates). It does NOT apply to the
instrument content itself.**

## Instrument Licenses

| Instrument | License | Copyright Holder | Terms |
|-----------|---------|-----------------|-------|
| **PHQ-9** | Public Domain | Pfizer Inc. (funded development, no copyright claimed) | Free to use, reproduce, and distribute without permission |
| **GAD-7** | Public Domain | Pfizer Inc. (funded development, no copyright claimed) | Free to use, reproduce, and distribute without permission |
| **PCL-5** | Public Domain | U.S. Department of Veterans Affairs, National Center for PTSD | U.S. Government work, no copyright |
| **ITQ** | Public Domain / free to all interested parties | Cloitre, Shevlin, Brewin et al. | Public-domain wording documented by the instrument authors; official source at traumameasuresglobal.com |
| **AUDIT** | Public Domain | World Health Organization | WHO encourages use and reproduction |
| **C-SSRS** | Free for clinical/research use | The Columbia Lighthouse Project | Free with attribution; training recommended |
| **PQ-16** | Free for clinical/research use | Ising, Loewy et al. | Published in peer-reviewed literature |
| **ASRS v1.1 Screener** | Public Domain | World Health Organization / Harvard Medical School | WHO instrument, freely available |
| **AQ-10** | Free for clinical/research use | Allison, Auyeung, Baron-Cohen | Autism Research Centre, University of Cambridge |
| **OCI-R** | Free for clinical/research use | Foa, Huppert, Leiberg et al. | Published in Psychological Assessment (APA) |
| **SSS-8** | Free for clinical/research use | Gierk, Kohlmann, Kroenke et al. | Published in JAMA Internal Medicine |
| **DES-II** | Public Domain | Carlson & Putnam | No copyright restrictions |
| **SCOFF** | Public Domain | Morgan, Reid, Lacey | Published in BMJ, freely available |
| **ISI** | Free for clinical/research use | Morin | Published academic instrument |
| **PID-5-BF** | Free for clinical/research use | American Psychiatric Association | APA Online Assessment Measures, freely downloadable |
| **WHODAS 2.0** | Public Domain | World Health Organization | WHO encourages use and adaptation |
| **PHQ-A** | Public Domain | Pfizer / Johnson, Harris, Spitzer, Williams | Adolescent PHQ adaptation published for clinical and research use |
| **RCADS-25** | Limited non-commercial clinical/research/educational use | UCLA Child FIRST / Chorpita lab | Free within UCLA's stated non-commercial terms; no item modification |
| **SCARED-C** | Free for clinical and research use | Boris Birmaher et al. | Reproduction allowed with unchanged wording |
| **SDQ Self/Parent** | Free for non-commercial use | Robert Goodman / SDQ Info | Non-commercial clinical, research, and educational use permitted |
| **DSM-5 XC Parent** | Reproducible by clinicians and researchers | American Psychiatric Association | APA explicitly allows reproduction for researcher/clinician use with patients |
| **SNAP-IV-26** | Public Domain | James Swanson / University of California Irvine | Freely available for clinical, educational, and research use |
| **CRAFFT 2.1+N** | Free for clinical, educational, and non-commercial research use | CeASAR / Boston Children's Hospital | Non-commercial use permitted; retain attribution |
| **CRIES-8** | Free of cost to clinicians and researchers | Children and War Foundation | Distributed free of charge via childrenandwar.org |
| **DAST-10** | Free for clinical and research use | CAMH / Addiction Research Foundation | Modification not permitted |
| **MDQ** | Free for research and educational use | Hirschfeld et al. | Non-commercial use only |

## German Translations

Where available, the German item translations are based on officially validated
German versions as cited in each test definition's `references` field (for
example Löwe et al. for PHQ-9/GAD-7, Krüger-Gottschalk et al. for PCL-5,
Gönner et al. for OCI-R, and Spitzer et al. for DES-II/FDS).

Some of the newer child/adolescent and expansion instruments carry an explicit
`_translation_note` in their JSON definition. In those cases the German wording
is a documented working translation or a mixed-source wording that must be
checked against the official validated German instrument before clinical use.

## Important Notes

- **Clinical use only.** These instruments are screening tools, not diagnostic
  instruments. Results must be interpreted by qualified mental health professionals.
- **No modification of items.** The item content reproduces the original published
  versions. Modified versions may invalidate psychometric properties.
- **Attribution.** When using results from these instruments, cite the original
  validation studies listed in each test definition's `references` field.

## Sources

Each test definition JSON file contains a `source_url` field pointing to the
official distribution source and a `references` field with the primary
validation publications.
