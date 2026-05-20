from src.constants import ActivePhase, ExclusionType, IDENTIFICATION_CRITERION_IDS, RiskTier, Role, format_role
from src.state import RunSummary, State, Verdict
from src.synthesis_utils import _passes_gates, derive_gpai_systemic, derive_role, derive_tier

def synthesis(state: State):
    findings = state.get("criterion_findings") or {}
    sd = state["system_description"]

    tier, triggering_findings = derive_tier(sd["role"], findings)

    reportable = [
        f for f in findings.values()
        if f["criterion_id"] not in IDENTIFICATION_CRITERION_IDS
    ]
    applicable = sorted(
        [f for f in reportable if f["applies"] == "yes" and _passes_gates(f, sd["role"], findings)],
        key=lambda f: -f["confidence_score"],
    )
    non_applicable = sorted(
        [f for f in reportable if f["applies"] == "no"],
        key=lambda f: -f["confidence_score"],
    )
    uncertain = sorted(
        [f for f in reportable if f["applies"] == "uncertain"],
        key=lambda f: -f["confidence_score"],
    )

    detected_role = sd["role"]
    derived_role = derive_role(detected_role, findings)

    e3_finding = findings.get("art25_3_pm_integrates_ai")
    e3_fired = e3_finding is not None and e3_finding.get("applies") == "yes"

    if not sd["in_eu_scope"]:
        tier = RiskTier.OUT_OF_SCOPE
        tier_reasoning = (
            "Your system is out of scope of the EU AI Act. None of the Art. 2 "
            "scope criteria were met — see the scope or non-applicable findings section for the "
            "per-criterion reasoning."
        )
    elif detected_role == Role.AUTHORISED_REPRESENTATIVE:
        tier = RiskTier.OUT_OF_SCOPE
        tier_reasoning = (
            "As an Authorised Representative, risk-classification criteria do "
            "not apply. See Art. 3 for the role determination."
        )
    elif ExclusionType.MILITARY in sd["exclusions"]:
        tier = RiskTier.OUT_OF_SCOPE
        tier_reasoning = (
            "Your system falls under the Art. 2(3) exclusion for military, "
            "defence, or national-security use, so the AI Act does not apply."
        )
    elif ExclusionType.THIRD_COUNTRY_LE in sd["exclusions"]:
        tier = RiskTier.OUT_OF_SCOPE
        tier_reasoning = (
            "Your system falls under the Art. 2(4) exclusion for third-country "
            "public authorities or international organisations acting under an "
            "international LE / judicial-cooperation agreement, so the AI Act "
            "does not apply."
        )
    elif detected_role == Role.PRODUCT_MANUFACTURER and not e3_fired:
        tier = RiskTier.OUT_OF_SCOPE
        tier_reasoning = (
            "Your product does not integrate an AI system under your name or "
            "trademark, so Art. 25(3) / Annex I obligations do not apply. See "
            "Art. 25(3) for the specific reasoning."
        )
    elif detected_role == Role.PRODUCT_MANUFACTURER and derived_role != Role.PROVIDER:
        tier_reasoning = (
            "Product-manufacturer obligations apply, but no high-risk "
            "classification criteria were triggered. See the applicable findings section "
            "for the criteria evaluated."
        )
    else:
        triggering_articles = sorted({f["article_ref"] for f in triggering_findings})
        if triggering_articles:
            tier_reasoning = (
                f"You were assigned {tier} risk because the following articles "
                f"were determined to be applicable: {', '.join(triggering_articles)}. "
                f"See the applicable findings section for the specific criteria."
            )
        else:
            applied_non_tier = sorted({f["article_ref"] for f in applicable})
            if applied_non_tier:
                tier_reasoning = (
                    f"No tier-driving criteria (Annex I, Annex III, Art. 50, Art. 51) "
                    f"applied to your system. The following non-tier criteria did apply "
                    f"but do not on their own change the risk level: "
                    f"{', '.join(applied_non_tier)}. Your risk level is therefore low."
                )
            else:
                tier_reasoning = "Based on your input, no criteria applied to your system, thus the risk level was determined to be low."

    if derived_role != detected_role:
        role_note = (
            f"While we initially detected your role to be \"{format_role(detected_role)}\", "
            f"based on the applicable findings you would be considered a \"{format_role(derived_role)}\""
        )
        tier_reasoning = f"{role_note}\n\n{tier_reasoning}"

    article_citations = sorted({f["article_ref"] for f in applicable})

    is_gpai_systemic = sd["is_gpai"] and derive_gpai_systemic(findings)

    clarified = [f for f in findings.values() if f["clarification_round_count"] > 0]
    run_summary: RunSummary = {
        "criteria_evaluated_total": len(findings),
        "clarification_rounds_total": sum(f["clarification_round_count"] for f in findings.values()),
        "unique_criteria_clarified": len(clarified),
        "clarified_criterion_ids": sorted(f["criterion_id"] for f in clarified),
    }

    verdict: Verdict = {
        "role": derived_role,
        "detected_role": detected_role,
        "risk_tier": tier,
        "tier_reasoning": tier_reasoning,
        "is_gpai": sd["is_gpai"],
        "is_gpai_systemic": is_gpai_systemic,
        "exclusions": sd["exclusions"],
        "applicable_findings": applicable,
        "non_applicable_findings": non_applicable,
        "uncertain_findings": uncertain,
        "article_citations": article_citations,
        "run_summary": run_summary,
    }
    return {"verdict": verdict, "active_phase": ActivePhase.SYNTHESIS}
