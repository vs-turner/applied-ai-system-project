import csv
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class Program:
    id: int
    university: str
    program_name: str
    location: str
    delivery: str           # "in-person", "online", "hybrid"
    tuition_total: float    # USD, full program cost
    application_fee: int    # USD (domestic/default)
    gre_required: bool
    duration_months: int
    ranking_tier: int       # 1=top10, 2=top25, 3=top50, 4=top100, 5=other
    visa_support: bool
    graduation_rate: float  # 0.0–1.0
    specializations: List[str]
    notes_file: str         # path to local text file (relative to project root)
    application_fee_international: int = 0  # USD


@dataclass
class ApplicantProfile:
    max_tuition: float
    max_application_fee: int
    is_international: bool
    willing_gre: bool
    preferred_delivery: str         # "in-person", "online", "hybrid", "any"
    needs_visa_support: bool
    preferred_ranking_tier: int     # 1–5; applicant wants programs at this tier or better
    research_focus: bool            # True = research-oriented, False = industry-oriented
    max_duration_months: int
    preferred_specializations: List[str]
    preferred_location: str = "any"


class Recommender:
    """OOP interface over the recommendation logic. Required by tests."""

    def __init__(self, programs: List[Program]):
        self.programs = programs

    def recommend(self, applicant: ApplicantProfile, k: int = 5) -> List[Program]:
        profile_dict = _profile_to_dict(applicant)
        scored = [
            (p, score_program(profile_dict, _program_to_dict(p))[0])
            for p in self.programs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored[:k]]

    def explain_recommendation(self, applicant: ApplicantProfile, program: Program) -> str:
        profile_dict = _profile_to_dict(applicant)
        _, reasons = score_program(profile_dict, _program_to_dict(program))
        keywords = applicant.preferred_specializations
        retrieved = retrieve_program_notes(program.notes_file, keywords)
        explanation = " | ".join(reasons)
        if retrieved:
            explanation += f"\n  Retrieved: {retrieved}"
        return explanation


def _profile_to_dict(p: ApplicantProfile) -> Dict:
    return {
        "max_tuition": p.max_tuition,
        "max_application_fee": p.max_application_fee,
        "is_international": p.is_international,
        "willing_gre": p.willing_gre,
        "preferred_delivery": p.preferred_delivery,
        "needs_visa_support": p.needs_visa_support,
        "preferred_ranking_tier": p.preferred_ranking_tier,
        "research_focus": p.research_focus,
        "max_duration_months": p.max_duration_months,
        "preferred_specializations": p.preferred_specializations,
        "preferred_location": p.preferred_location,
    }


def _program_to_dict(p: Program) -> Dict:
    return {
        "id": p.id,
        "university": p.university,
        "program_name": p.program_name,
        "location": p.location,
        "delivery": p.delivery,
        "tuition_total": p.tuition_total,
        "application_fee": p.application_fee,
        "application_fee_international": p.application_fee_international,
        "gre_required": p.gre_required,
        "duration_months": p.duration_months,
        "ranking_tier": p.ranking_tier,
        "visa_support": p.visa_support,
        "graduation_rate": p.graduation_rate,
        "specializations": p.specializations,
        "notes_file": p.notes_file,
    }


def load_programs(csv_path: str) -> List[Dict]:
    programs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            domestic_fee = int(row["application_fee"])
            intl_fee = int(row.get("application_fee_international", domestic_fee) or domestic_fee)
            programs.append({
                "id": int(row["id"]),
                "university": row["university"],
                "program_name": row["program_name"],
                "location": row["location"].strip().lower(),
                "delivery": row["delivery"].strip().lower(),
                "tuition_total": float(row["tuition_total"]),
                "application_fee": domestic_fee,
                "application_fee_international": intl_fee,
                "gre_required": row["gre_required"].strip().lower() == "true",
                "duration_months": int(row["duration_months"]),
                "ranking_tier": int(row["ranking_tier"]),
                "visa_support": row["visa_support"].strip().lower() == "true",
                "graduation_rate": float(row["graduation_rate"]),
                "specializations": [s.strip().lower() for s in row["specializations"].split(";")],
                "notes_file": row["notes_file"],
            })
    return programs


def retrieve_program_notes(notes_file: str, keywords: List[str] = None) -> str:
    """Return relevant sentences from a program's local text file.

    Falls back to the first 300 characters if no keywords are given or nothing matches.
    """
    if not os.path.exists(notes_file):
        return ""
    with open(notes_file, encoding="utf-8") as f:
        text = f.read()
    if not keywords:
        return text[:300].strip()
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    matched = [s for s in sentences if any(kw.lower() in s.lower() for kw in keywords)]
    return ". ".join(matched[:3]).strip() if matched else text[:300].strip()


def score_program(applicant: Dict, program: Dict) -> Tuple[float, List[str]]:
    """Score a single program against applicant preferences.

    Returns (score, reasons) where reasons is a list of human-readable strings
    explaining each scoring contribution.
    """
    score = 0.0
    reasons = []

    # Tuition fit (weight: 3.0)
    if program["tuition_total"] <= applicant["max_tuition"]:
        score += 3.0
        reasons.append(
            f"Within budget (+3.0): ${program['tuition_total']:,.0f} <= ${applicant['max_tuition']:,.0f}"
        )
    else:
        over_ratio = (program["tuition_total"] - applicant["max_tuition"]) / applicant["max_tuition"]
        penalty = round(min(3.0, over_ratio * 3.0), 2)
        score -= penalty
        reasons.append(
            f"Over budget (-{penalty}): ${program['tuition_total']:,.0f} > ${applicant['max_tuition']:,.0f}"
        )

    # GRE requirement (weight: 2.5)
    if not applicant["willing_gre"] and program["gre_required"]:
        score -= 2.5
        reasons.append("GRE required but applicant prefers GRE-optional (-2.5)")
    else:
        score += 1.0
        label = "GRE required and applicant willing" if program["gre_required"] else "GRE not required"
        reasons.append(f"GRE compatible (+1.0): {label}")

    # Delivery mode (weight: 2.0)
    if applicant["preferred_delivery"] == "any" or applicant["preferred_delivery"] == program["delivery"]:
        score += 2.0
        reasons.append(f"Delivery match (+2.0): {program['delivery']}")
    else:
        reasons.append(f"Delivery mismatch (0): wants {applicant['preferred_delivery']}, offers {program['delivery']}")

    # Visa support (weight: 2.0 / -1.5)
    if applicant["needs_visa_support"] and program["visa_support"]:
        score += 2.0
        reasons.append("Visa support available (+2.0)")
    elif applicant["needs_visa_support"] and not program["visa_support"]:
        score -= 1.5
        reasons.append("Visa support unavailable (-1.5)")

    # Ranking tier (weight: 1.5)
    tier_diff = program["ranking_tier"] - applicant["preferred_ranking_tier"]
    if tier_diff <= 0:
        score += 1.5
        reasons.append(f"Meets ranking preference (+1.5): tier {program['ranking_tier']}")
    else:
        penalty = round(min(1.5, tier_diff * 0.5), 2)
        score -= penalty
        reasons.append(
            f"Below ranking preference (-{penalty}): tier {program['ranking_tier']} vs preferred {applicant['preferred_ranking_tier']}"
        )

    # Specialization overlap (weight: up to 1.5)
    overlap = set(applicant["preferred_specializations"]) & set(program["specializations"])
    if overlap:
        spec_score = round(min(1.5, len(overlap) * 0.75), 2)
        score += spec_score
        reasons.append(f"Specialization match (+{spec_score}): {', '.join(sorted(overlap))}")

    # Application fee (weight: 1.0 / -0.5)
    fee_key = "application_fee_international" if applicant.get("is_international", False) else "application_fee"
    applied_fee = program.get(fee_key, program["application_fee"])
    if applied_fee <= applicant["max_application_fee"]:
        score += 1.0
        reasons.append(f"Application fee within limit (+1.0): ${applied_fee}")
    else:
        score -= 0.5
        reasons.append(
            f"Application fee over limit (-0.5): ${applied_fee} > ${applicant['max_application_fee']}"
        )

    # Research vs industry fit (weight: 1.0 / 0.5)
    if applicant["research_focus"] and program["ranking_tier"] <= 2:
        score += 1.0
        reasons.append("Strong research program matches research focus (+1.0)")
    elif not applicant["research_focus"] and program["ranking_tier"] >= 3:
        score += 0.5
        reasons.append("Industry-oriented program matches industry focus (+0.5)")

    # Duration fit (weight: 0.5)
    if program["duration_months"] <= applicant["max_duration_months"]:
        score += 0.5
        reasons.append(f"Duration within target (+0.5): {program['duration_months']} months")
    else:
        reasons.append(
            f"Duration over target (0): {program['duration_months']} months > {applicant['max_duration_months']} months"
        )

    # Location preference (weight: 1.0)
    if applicant["preferred_location"] != "any" and applicant["preferred_location"].lower() in program["location"]:
        score += 1.0
        reasons.append(f"Location match (+1.0): {program['location']}")

    return (round(score, 4), reasons)


def confidence_label(score: float) -> str:
    """Classify match quality into a human-readable tier based on score."""
    if score >= 9.0:
        return "Strong match"
    if score >= 5.0:
        return "Moderate match"
    return "Weak match"


def recommend_programs(applicant: Dict, programs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all programs, rank by score descending, return top k with explanations."""
    scored = [(p, *score_program(applicant, p)) for p in programs]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:k]
    return [
        (program, score, " | ".join(reasons))
        for program, score, reasons in top
    ]
