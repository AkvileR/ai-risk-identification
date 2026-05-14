from .constants import ALL_ROLES, AssessmentCriterion, Role

#TODO: article_ref might need to be reformatted to fit the KB style
CRITERIA: list[AssessmentCriterion] = [
    {
        # E1
        "id": "art3_entity_role",
        "article_ref": "Art. 3",
        "question": "Which kind of entity is your organisation with respect to the AI system?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # E3
        "id": "art25_3_pm_integrates_ai",
        "article_ref": "Art. 25(3)",
        "question": "Does your product integrate an AI system that is (or will be) placed on the market or put into service under your name or trademark — either together with the product, or after the product has been placed on the market?",
        "applies_to_roles": {Role.PRODUCT_MANUFACTURER},
    },
    {
        # HR1
        "id": "annex1_section_b_civil_aviation_security",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on civil aviation security?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_two_three_wheel_vehicles",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on two- or three-wheel vehicles and quadricycles?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_agricultural_forestry_vehicles",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on agricultural and forestry vehicles?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_marine_equipment",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on marine equipment?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_rail_interoperability",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on interoperability of the rail system?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_motor_vehicles",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on motor vehicles and their trailers?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR1
        "id": "annex1_section_b_civil_aviation",
        "article_ref": "Annex I §B",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on civil aviation?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6 — same definition
        "id": "annex1_section_a_machinery",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on machinery?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_toys",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on the safety of toys?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_recreational_craft",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on recreational craft and personal watercraft?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_lifts",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on lifts and safety components for lifts?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_explosive_atmospheres_equipment",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on equipment and protective systems intended for use in potentially explosive atmospheres?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_radio_equipment",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on radio equipment?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_pressure_equipment",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on pressure equipment?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_cableway_installations",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on cableway installations?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_personal_protective_equipment",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on personal protective equipment?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_gaseous_fuels_appliances",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on appliances burning gaseous fuels?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_medical_devices",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on medical devices?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR2 / HR6
        "id": "annex1_section_a_in_vitro_diagnostic_medical_devices",
        "article_ref": "Annex I §A",
        "question": "Is the AI system intended to be used as a safety component of, or itself, a product covered by the Union harmonisation legislation on in vitro diagnostic medical devices?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR3
        "id": "art6_third_party_conformity_assessment_required",
        "article_ref": "Art. 6(1)(b)",
        "question": "Is the product (or the product for which the AI system is a safety component) required to undergo a third-party conformity assessment under existing EU laws?",
        "applies_to_roles": {
            Role.PROVIDER,
            Role.DEPLOYER,
            Role.DISTRIBUTOR,
            Role.IMPORTER,
        },
    },
    {
        # HR4
        "id": "annex3_biometrics",
        "article_ref": "Annex III §1",
        "question": "Is the AI system, where its use is permitted under relevant Union or national law, a remote biometric identification system (other than biometric verification confirming a person is who they claim to be), a biometric categorisation system based on sensitive or protected attributes, or an emotion recognition system?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_critical_infrastructure",
        "article_ref": "Annex III §2",
        "question": "Is the AI system intended to be used as a safety component in the management and operation of critical digital infrastructure, road traffic, or in the supply of water, gas, heating or electricity?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_education",
        "article_ref": "Annex III §3",
        "question": "Is the AI system intended to be used to determine access or admission to or assign people to educational and vocational training institutions, to evaluate learning outcomes, to assess the appropriate level of education, or to monitor and detect prohibited behaviour during tests at any level of education or vocational training?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_employment",
        "article_ref": "Annex III §4",
        "question": "Is the AI system intended to be used for recruitment or selection of natural persons (including targeted job advertising, application filtering, and candidate evaluation), or to make decisions affecting work-related relationships such as promotion, termination, task allocation based on individual behaviour or traits, or monitoring and evaluating performance and behaviour?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_essential_services",
        "article_ref": "Annex III §5",
        "question": "Is the AI system intended to be used to evaluate eligibility for essential public assistance benefits or healthcare services, to evaluate creditworthiness or establish a credit score (other than for detecting financial fraud), to assess risk and pricing in life or health insurance, or to evaluate, classify or dispatch emergency calls and first-response services?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_law_enforcement",
        "article_ref": "Annex III §6",
        "question": "Is the AI system, where permitted by Union or national law, intended to be used by or on behalf of law enforcement (or Union institutions supporting them) to assess victimisation risk, as a polygraph or similar tool, to evaluate evidence reliability, to assess offending or re-offending risk, or for profiling natural persons in the detection, investigation or prosecution of criminal offences?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_migration_border",
        "article_ref": "Annex III §7",
        "question": "Is the AI system, where permitted by Union or national law, intended to be used by or on behalf of competent public authorities (or Union institutions) in migration, asylum or border-control management — as a polygraph or similar tool, to assess security/irregular-migration/health risk of persons entering a Member State, to assist examination of asylum, visa or residence applications, or to detect, recognise or identify persons (other than verifying travel documents)?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR4
        "id": "annex3_justice_democracy",
        "article_ref": "Annex III §8",
        "question": "Is the AI system intended to be used by or on behalf of a judicial authority to assist in researching and interpreting facts and the law and applying the law to a concrete set of facts (or in alternative dispute resolution in a similar way), or intended to influence the outcome of an election or referendum or the voting behaviour of natural persons (excluding administrative or logistical campaign tools to which voters are not directly exposed)?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # HR5
        "id": "art6_significant_risk",
        "article_ref": "Art. 6(3)",
        "question": "Does the AI system pose a significant risk of harm to the health, safety or fundamental rights of natural persons?",
        "applies_to_roles": {
            Role.PROVIDER,
            Role.DEPLOYER,
            Role.DISTRIBUTOR,
            Role.IMPORTER,
        },
    },
    {
        # S1
        "id": "art2_provider_places_ai_eu",
        "article_ref": "Art. 2",
        "question": "Are you placing on the market or putting into service AI systems in the EU?",
        "applies_to_roles": {Role.PROVIDER},
    },
    {
        # S1
        "id": "art2_provider_places_gpai_eu",
        "article_ref": "Art. 2",
        "question": "Are you placing on the market General Purpose AI models in the EU?",
        "applies_to_roles": {Role.PROVIDER},
    },
    {
        # S1
        "id": "art2_deployer_established_eu",
        "article_ref": "Art. 2",
        "question": "Are you established or located within the EU?",
        "applies_to_roles": {Role.DEPLOYER},
    },
    {
        # S1
        "id": "art2_importer_third_country_trademark",
        "article_ref": "Art. 2",
        "question": "Are you established or located within the EU and placing on the market an AI system that bears the name or trademark of somebody established outside of the EU?",
        "applies_to_roles": {Role.IMPORTER},
    },
    {
        # S1
        "id": "art2_output_used_in_eu",
        "article_ref": "Art. 2",
        "question": "Is your AI system's output used in the EU?",
        "applies_to_roles": {Role.PROVIDER, Role.DEPLOYER, Role.DISTRIBUTOR},
    },
    {
        # R1
        "id": "gpai_systemic_risk",
        "article_ref": "Art. 51",
        "question": "Does the general-purpose AI model have high-impact capabilities — that is, the Commission designated it as having high-impact capabilities or impact equivalent to those criteria?",
        "applies_to_roles": {Role.PROVIDER},
    },
    {
        # R2
        "id": "art2_exclusions",
        "article_ref": "Art. 2",
        "question": "Does your AI system fall under any of the exclusions in Article 2?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_subliminal",
        "article_ref": "Art. 5(1)(a)",
        "question": "Does the system deploy subliminal techniques beyond a person's consciousness, or purposefully manipulative or deceptive techniques, with the objective or effect of materially distorting behaviour by appreciably impairing informed decision-making, in a manner that causes or is reasonably likely to cause significant harm?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_vulnerability_exploitation",
        "article_ref": "Art. 5(1)(b)",
        "question": "Does the system exploit vulnerabilities of a natural person or specific group due to age, disability, or a specific social or economic situation, with the objective or effect of materially distorting their behaviour in a manner that causes or is reasonably likely to cause significant harm?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_social_scoring",
        "article_ref": "Art. 5(1)(c)",
        "question": "Does the system evaluate or classify natural persons or groups over time based on social behaviour or personal/personality characteristics, producing a social score that leads to detrimental or unfavourable treatment in unrelated social contexts, or treatment that is unjustified or disproportionate to the underlying behaviour?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_predictive_policing",
        "article_ref": "Art. 5(1)(d)",
        "question": "Does the system make risk assessments of natural persons to predict the risk of committing a criminal offence based solely on profiling or assessing personality traits and characteristics, without being limited to supporting human assessment grounded in objective and verifiable facts directly linked to a criminal activity?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_untargeted_scraping",
        "article_ref": "Art. 5(1)(e)",
        "question": "Does the system create or expand facial recognition databases through the untargeted scraping of facial images from the internet or CCTV footage?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_emotion_workplace_education",
        "article_ref": "Art. 5(1)(f)",
        "question": "Does the system infer emotions of natural persons in workplace or education settings, outside of uses placed on the market or put into service for medical or safety reasons?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_biometric_categorization",
        "article_ref": "Art. 5(1)(g)",
        "question": "Does the system biometrically categorise individual natural persons to deduce or infer their race, political opinions, trade union membership, religious or philosophical beliefs, sex life or sexual orientation, outside of lawful labelling or filtering of biometric datasets or law-enforcement biometric categorisation?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R3
        "id": "art5_realtime_rbi",
        "article_ref": "Art. 5(1)(h)",
        "question": "Does the system involve the use of 'real-time' remote biometric identification in publicly accessible spaces for law-enforcement purposes, outside of strictly necessary uses for targeted search of victims of specific serious crimes, prevention of substantial and imminent threats to life or terrorist attacks, or localisation of suspects of serious offences?",
        "applies_to_roles": ALL_ROLES,
    },
    {
        # R4
        "id": "art50_chatbot",
        "article_ref": "Art. 50(1)",
        "question": "Is the AI system intended to interact directly with natural persons in a way that is not obvious to a reasonably well-informed, observant and circumspect person (and not exclusively a law-enforcement-authorised system for criminal-offence detection, prevention, investigation or prosecution that is not available for the public to report criminal offences)?",
        "applies_to_roles": {Role.PROVIDER},
    },
    {
        # R4
        "id": "art50_synthetic_content",
        "article_ref": "Art. 50(2)",
        "question": "Does the AI system (including a general-purpose AI system) generate synthetic audio, image, video or text content, beyond uses limited to assistive standard editing that does not substantially alter the input data or its semantics, and outside the law-enforcement-authorised exemption for criminal-offence detection, prevention, investigation or prosecution?",
        "applies_to_roles": {Role.PROVIDER},
    },
    {
        # R4
        "id": "art50_emotion_biometric_disclosure",
        "article_ref": "Art. 50(3)",
        "question": "Is the system an emotion recognition system or a biometric categorisation system whose deployer exposes natural persons to its operation, outside of uses permitted by law to detect, prevent or investigate criminal offences with appropriate safeguards under Union law?",
        "applies_to_roles": {Role.DEPLOYER},
    },
    {
        # R4
        "id": "art50_deepfake_disclosure",
        "article_ref": "Art. 50(4)",
        "question": "Does the AI system generate or manipulate image, audio or video content constituting a deep fake, outside of law-enforcement-authorised uses or the limited-disclosure regime for evidently artistic, creative, satirical, fictional or analogous works?",
        "applies_to_roles": {Role.DEPLOYER},
    },
    {
        # R4
        "id": "art50_public_interest_text_disclosure",
        "article_ref": "Art. 50(4)",
        "question": "Does the AI system generate or manipulate text that is published with the purpose of informing the public on matters of public interest, outside of law-enforcement-authorised uses or cases where the content has undergone human review or editorial control with assigned editorial responsibility?",
        "applies_to_roles": {Role.DEPLOYER},
    }
]

from .synthesis_utils import _is_non_tier, article_to_tier

CRITERIA_BY_ID: dict[str, AssessmentCriterion] = {c["id"]: c for c in CRITERIA}

_seen_ids: set[str] = set()
for _c in CRITERIA:
    assert _c["id"] not in _seen_ids, f"Duplicate id: {_c['id']}"
    _seen_ids.add(_c["id"])
    if not _is_non_tier(_c["article_ref"]):
        article_to_tier(_c["article_ref"])
    assert _c["question"].strip(), f"Empty question on {_c['id']}"
