# -*- coding: utf-8 -*-
"""
Remplace, dans tous les documents du projet, les termes anglais liés à
l'entreprise fictive et à son organisation par leurs équivalents français,
de façon cohérente sur l'ensemble du dépôt.

Ne touche PAS :
- aux noms de technologies (Kafka, Spark, Airflow, Squad Goals Scrum...
  restent des noms propres de produits, hors périmètre) ;
- au vocabulaire Agile/Scrum standard (Sprint, Backlog, Epic, User Story,
  Product Owner, Scrum Master, ADR...), qui reste utilisé tel quel en
  français dans la pratique professionnelle réelle ;
- aux noms de produits concurrents réels cités en référence (EY Helix,
  PwC Halo, Deloitte Argus/Optix, KPMG Clara, Forvis Mazars, Accenture,
  Capgemini Invent...), qui sont des noms propres factuels ;
- aux noms de fichiers (restent en anglo-français mixte pour ne pas casser
  les liens déjà distribués).
"""
import re

# Ordre important : du plus spécifique/long au plus générique/court,
# pour éviter qu'un remplacement générique ne casse un remplacement
# plus spécifique qui doit s'appliquer en premier.
REPLACEMENTS = [
    # Tagline / nom complet du projet
    (r"Continuous Audit Intelligence Platform", "Plateforme d'Intelligence d'Audit Continu"),

    # Nom de la Tribu (avant le remplacement générique Veridian/Tribe)
    (r"Trust & Assurance Technology Tribe", "Tribu Technologie Audit & Confiance"),

    # Nom du Hub data (avant le remplacement générique Veridian)
    (r"Veridian Data (&|et) AI Hub", "Pôle Data & IA de Véridien"),
    (r"\bData (&|et) AI Hub\b", "Pôle Data & IA"),

    # Nom de l'entreprise (forme longue avant forme courte)
    (r"Veridian Global Advisory", "Véridien & Associés"),
    (r"\bVGA\b", "Véridien"),

    # Rôle de direction
    (r"Global Head of Audit Innovation", "Directeur Groupe de l'Innovation Audit"),

    # Noms des Squads (avant le remplacement générique Squad -> Équipe)
    (r"Ingestion (&|et) Connectivity", "Ingestion & Connectivité"),
    (r"Data Platform Core", "Plateforme Data"),
    (r"Data Quality (&|et) Governance", "Qualité & Gouvernance des Données"),
    (r"Analytics (&|et) Serving", "Analytique & Restitution"),
    (r"Platform Reliability \(DataOps\)", "Fiabilité de la Plateforme (DataOps)"),
    (r"Platform Reliability", "Fiabilité de la Plateforme"),

    # Lines of Service (forme avec abréviation avant forme sans, avant le
    # remplacement générique des noms de LoS)
    (r"Lines of Service \(LoS\)", "Métiers (branches d'activité)"),
    (r"Lines? of Service", lambda m: "Métiers" if m.group(0).lower().startswith("lines") else "Métier"),
    (r"\bLoS\b", "Métier"),

    # Noms des Lines of Service elles-mêmes
    (r"Assurance (&|et) Audit", "Audit & Certification des Comptes"),
    (r"Tax (&|et) Legal", "Fiscalité & Juridique"),
    (r"Risk Advisory", "Gestion des Risques"),
    (r"\bConsulting\b", "Conseil"),

    # Rôles
    (r"Engagement Partners", "Associés responsables de mission"),
    (r"Engagement Partner", "Associé responsable de mission"),
    (r"\bCISO\b", "RSSI"),

    # Organisation Spotify model : pluriels avant singuliers, casse capitalisée
    # avant casse minuscule (emploi en milieu de phrase)
    (r"\bSquads\b", "Équipes"),
    (r"\bSquad\b", "Équipe"),
    (r"\bsquads\b", "équipes"),
    (r"\bsquad\b", "équipe"),
    (r"\bTribes\b", "Tribus"),
    (r"\bTribe\b", "Tribu"),
    (r"\btribes\b", "tribus"),
    (r"\btribe\b", "tribu"),

    # Reliquat : "Veridian" utilisé seul comme adjectif/référence courte
    (r"\bVeridian\b", "Véridien"),
]

FILES = [
    "README.md",
    "docs/00-analyse-marche-besoins.md",
    "docs/01-selection-projet.md",
    "docs/02-entreprise-fictive-veridian.md",
    "docs/03-organisation-agile.md",
    "docs/04-architecture-globale.md",
    "docs/05-plan-de-travail.md",
    "docs/06-guide-environnement-local.md",
    "docs/07-dossier-synthese-client-projet-technologies.md",
    "docs/adr/0001-orchestrateur-airflow.md",
    "docs/adr/0002-format-table-lakehouse-iceberg.md",
    "docs/adr/0003-catalogue-lineage-openmetadata.md",
    "docs/adr/0004-streaming-backbone-kafka.md",
    "docs/adr/0005-hebergement-cloud-oracle-k3s.md",
    "docs/adr/0006-moteur-requetage-duckdb.md",
    "docs/product-vision.md",
    "docs/product-backlog.md",
    "docs/prompt-nouvelle-conversation.md",
    "build_lexicon.py",
]

def apply_replacements(text):
    for pattern, repl in REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text

def main():
    for path in FILES:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        updated = apply_replacements(original)
        if updated != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"MODIFIÉ  {path}")
        else:
            print(f"inchangé {path}")

if __name__ == "__main__":
    main()
