"""Scoring engine for diagnostic instruments."""
from typing import Any


def score_test(test_def: dict, responses: dict[str, int]) -> dict[str, Any]:
    """Score a completed test based on its definition and user responses.

    Args:
        test_def: The test definition JSON (loaded from tests/*.json)
        responses: Dict mapping item number (str) to selected value (int)

    Returns:
        Dict with total_score, severity, label, color, subscales, alerts
    """
    scoring = test_def.get("scoring", {})
    method = scoring.get("method", "sum")
    items = test_def.get("items", [])
    result = {
        "test_id": test_def["id"],
        "test_name": test_def["name"],
        "method": method,
        "total_score": 0,
        "max_score": 0,
        "severity": "unknown",
        "label": {"de": "Nicht berechenbar", "en": "Cannot compute"},
        "color": "#9E9E9E",
        "subscales": [],
        "alerts": [],
        "action": None,
        "details": {}
    }

    if method == "sum":
        result = _score_sum(test_def, scoring, items, responses, result)
    elif method == "mean":
        result = _score_mean(test_def, scoring, items, responses, result)
    elif method == "threshold_count":
        result = _score_threshold_count(test_def, scoring, items, responses, result)
    elif method == "directional_sum":
        result = _score_directional_sum(test_def, scoring, items, responses, result)
    elif method == "algorithm":
        result = _score_algorithm(test_def, scoring, items, responses, result)
    elif method == "classification":
        result = _score_classification(test_def, scoring, items, responses, result)
    elif method == "endorsement_count_plus_distress":
        result = _score_endorsement(test_def, scoring, items, responses, result)
    elif method == "domain_mean":
        result = _score_domain_mean(test_def, scoring, items, responses, result)
    elif method == "simple_sum_and_complex":
        result = _score_simple_sum(test_def, scoring, items, responses, result)

    # Check critical items
    _check_critical_items(test_def, responses, result)

    return result


def _score_sum(test_def, scoring, items, responses, result):
    """Simple sum scoring (PHQ-9, GAD-7, PCL-5, OCI-R, SSS-8, ISI, SCOFF)."""
    total = 0
    for item in items:
        key = str(item["number"])
        if key in responses:
            total += int(responses[key])

    score_range = scoring.get("range", [0, 100])
    result["total_score"] = total
    result["max_score"] = score_range[1]

    # Find severity threshold
    for thresh in scoring.get("thresholds", []):
        if thresh["min"] <= total <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    # Score subscales
    for sub in scoring.get("subscales", []):
        sub_total = sum(int(responses.get(str(i), 0)) for i in sub["items"])
        sub_range = sub.get("range", [0, 0])
        result["subscales"].append({
            "name": sub["name"],
            "score": sub_total,
            "max_score": sub_range[1] if sub_range else 0
        })

    # Action guide
    action_guide = scoring.get("action_guide", {})
    if action_guide:
        for lang in ["de", "en"]:
            if lang in action_guide:
                for ag in action_guide[lang]:
                    parts = ag["range"].split("-")
                    low, high = int(parts[0]), int(parts[1])
                    if low <= total <= high:
                        if "action" not in result or result["action"] is None:
                            result["action"] = {}
                        result["action"][lang] = ag["action"]

    return result


def _score_mean(test_def, scoring, items, responses, result):
    """Mean scoring (DES-II)."""
    values = []
    for item in items:
        key = str(item["number"])
        if key in responses:
            values.append(int(responses[key]))

    if values:
        mean_val = sum(values) / len(values)
    else:
        mean_val = 0

    result["total_score"] = round(mean_val, 1)
    result["max_score"] = scoring.get("range", [0, 100])[1]

    for thresh in scoring.get("thresholds", []):
        if thresh["min"] <= mean_val <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    # Subscales
    for sub in scoring.get("subscales", []):
        sub_values = [int(responses.get(str(i), 0)) for i in sub["items"]]
        sub_mean = sum(sub_values) / len(sub_values) if sub_values else 0
        result["subscales"].append({
            "name": sub["name"],
            "score": round(sub_mean, 1),
            "max_score": 100
        })

    return result


def _score_threshold_count(test_def, scoring, items, responses, result):
    """Count items exceeding their individual thresholds (ASRS)."""
    count = 0
    for item in items:
        key = str(item["number"])
        threshold = item.get("scoring_threshold", 2)
        if key in responses and int(responses[key]) >= threshold:
            count += 1

    result["total_score"] = count
    result["max_score"] = len(items)

    for thresh in scoring.get("thresholds", []):
        if thresh["min"] <= count <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    return result


def _score_directional_sum(test_def, scoring, items, responses, result):
    """Directional scoring (AQ-10): score based on agree/disagree direction."""
    total = 0
    for item in items:
        key = str(item["number"])
        direction = item.get("scoring_direction", "agree")
        if key in responses:
            val = int(responses[key])
            if direction == "agree" and val <= 1:  # 0=definitely agree, 1=slightly agree
                total += 1
            elif direction == "disagree" and val >= 2:  # 2=slightly disagree, 3=definitely disagree
                total += 1

    result["total_score"] = total
    result["max_score"] = len(items)

    for thresh in scoring.get("thresholds", []):
        if thresh["min"] <= total <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    return result


def _score_algorithm(test_def, scoring, items, responses, result):
    """Algorithm-based scoring (ITQ) with diagnostic criteria."""
    diag_algo = scoring.get("diagnostic_algorithm", {})

    # Score subscales first
    for sub in scoring.get("subscales", []):
        sub_total = sum(int(responses.get(str(i), 0)) for i in sub["items"])
        result["subscales"].append({
            "name": sub["name"],
            "score": sub_total,
            "max_score": sub.get("range", [0, 8])[1]
        })

    # Check PTSD criteria
    ptsd_met = True
    ptsd_criteria = diag_algo.get("ptsd", {}).get("criteria", [])
    for criterion in ptsd_criteria:
        endorsed = sum(
            1 for i in criterion["items"]
            if int(responses.get(str(i), 0)) >= criterion["threshold"]
        )
        if endorsed < criterion["min_endorsed"]:
            ptsd_met = False
            break

    # Check CPTSD criteria (requires PTSD + DSO)
    cptsd_met = False
    if ptsd_met:
        cptsd_met = True
        additional = diag_algo.get("cptsd", {}).get("additional_criteria", [])
        for criterion in additional:
            endorsed = sum(
                1 for i in criterion["items"]
                if int(responses.get(str(i), 0)) >= criterion["threshold"]
            )
            if endorsed < criterion["min_endorsed"]:
                cptsd_met = False
                break

    if cptsd_met:
        result["severity"] = "cptsd"
        result["label"] = {"de": "Kriterien für Komplexe PTBS erfüllt", "en": "Complex PTSD criteria met"}
        result["color"] = "#B71C1C"
    elif ptsd_met:
        result["severity"] = "ptsd"
        result["label"] = {"de": "Kriterien für PTBS erfüllt", "en": "PTSD criteria met"}
        result["color"] = "#F44336"
    else:
        result["severity"] = "below_threshold"
        result["label"] = {"de": "Kriterien nicht erfüllt", "en": "Criteria not met"}
        result["color"] = "#4CAF50"

    result["details"]["ptsd_criteria_met"] = ptsd_met
    result["details"]["cptsd_criteria_met"] = cptsd_met

    return result


def _score_classification(test_def, scoring, items, responses, result):
    """Classification-based scoring (C-SSRS)."""
    risk_levels = scoring.get("risk_levels", [])
    highest_level = risk_levels[0] if risk_levels else None

    for item in items:
        key = str(item["number"])
        if key in responses and int(responses[key]) > 0:
            # Find the corresponding risk level
            for level in risk_levels:
                if item["number"] in level.get("items_positive", []):
                    highest_level = level

    if highest_level:
        result["severity"] = highest_level.get("level", "unknown")
        result["label"] = highest_level.get("label", {})
        result["color"] = highest_level.get("color", "#9E9E9E")
        result["action"] = highest_level.get("action", {})

    # Always include emergency resources for C-SSRS
    result["details"]["emergency_resources"] = scoring.get("emergency_resources", {})

    return result


def _score_endorsement(test_def, scoring, items, responses, result):
    """Endorsement count + distress (PQ-16)."""
    endorsed = 0
    distress_total = 0

    for item in items:
        key = str(item["number"])
        endorse_key = f"{key}_endorsed"
        distress_key = f"{key}_distress"

        if endorse_key in responses and int(responses[endorse_key]) > 0:
            endorsed += 1
            if distress_key in responses:
                distress_total += int(responses[distress_key])

    result["total_score"] = endorsed
    result["max_score"] = len(items)
    result["details"]["distress_score"] = distress_total
    result["details"]["distress_max"] = len(items) * 3

    for thresh in scoring.get("thresholds", []):
        if thresh["min"] <= endorsed <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    return result


def _score_domain_mean(test_def, scoring, items, responses, result):
    """Domain-based mean scoring (PID-5-BF)."""
    domains = scoring.get("domains", [])
    domain_thresholds = scoring.get("thresholds_per_domain", [])

    for domain in domains:
        domain_sum = sum(int(responses.get(str(i), 0)) for i in domain["items"])
        domain_range = domain.get("range", [0, 15])

        domain_severity = "low"
        domain_label = {}
        domain_color = "#4CAF50"
        for thresh in domain_thresholds:
            if thresh["min"] <= domain_sum <= thresh["max"]:
                domain_severity = thresh["severity"]
                domain_label = thresh["label"]
                domain_color = thresh["color"]
                break

        result["subscales"].append({
            "name": domain["name"],
            "score": domain_sum,
            "max_score": domain_range[1],
            "severity": domain_severity,
            "label": domain_label,
            "color": domain_color,
            "hitop": domain.get("hitop", ""),
            "icd11_trait": domain.get("icd11_trait", "")
        })

    # Overall score = sum of all domains
    total = sum(int(responses.get(str(i), 0)) for i in range(1, len(items) + 1))
    result["total_score"] = total
    result["max_score"] = len(items) * 3

    return result


def _score_simple_sum(test_def, scoring, items, responses, result):
    """Simple sum + complex IRT scoring (WHODAS 2.0)."""
    # Simple sum for items 1-10 (Likert items only)
    likert_items = [i for i in items if i.get("response_type") != "days"]
    total = sum(int(responses.get(str(i["number"]), 0)) for i in likert_items)

    simple_range = scoring.get("simple", {}).get("range", [0, 40])
    result["total_score"] = total
    result["max_score"] = simple_range[1]

    for thresh in scoring.get("thresholds_simple", []):
        if thresh["min"] <= total <= thresh["max"]:
            result["severity"] = thresh.get("severity", "unknown")
            result["label"] = thresh.get("label", {})
            result["color"] = thresh.get("color", "#9E9E9E")
            break

    # Domain scores
    for domain in scoring.get("domains", []):
        dom_total = sum(int(responses.get(str(i), 0)) for i in domain["items"] if not any(
            it.get("response_type") == "days" for it in items if it["number"] == i
        ))
        result["subscales"].append({
            "name": domain["name"],
            "score": dom_total,
            "max_score": len(domain["items"]) * 4
        })

    # Days items
    for item in items:
        if item.get("response_type") == "days":
            key = str(item["number"])
            if key in responses:
                result["details"][f"item_{key}_days"] = int(responses.get(key, 0))

    return result


def _check_critical_items(test_def, responses, result):
    """Check for critical items that trigger alerts."""
    scoring = test_def.get("scoring", {})

    # PHQ-9 Item 9 (suicidality)
    critical = scoring.get("critical_item")
    if critical:
        key = str(critical["item_number"])
        if key in responses and int(responses[key]) > 0:
            result["alerts"].append(critical["alert"])

    # General critical items
    for item in test_def.get("items", []):
        if item.get("critical"):
            key = str(item["number"])
            if key in responses and int(responses[key]) > 0:
                result["alerts"].append({
                    "de": f"WARNUNG: Kritisches Item {item['number']} positiv beantwortet!",
                    "en": f"WARNING: Critical item {item['number']} endorsed!"
                })


def get_score_percentage(result: dict) -> float:
    """Get score as percentage 0-100."""
    if result["max_score"] == 0:
        return 0.0
    return round((result["total_score"] / result["max_score"]) * 100, 1)
