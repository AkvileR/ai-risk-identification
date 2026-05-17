from .constants import (
    NON_TIER_ARTICLE_PREFIXES,
    ROLE_CHANGING_ARTICLE_PREFIXES,
    RiskTier,
    Role,
)
from .state import CriterionFinding

_TIER_ORDER: list[RiskTier] = [
    RiskTier.MINIMAL,
    RiskTier.LIMITED,
    RiskTier.HIGH,
    RiskTier.PROHIBITED,
]

def _is_non_tier(article_ref: str) -> bool:
    return any(article_ref.startswith(p) for p in NON_TIER_ARTICLE_PREFIXES)

def is_role_changing_article(article_ref: str) -> bool:
    return any(article_ref.startswith(p) for p in ROLE_CHANGING_ARTICLE_PREFIXES)

def _conformity_gate_passes(
    initial_role: Role,
    findings: dict[str, CriterionFinding],
) -> bool:
    if initial_role == Role.PRODUCT_MANUFACTURER:
        return True
    conformity = findings.get("art6_third_party_conformity_assessment_required")
    return conformity is not None and conformity["applies"] == "yes"

def _significant_risk_gate_passes(findings: dict[str, CriterionFinding]) -> bool:
    hr5 = findings.get("art6_significant_risk")
    return hr5 is not None and hr5["applies"] == "yes"

def _passes_gates(
    finding: CriterionFinding,
    initial_role: Role,
    findings: dict[str, CriterionFinding],
) -> bool:
    art = finding["article_ref"]
    if art.startswith("Annex I §A") and not _conformity_gate_passes(initial_role, findings):
        return False
    if art.startswith("Annex III") and not _significant_risk_gate_passes(findings):
        return False
    return True

def article_to_tier(article_ref: str) -> RiskTier:
    if article_ref.startswith("Art. 50"):
        return RiskTier.LIMITED
    if article_ref.startswith("Art. 51"):
        return RiskTier.HIGH
    if article_ref.startswith("Art. 25"):
        return RiskTier.MINIMAL
    if article_ref.startswith("Art. 6(1)(b)"):
        return RiskTier.MINIMAL
    if article_ref.startswith("Art. 5("):
        return RiskTier.PROHIBITED
    if article_ref.startswith(("Annex I", "Annex III")):
        return RiskTier.HIGH
    raise ValueError(f"No tier mapping for article: {article_ref}")

def derive_tier(
    initial_role: Role,
    criterion_findings: dict[str, CriterionFinding],
) -> tuple[RiskTier, list[CriterionFinding]]:
    conformity_gate = _conformity_gate_passes(initial_role, criterion_findings)
    risk_gate = _significant_risk_gate_passes(criterion_findings)
    triggered = []
    for f in criterion_findings.values():
        if f["applies"] != "yes":
            continue
        if _is_non_tier(f["article_ref"]):
            continue
        if f["article_ref"].startswith("Annex I §A") and not conformity_gate:
            continue
        if f["article_ref"].startswith("Annex III") and not risk_gate:
            continue
        triggered.append(f)
    tier = RiskTier.MINIMAL
    for finding in triggered:
        finding_tier = article_to_tier(finding["article_ref"])
        if _TIER_ORDER.index(finding_tier) > _TIER_ORDER.index(tier):
            tier = finding_tier
    triggering = [f for f in triggered if article_to_tier(f["article_ref"]) == tier]
    return tier, triggering

def derive_gpai_systemic(
    criterion_findings: dict[str, CriterionFinding],
) -> bool:
    return any(
        f["applies"] == "yes" and f["article_ref"].startswith("Art. 51")
        for f in criterion_findings.values()
    )

def derive_role(
    initial_role: Role,
    criterion_findings: dict[str, CriterionFinding],
) -> Role:
    if initial_role == Role.PROVIDER:
        return Role.PROVIDER
    conformity_gate = _conformity_gate_passes(initial_role, criterion_findings)
    risk_gate = _significant_risk_gate_passes(criterion_findings)
    for f in criterion_findings.values():
        if f["applies"] != "yes":
            continue
        art = f["article_ref"]
        if art.startswith("Annex I §A") and not conformity_gate:
            continue
        if art.startswith("Annex III") and not risk_gate:
            continue
        if is_role_changing_article(art):
            return Role.PROVIDER
    return initial_role
