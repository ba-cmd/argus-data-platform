# Argus — Plateforme d'Intelligence d'Audit Continu

Projet de Data Engineering réaliste, construit dans le cadre d'un apprentissage encadré simulant le fonctionnement d'un grand cabinet international d'audit et de conseil.

## Contexte

Ce dépôt documente et implémente **Argus**, une plateforme data de bout en bout (ingestion batch + streaming, qualité de données, lakehouse, transformation, gouvernance, détection d'anomalies, API) construite pour l'entreprise fictive **Véridien & Associés**.

Le projet suit un fonctionnement Agile Scrum complet (Product Vision, Backlog, Sprints, ADR, Code Reviews, Sprint Review/Retrospective) afin de reproduire les conditions réelles de travail d'un Data Engineer dans une grande organisation internationale.

## Documentation

| Document | Contenu |
|---|---|
| [`docs/00-analyse-marche-besoins.md`](docs/00-analyse-marche-besoins.md) | Analyse des problématiques Data des grands cabinets d'audit/conseil |
| [`docs/01-selection-projet.md`](docs/01-selection-projet.md) | 3 propositions de projet et sélection argumentée |
| [`docs/02-entreprise-fictive-veridian.md`](docs/02-entreprise-fictive-veridian.md) | Présentation de Véridien & Associés |
| [`docs/03-organisation-agile.md`](docs/03-organisation-agile.md) | Pôle, entités, équipes, rôles, parties prenantes |
| [`docs/04-architecture-globale.md`](docs/04-architecture-globale.md) | Architecture fonctionnelle, technique, data, flux |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`docs/05-plan-de-travail.md`](docs/05-plan-de-travail.md) | Plan de travail complet, Epics, Sprints, DoD |
| [`docs/06-guide-environnement-local.md`](docs/06-guide-environnement-local.md) | Configuration du poste de développement (WSL2, profils Docker) |
| [`docs/07-dossier-synthese-client-projet-technologies.md`](docs/07-dossier-synthese-client-projet-technologies.md) | Dossier de synthèse : client, projet, et choix technologiques comparés à leurs alternatives |
| [`docs/prompt-nouvelle-conversation.md`](docs/prompt-nouvelle-conversation.md) | Prompt à réutiliser pour ouvrir la conversation de chaque Sprint |

## Statut

Phase actuelle : **cadrage (avant Sprint 0)**. Le plan de travail est en attente de validation avant démarrage du développement.
## Contribution

Convention de branches : `main` est la branche protégée (jamais de commit direct dessus une fois la CI en place) ; chaque ticket est développé sur une branche `feature/argus-N-description-courte`, fusionnée via Pull Request après revue.
## Stack technique cible

Apache Spark/PySpark · Apache Kafka · Kafka Connect · Schema Registry · Apache Cassandra · Elasticsearch · PostgreSQL · Apache Iceberg · Apache Parquet · Apache Avro · dbt · Apache Airflow · FastAPI · GraphQL · Docker/Kubernetes · Terraform · OpenLineage · OpenMetadata · Prometheus/Grafana · Great Expectations · MinIO · Trino/DuckDB

Voir les [ADR](docs/adr/) pour la justification de chaque choix.
