"""
CLI runner for the CS Master's Program Recommender.

Loads programs from data/programs.csv and per-program text files,
scores them against applicant personas, and prints ranked recommendations
with retrieval-backed explanations.
"""

from src.recommender import load_programs, recommend_programs, retrieve_program_notes, confidence_label


def main() -> None:
    programs = load_programs("data/programs.csv")
    print(f"Loaded {len(programs)} programs\n")

    personas = {
        "Budget-Focused Domestic": {
            "max_tuition": 25000,
            "max_application_fee": 100,
            "is_international": False,
            "willing_gre": False,
            "preferred_delivery": "online",
            "needs_visa_support": False,
            "preferred_ranking_tier": 3,
            "research_focus": False,
            "max_duration_months": 30,
            "preferred_specializations": ["ml", "software-engineering"],
            "preferred_location": "any",
        },
        "International Applicant": {
            "max_tuition": 70000,
            "max_application_fee": 150,
            "is_international": True,
            "willing_gre": True,
            "preferred_delivery": "in-person",
            "needs_visa_support": True,
            "preferred_ranking_tier": 2,
            "research_focus": True,
            "max_duration_months": 18,
            "preferred_specializations": ["ml", "ai"],
            "preferred_location": "any",
        },
        "Online-First Learner": {
            "max_tuition": 30000,
            "max_application_fee": 100,
            "is_international": False,
            "willing_gre": False,
            "preferred_delivery": "online",
            "needs_visa_support": False,
            "preferred_ranking_tier": 3,
            "research_focus": False,
            "max_duration_months": 36,
            "preferred_specializations": ["systems", "software-engineering"],
            "preferred_location": "any",
        },
        "Research-Oriented Top-Tier": {
            "max_tuition": 80000,
            "max_application_fee": 150,
            "is_international": False,
            "willing_gre": True,
            "preferred_delivery": "in-person",
            "needs_visa_support": False,
            "preferred_ranking_tier": 1,
            "research_focus": True,
            "max_duration_months": 18,
            "preferred_specializations": ["ml", "ai", "theory"],
            "preferred_location": "any",
        },
        "Ranking-Focused Career Switcher": {
            "max_tuition": 70000,
            "max_application_fee": 130,
            "is_international": False,
            "willing_gre": True,
            "preferred_delivery": "in-person",
            "needs_visa_support": False,
            "preferred_ranking_tier": 1,
            "research_focus": False,
            "max_duration_months": 18,
            "preferred_specializations": ["ml", "systems", "security"],
            "preferred_location": "any",
        },
    }

    # Five Options: "Budget-Focused Domestic", "International Applicant", 
    # "Online-First Learner", "Research-Oriented Top-Tier", 
    # "Ranking-Focused Career Switcher"
    
    active_persona_name = "International Applicant"
    applicant = personas[active_persona_name]

    print(f"Applicant Profile: {active_persona_name}")
    print("Preferences:")
    for key, value in applicant.items():
        print(f"  {key}: {value}")

    recommendations = recommend_programs(applicant, programs, k=5)

    print(f"\nTop {len(recommendations)} Recommended Programs:\n")
    for rank, (program, score, reasons_str) in enumerate(recommendations, start=1):
        app_fee = (
            program.get("application_fee_international", program["application_fee"])
            if applicant.get("is_international", False)
            else program["application_fee"]
        )
        print(f"#{rank} {program['university']} — {program['program_name']} [{confidence_label(score)}]")
        print(f"     Score: {score:.2f} | Delivery: {program['delivery']} | "
              f"Tuition: ${program['tuition_total']:,.0f} | "
              f"GRE Required: {program['gre_required']} | "
              f"App Fee: ${app_fee}")
        print(f"     Scoring breakdown: {reasons_str}")

        keywords = applicant["preferred_specializations"]
        retrieved = retrieve_program_notes(program["notes_file"], keywords)
        if retrieved:
            print(f"     Retrieved: {retrieved}")
        print()


if __name__ == "__main__":
    main()
