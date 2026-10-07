"""Local NASA knowledge base and offline evidence retriever for Pillar 4.
Contains canonical NASA research and clinical guidelines referenced in the project research docs.
Works 100% offline without requiring any external network requests.
"""

from typing import List, Dict, Any
from aegis_deepspace.models import EvidenceCitation


# Pre-cached NASA research references from NASA Human Research Roadmap (HRR), NTRS, and LSDA
NASA_KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {
        "id": "NASA-HRR-RAD-01",
        "topic": "radiation",
        "source": "NASA Human Research Roadmap (HRR)",
        "title": "Risk of Acute Radiation Syndromes Due to Solar Particle Events",
        "citation": "Durante & Cucinotta 2011, Rev. Mod. Phys. / Zeitlin et al. 2013, Science",
        "excerpt": "During high-flux solar particle events (SPEs), ambient habitat dose rates exceeding 0.1 mSv/h require immediate crew relocation to module topologies with shielding mass density >35 g/cm2 (e.g., storm shelters or water wall enclosures) to mitigate acute hematopoietic and prodromal effects.",
        "reference_url": "https://humanresearchroadmap.nasa.gov/risks/risk.aspx?i=100"
    },
    {
        "id": "NASA-NTRS-VOICE-01",
        "topic": "voice_vitals",
        "source": "NASA NTRS / LSDA",
        "title": "Acoustic Biomarkers for Fatigue and Cognitive Strain in High-Stress Analog Environments",
        "citation": "Fagherazzi et al. 2021, Digital Biomarkers; Basner et al. 2015, Aerosp. Med. Hum. Perform.",
        "excerpt": "Vocal acoustic features, including elevated fundamental frequency jitter, vowel space reduction, and speech rate degradation (>1.5 SD from baseline), provide passive detection of neuro-behavioral exhaustion and subclinical cognitive slowing before psychomotor vigilance performance fails.",
        "reference_url": "https://ntrs.nasa.gov/citations/20130014735"
    },
    {
        "id": "NASA-NTRS-HYPOXIA-01",
        "topic": "hypoxia_co2",
        "source": "NASA Exploration Atmospheres Working Group (NTRS)",
        "title": "Clinical Standards for Hypoxia and Hypercapnia under Closed Environmental Control",
        "citation": "Law et al. 2014, Aviat. Space Environ. Med. / NASA-STD-3001",
        "excerpt": "Elevated vocal strain combined with acoustic dyspnea markers indicates impending hypoxemia or hypercapnia in confined spacecraft habitats. Immediate cabin partial pressure (ppO2 and ppCO2) verification and supplemental oxygen staging are recommended.",
        "reference_url": "https://ntrs.nasa.gov/citations/20120017346"
    },
    {
        "id": "NASA-LSDA-TWIN-01",
        "topic": "astro_twin",
        "source": "NASA Life Sciences Data Archive (LSDA) / OSDR",
        "title": "Musculoskeletal Deconditioning and Countermeasure Prescription in Deep-Space Transit",
        "citation": "LeBlanc et al. 2000, J. Musculoskelet. Neuronal Interact.; Smith et al. 2012, J. Bone Miner. Res.",
        "excerpt": "Cessation or restriction of daily resistive and aerobic exercise beyond 72 consecutive hours (e.g., during prolonged storm shelter sheltering) initiates exponential bone resorption (approx. 1.0-1.5% BMD loss/month) and calf muscle atrophy. Post-shelter countermeasure re-engagement requires progressive resistance loading.",
        "reference_url": "https://lsda.jsc.nasa.gov/"
    },
    {
        "id": "NASA-NTRS-BLACKOUT-01",
        "topic": "comms_blackout",
        "source": "NASA NTRS Technical Report",
        "title": "Communication Delays, Disruptions, and Blackouts for Crewed Mars Missions (ASCEND)",
        "citation": "ASCEND Technical Report 2022, NASA NTRS",
        "excerpt": "Under one-way transmission latencies exceeding 20 minutes or absolute communication blackouts, onboard medical operations must transition to autonomous clinical decision support. Ground telemetry handoffs must be deferred while local edge protocols guide crew safety.",
        "reference_url": "https://ntrs.nasa.gov/citations/20220013418"
    }
]


def retrieve_relevant_evidence(
    radiation_flag: bool = False,
    voice_flag: bool = False,
    hypoxia_flag: bool = False,
    astro_flag: bool = False,
    comms_offline: bool = False
) -> List[EvidenceCitation]:
    """Retrieves relevant NASA citations based on active anomaly flags locally and deterministically."""
    results: List[EvidenceCitation] = []
    
    for doc in NASA_KNOWLEDGE_BASE:
        topic = doc["topic"]
        match = False
        if topic == "radiation" and radiation_flag:
            match = True
        elif topic == "voice_vitals" and voice_flag:
            match = True
        elif topic == "hypoxia_co2" and hypoxia_flag:
            match = True
        elif topic == "astro_twin" and astro_flag:
            match = True
        elif topic == "comms_blackout" and comms_offline:
            match = True
            
        if match:
            results.append(
                EvidenceCitation(
                    source=doc["source"],
                    title=doc["title"],
                    citation=doc["citation"],
                    excerpt=doc["excerpt"],
                    reference_url=doc.get("reference_url")
                )
            )
            
    # Default baseline citation if no anomaly
    if not results:
        doc = NASA_KNOWLEDGE_BASE[1]  # Voice baseline
        results.append(
            EvidenceCitation(
                source=doc["source"],
                title=doc["title"],
                citation=doc["citation"],
                excerpt="Routine baseline monitoring: Continue passive acoustic tracking during nominal mission operations.",
                reference_url=doc.get("reference_url")
            )
        )
        
    return results
