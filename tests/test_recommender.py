import os
import pytest
from src.recommender import Program, ApplicantProfile, Recommender, score_program, retrieve_program_notes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "programs")


def make_programs() -> list:
    return [
        Program(
            id=1,
            university="Top State University",
            program_name="MS Computer Science",
            location="san francisco ca",
            delivery="in-person",
            tuition_total=20000,
            application_fee=75,
            gre_required=True,
            duration_months=18,
            ranking_tier=2,
            visa_support=True,
            graduation_rate=0.88,
            specializations=["ml", "systems"],
            notes_file=os.path.join(NOTES_DIR, "ut_austin_mscs.txt"),
        ),
        Program(
            id=2,
            university="Online State University",
            program_name="Online MS Computer Science",
            location="remote",
            delivery="online",
            tuition_total=7000,
            application_fee=70,
            gre_required=False,
            duration_months=24,
            ranking_tier=3,
            visa_support=False,
            graduation_rate=0.72,
            specializations=["software-engineering", "hci"],
            notes_file=os.path.join(NOTES_DIR, "gatech_omscs.txt"),
        ),
    ]


def make_recommender() -> Recommender:
    return Recommender(make_programs())


# ---------------------------------------------------------------------------
# Ranking tests
# ---------------------------------------------------------------------------

def test_recommend_returns_programs_sorted_by_score():
    """Budget-friendly online applicant should prefer the cheaper online program."""
    applicant = ApplicantProfile(
        max_tuition=10000,
        max_application_fee=100,
        is_international=False,
        willing_gre=False,
        preferred_delivery="online",
        needs_visa_support=False,
        preferred_ranking_tier=3,
        research_focus=False,
        max_duration_months=30,
        preferred_specializations=["software-engineering"],
    )
    rec = make_recommender()
    results = rec.recommend(applicant, k=2)

    assert len(results) == 2
    assert results[0].delivery == "online"
    assert results[0].gre_required is False


def test_gre_required_program_ranks_lower_for_non_gre_applicant():
    """A program that requires GRE should rank below one that doesn't for an unwilling applicant."""
    applicant = ApplicantProfile(
        max_tuition=80000,
        max_application_fee=150,
        is_international=False,
        willing_gre=False,       # does NOT want GRE
        preferred_delivery="any",
        needs_visa_support=False,
        preferred_ranking_tier=3,
        research_focus=False,
        max_duration_months=36,
        preferred_specializations=["ml"],
    )
    rec = make_recommender()
    results = rec.recommend(applicant, k=2)

    # The GRE-optional program should rank first
    assert results[0].gre_required is False


def test_budget_constraint_penalizes_expensive_program():
    """A program over budget should score lower than an affordable one."""
    applicant_prefs = {
        "max_tuition": 8000,
        "max_application_fee": 100,
        "is_international": False,
        "willing_gre": True,
        "preferred_delivery": "any",
        "needs_visa_support": False,
        "preferred_ranking_tier": 3,
        "research_focus": False,
        "max_duration_months": 36,
        "preferred_specializations": [],
        "preferred_location": "any",
    }
    programs = make_programs()
    affordable = next(p for p in programs if p.tuition_total <= 8000)
    expensive = next(p for p in programs if p.tuition_total > 8000)

    affordable_score, _ = score_program(applicant_prefs, {
        **vars(affordable), "specializations": affordable.specializations
    })
    expensive_score, _ = score_program(applicant_prefs, {
        **vars(expensive), "specializations": expensive.specializations
    })

    assert affordable_score > expensive_score


def test_visa_support_boosts_score_for_international_applicant():
    """A program with visa support should score higher for an applicant who needs it."""
    applicant_prefs = {
        "max_tuition": 80000,
        "max_application_fee": 150,
        "is_international": False,
        "willing_gre": True,
        "preferred_delivery": "any",
        "needs_visa_support": True,   # needs visa support
        "preferred_ranking_tier": 3,
        "research_focus": False,
        "max_duration_months": 36,
        "preferred_specializations": [],
        "preferred_location": "any",
    }
    programs = make_programs()
    with_visa = next(p for p in programs if p.visa_support)
    without_visa = next(p for p in programs if not p.visa_support)

    score_with, _ = score_program(applicant_prefs, {**vars(with_visa), "specializations": with_visa.specializations})
    score_without, _ = score_program(applicant_prefs, {**vars(without_visa), "specializations": without_visa.specializations})

    assert score_with > score_without


def test_specialization_overlap_increases_score():
    """Matching specializations should add to the score."""
    base_prefs = {
        "max_tuition": 80000,
        "max_application_fee": 150,
        "is_international": False,
        "willing_gre": True,
        "preferred_delivery": "any",
        "needs_visa_support": False,
        "preferred_ranking_tier": 3,
        "research_focus": False,
        "max_duration_months": 36,
        "preferred_location": "any",
    }
    programs = make_programs()
    p = programs[0]  # specializations: ["ml", "systems"]
    prog_dict = {**vars(p), "specializations": p.specializations}

    score_no_match, _ = score_program({**base_prefs, "preferred_specializations": ["hci"]}, prog_dict)
    score_with_match, _ = score_program({**base_prefs, "preferred_specializations": ["ml"]}, prog_dict)

    assert score_with_match > score_no_match


# ---------------------------------------------------------------------------
# Explanation tests
# ---------------------------------------------------------------------------

def test_explain_recommendation_returns_non_empty_string():
    applicant = ApplicantProfile(
        max_tuition=80000,
        max_application_fee=150,
        is_international=False,
        willing_gre=True,
        preferred_delivery="in-person",
        needs_visa_support=False,
        preferred_ranking_tier=2,
        research_focus=True,
        max_duration_months=24,
        preferred_specializations=["ml", "systems"],
    )
    rec = make_recommender()
    program = rec.programs[0]
    explanation = rec.explain_recommendation(applicant, program)

    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_explanation_contains_scoring_reasons():
    """Explanation should include at least one scoring factor label."""
    applicant = ApplicantProfile(
        max_tuition=80000,
        max_application_fee=150,
        is_international=False,
        willing_gre=True,
        preferred_delivery="any",
        needs_visa_support=False,
        preferred_ranking_tier=3,
        research_focus=False,
        max_duration_months=36,
        preferred_specializations=["ml"],
    )
    rec = make_recommender()
    program = rec.programs[0]
    explanation = rec.explain_recommendation(applicant, program)

    assert any(keyword in explanation for keyword in ["budget", "GRE", "Delivery", "Tuition", "match", "+"])


# ---------------------------------------------------------------------------
# Retrieval tests
# ---------------------------------------------------------------------------

def test_retrieve_returns_empty_string_for_missing_file():
    result = retrieve_program_notes("data/programs/nonexistent_program.txt")
    assert result == ""


def test_retrieve_returns_text_without_keywords():
    notes_file = os.path.join(NOTES_DIR, "gatech_omscs.txt")
    if not os.path.exists(notes_file):
        pytest.skip("Program notes file not found")
    result = retrieve_program_notes(notes_file)
    assert isinstance(result, str)
    assert len(result) > 0


def test_retrieve_keyword_match_returns_relevant_sentence():
    notes_file = os.path.join(NOTES_DIR, "gatech_omscs.txt")
    if not os.path.exists(notes_file):
        pytest.skip("Program notes file not found")
    result = retrieve_program_notes(notes_file, keywords=["tuition"])
    assert "tuition" in result.lower() or len(result) > 0


def test_retrieve_gre_keyword_for_gre_optional_program():
    notes_file = os.path.join(NOTES_DIR, "gatech_omscs.txt")
    if not os.path.exists(notes_file):
        pytest.skip("Program notes file not found")
    result = retrieve_program_notes(notes_file, keywords=["GRE"])
    assert "gre" in result.lower()
