# Argus — Plateforme d'Intelligence d'Audit Continu

Projet de Data Engineering réaliste, construit dans le cadre d'un apprentissage encadré simulant le fonctionnement d'un grand cabinet international d'audit et de conseil.

## Contexte

Ce dépôt documente et implémente **Argus**, une plateforme data de bout en bout (ingestion batch + streaming, qualité de données, lakehouse, transformation, gouvernance, détection d'anomalies, API) construite pour l'entreprise fictive **Véridien & Associés**.

Le projet suit un fonctionnement Agile Scrum complet (Product Vision, Backlog, Sprints, ADR, Code Reviews, Sprint Review/Retrospective) afin de reproduire les conditions réelles de travail d'un Data Engineer dans une grande organisation internationale.

## Documentation

La documentation complète du projet (analyse de marché, sélection du projet, entreprise fictive, organisation Agile, architecture, ADR, plan de travail, guide d'environnement local, dossier de synthèse technologique) est maintenue en local, hors de ce dépôt Git, et sert de journal de travail au fil des Sprints.

## Statut

Phase actuelle : **cadrage (avant Sprint 0)**. Le plan de travail est en attente de validation avant démarrage du développement.
## Contribution

Convention de branches : `main` est la branche protégée (jamais de commit direct dessus une fois la CI en place) ; chaque ticket est développé sur une branche `feature/argus-N-description-courte`, fusionnée via Pull Request après revue.
## Stack technique cible

Apache Spark/PySpark · Apache Kafka · Kafka Connect · Schema Registry · Apache Cassandra · Elasticsearch · PostgreSQL · Apache Iceberg · Apache Parquet · Apache Avro · dbt · Apache Airflow · FastAPI · GraphQL · Docker/Kubernetes · Terraform · OpenLineage · OpenMetadata · Prometheus/Grafana · Great Expectations · MinIO · Trino/DuckDB

Voir les [ADR](docs/adr/) pour la justification de chaque choix.
