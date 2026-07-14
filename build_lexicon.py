# -*- coding: utf-8 -*-
"""
Construit et injecte, à la fin de chaque document Markdown du projet Argus,
un lexique complet (définition / importance dans Argus / raison du choix)
pour chaque terme technique, technologique, méthodologique ou métier
mentionné dans ce document précis.
"""
import re

TERMS = {
# ============ A. CONCEPTS D'ARCHITECTURE DATA ============
"data_lake": {
    "label": "Data Lake",
    "definition": "Un espace de stockage centralisé qui conserve des données brutes, dans leur format d'origine (fichiers, logs, exports), sans exiger de schéma fixe à l'écriture.",
    "importance": "C'est la fondation physique du lakehouse Argus : toutes les données comptables et transactionnelles y transitent avant transformation.",
    "reason": "Il permet d'absorber des formats hétérogènes venant de multiples ERP clients sans devoir imposer un modèle unique dès l'ingestion, ce qu'un entrepôt de données classique ne permet pas.",
},
"lakehouse": {
    "label": "Lakehouse",
    "definition": "Une architecture hybride qui combine la flexibilité et le faible coût d'un Data Lake avec les garanties transactionnelles (ACID) et les capacités de requêtage d'un entrepôt de données (Data Warehouse).",
    "importance": "Argus est structuré comme un lakehouse : c'est le patron architectural central qui organise l'ensemble du cycle de vie de la donnée (zones Bronze/Silver/Gold).",
    "reason": "Un cabinet d'audit a besoin à la fois de gros volumes bruts à faible coût (lac) et de garanties fortes de cohérence/qualité pour les analyses (entrepôt) — le lakehouse évite de maintenir deux systèmes séparés.",
},
"data_warehouse": {
    "label": "Data Warehouse (entrepôt de données)",
    "definition": "Un système de stockage structuré, optimisé pour l'analyse, où les données sont modélisées selon un schéma défini à l'avance (schema-on-write).",
    "importance": "Argus s'en inspire pour sa zone Gold (marts d'audit modélisés), sans en être un au sens strict.",
    "reason": "Mentionné en comparaison avec le Data Lake et le Lakehouse pour justifier pourquoi Argus ne retient ni l'un ni l'autre isolément.",
},
"medallion": {
    "label": "Architecture en zones Bronze / Silver / Gold (architecture médaillon)",
    "definition": "Un modèle d'organisation du lakehouse en couches successives : Bronze (données brutes typées), Silver (données nettoyées et validées), Gold (modèles métier prêts à l'usage).",
    "importance": "C'est l'ossature de toute la couche de stockage d'Argus ; chaque pipeline de données progresse à travers ces zones.",
    "reason": "Elle sépare clairement la responsabilité de chaque étape (ingestion, qualité, modélisation métier), ce qui facilite la gouvernance, le débogage et la réutilisation des données intermédiaires.",
},
"data_vault": {
    "label": "Data Vault",
    "definition": "Une méthode de modélisation des données (et non une architecture de stockage) qui organise l'information en Hubs (entités métier identifiantes, ex. un client ou une transaction), Links (relations entre ces entités) et Satellites (attributs descriptifs, historisés dans le temps).",
    "importance": "Évoquée dans Argus comme modèle de modélisation possible pour la zone Silver/Gold du lakehouse, en complément ou alternative à un schéma en étoile Kimball.",
    "reason": "Elle conserve un historique complet des changements, facilite la traçabilité exigée en audit, et permet d'intégrer une nouvelle source (ex. un nouvel ERP filiale) sans reconstruire tout le modèle existant.",
},
"kimball": {
    "label": "Modèle Kimball (modélisation dimensionnelle)",
    "definition": "Une méthode de modélisation des données qui organise l'information en tables de faits (les mesures, ex. les transactions comptables) entourées de tables de dimensions (les axes d'analyse, ex. client, date, filiale), formant un schéma en étoile.",
    "importance": "C'est le modèle naturel de la zone Gold d'Argus, où les marts d'audit sont construits avec dbt (un outil directement issu de cette tradition de modélisation) pour être consommés par la BI et l'API.",
    "reason": "Il est simple à comprendre pour les utilisateurs métier et optimisé pour les performances de requêtage analytique, ce qui correspond exactement à l'usage de la couche Gold (tableaux de bord, indicateurs d'audit).",
},
"batch": {
    "label": "Traitement batch (par lots)",
    "definition": "Un mode de traitement où les données sont collectées puis traitées par lots à intervalles réguliers (ex. une fois par jour ou par mois), plutôt qu'au fil de l'eau.",
    "importance": "C'est le mode d'ingestion principal des grands livres comptables dans Argus, alimentant les zones Bronze puis Silver/Gold.",
    "reason": "Les exports comptables des ERP clients sont par nature périodiques (clôtures) — le batch est le mode naturellement adapté à ce rythme, avec un débit de traitement élevé.",
},
"streaming": {
    "label": "Traitement streaming (en flux continu)",
    "definition": "Un mode de traitement où chaque événement (transaction, paiement) est traité dès son arrivée, en continu, avec une latence de l'ordre de la seconde à la minute.",
    "importance": "Utilisé dans Argus pour le monitoring quasi temps réel des transactions financières et la détection d'anomalies au fil de l'eau.",
    "reason": "L'audit continu exige de détecter des anomalies rapidement, pas seulement lors de la clôture — le streaming comble ce besoin que le batch seul ne peut pas satisfaire.",
},
"lambda_architecture": {
    "label": "Architecture Lambda",
    "definition": "Un patron d'architecture qui fait cohabiter un chemin batch (exhaustif mais lent) et un chemin streaming (rapide mais partiel), avec une étape de réconciliation entre les deux.",
    "importance": "Argus l'applique pour rapprocher les agrégats issus du flux temps réel avec les écritures comptables officielles du batch.",
    "reason": "Elle donne le meilleur des deux mondes : réactivité du streaming pour l'alerte précoce, exhaustivité et fiabilité du batch pour la vérité comptable officielle.",
},
"cdc": {
    "label": "CDC (Change Data Capture)",
    "definition": "Une technique qui capte en continu les changements (insertions, mises à jour, suppressions) survenant dans une base de données source, pour les répliquer ailleurs sans réinterroger toute la base.",
    "importance": "Évoqué comme mécanisme d'ingestion alternatif/complémentaire aux exports fichiers, notamment dans les scénarios de gouvernance fédérée.",
    "reason": "Il évite de recharger l'intégralité d'une source à chaque synchronisation, ce qui est essentiel à l'échelle des volumes visés par Argus.",
},
"dq_gate": {
    "label": "Data Quality Gate (contrôle qualité bloquant)",
    "definition": "Un contrôle automatisé placé entre deux zones du lakehouse qui empêche une donnée non conforme (incomplète, incohérente) de progresser plus loin dans le pipeline.",
    "importance": "C'est un des piliers d'Argus (Epic E3) : aucune donnée n'atteint la zone Silver/Gold sans être passée par ce contrôle.",
    "reason": "Dans un contexte d'audit, une donnée fausse utilisée dans une analyse engage la responsabilité du cabinet — le contrôle qualité ne peut pas être optionnel ou a posteriori.",
},
"lineage": {
    "label": "Data Lineage (traçabilité des données)",
    "definition": "La cartographie de bout en bout du parcours d'une donnée : d'où elle vient, quelles transformations elle a subies, et où elle est utilisée.",
    "importance": "Argus capture le lineage à chaque étape de transformation (Epic E7), du fichier source jusqu'au résultat présenté à l'auditeur.",
    "reason": "Un régulateur ou un client peut exiger de justifier un chiffre — sans lineage, impossible de répondre avec certitude à la question 'd'où vient cette donnée ?'.",
},
"data_catalog": {
    "label": "Catalogue de données (Data Catalog)",
    "definition": "Un inventaire centralisé de tous les jeux de données d'une organisation, avec leurs propriétaires, leur description, leur niveau de sensibilité et leurs relations.",
    "importance": "Argus s'appuie sur un catalogue pour documenter chaque dataset produit et classifier sa sensibilité (PII, secret professionnel).",
    "reason": "Sans catalogue, une plateforme avec des dizaines de datasets par mission devient impossible à gouverner ou à auditer soi-même.",
},
"schema_registry_concept": {
    "label": "Schema Registry (registre de schémas)",
    "definition": "Un service qui stocke et versionne les schémas (structure) des messages échangés sur un flux de données, et vérifie leur compatibilité avant toute publication.",
    "importance": "Il encadre tous les messages Kafka circulant dans Argus, garantissant qu'aucun message mal formé ne peut être publié.",
    "reason": "Pour des données financières, une évolution de schéma non contrôlée pourrait fausser silencieusement une analyse — le registre impose une discipline de compatibilité.",
},
"schema_evolution": {
    "label": "Évolution de schéma (Schema Evolution)",
    "definition": "La capacité d'un format de données à accepter des changements de structure (ajout/suppression de colonnes) sans casser les usages existants ni réécrire l'historique.",
    "importance": "Permise nativement par Iceberg et encadrée par le Schema Registry pour Kafka, elle sécurise l'évolution du produit Argus dans le temps.",
    "reason": "Les besoins d'audit évoluent (nouveaux champs à tracer) ; sans cette capacité, chaque évolution obligerait à retraiter tout l'historique.",
},
"multi_tenant": {
    "label": "Multi-tenant",
    "definition": "Une architecture où une même infrastructure technique sert plusieurs clients ('tenants') tout en garantissant une isolation stricte de leurs données respectives.",
    "importance": "Chaque mission client de Véridien est un tenant dans Argus, avec un `tenant_id` propagé de bout en bout du pipeline.",
    "reason": "Le secret professionnel et les règles anti-conflit d'intérêts imposent qu'aucune donnée d'un client ne soit jamais visible par une autre mission, tout en mutualisant les coûts d'infrastructure.",
},
"partitioning": {
    "label": "Partitionnement",
    "definition": "Le découpage physique d'une table de données selon un ou plusieurs critères (ex. date, tenant), pour que les requêtes ne lisent que les portions pertinentes.",
    "importance": "Les tables Iceberg d'Argus sont partitionnées par tenant et par période, ce qui accélère les requêtes et renforce l'isolation.",
    "reason": "Sans partitionnement, chaque requête devrait scanner l'intégralité des données, ce qui est ingérable à l'échelle visée par le projet.",
},
"time_travel": {
    "label": "Time Travel",
    "definition": "La capacité d'interroger une table de données telle qu'elle existait à un instant précis dans le passé, grâce à l'historisation des versions.",
    "importance": "Permise par Iceberg, elle permet à un auditeur de reconstituer l'état exact d'une donnée à une date donnée.",
    "reason": "C'est une exigence directe du métier de l'audit : pouvoir prouver ce qu'on savait/voyait à une date de clôture précise.",
},
"etl_elt": {
    "label": "ETL / ELT",
    "definition": "Deux séquences de traitement de données : ETL (Extract-Transform-Load) transforme avant de charger ; ELT (Extract-Load-Transform) charge d'abord les données brutes puis les transforme dans le système cible.",
    "importance": "Argus suit une logique ELT : les données brutes sont chargées telles quelles en zone Bronze, puis transformées progressivement via Spark/dbt.",
    "reason": "L'approche ELT conserve toujours une copie brute exploitable (utile pour l'audit et le débogage) et tire parti de la puissance de calcul du lakehouse plutôt que d'un outil ETL externe.",
},
"testing_100": {
    "label": "Contrôle à 100% de la population (vs échantillonnage)",
    "definition": "Une approche d'audit qui analyse l'intégralité des transactions d'une période plutôt qu'un échantillon statistique représentatif.",
    "importance": "C'est l'objectif métier central d'Argus : remplacer le sondage traditionnel par une analyse exhaustive rendue possible par le traitement distribué.",
    "reason": "Un échantillon peut manquer une anomalie isolée mais significative ; le traitement à l'échelle (Spark) rend l'analyse exhaustive économiquement viable.",
},
"rbac": {
    "label": "RBAC (contrôle d'accès basé sur les rôles)",
    "definition": "Un modèle de sécurité où les droits d'accès sont attribués à des rôles (ex. 'auditeur mission A'), eux-mêmes attribués aux utilisateurs, plutôt que gérés individuellement.",
    "importance": "Argus l'utilise pour garantir qu'un utilisateur de la mission Client A ne puisse pas accéder aux données de la mission Client B (Epic E12).",
    "reason": "C'est le mécanisme concret qui rend le cloisonnement multi-tenant réellement applicable et vérifiable, exigence non négociable de secret professionnel.",
},
"data_mesh": {
    "label": "Data Mesh",
    "definition": "Un paradigme d'architecture data décentralisé où chaque domaine métier possède et expose ses propres données comme un produit, sous une gouvernance fédérée commune.",
    "importance": "Évalué comme piste de projet alternative (Projet C – Nexus) mais non retenu comme architecture centrale d'Argus.",
    "reason": "Pertinent à connaître car tendance forte du marché, mais écarté pour ce projet car il dilue le cas d'usage métier concret au profit d'un enjeu principalement organisationnel.",
},

# ============ B. TRAITEMENT DISTRIBUÉ ============
"spark": {
    "label": "Apache Spark",
    "definition": "Un moteur de traitement de données distribué, capable de répartir des calculs sur plusieurs machines pour traiter de très grands volumes de données en parallèle.",
    "importance": "C'est le moteur de calcul central d'Argus pour toutes les transformations lourdes (nettoyage, jointures, scoring ML) sur les zones Bronze/Silver/Gold.",
    "reason": "Il permet d'analyser 100% d'une population de données comptables (potentiellement des dizaines de millions de lignes), ce qu'un traitement sur une seule machine ne pourrait pas absorber dans un temps raisonnable.",
},
"pyspark": {
    "label": "PySpark",
    "definition": "L'interface Python d'Apache Spark, qui permet d'écrire des traitements distribués avec la syntaxe et les bibliothèques Python.",
    "importance": "C'est le langage utilisé pour tous les jobs de transformation et de scoring d'anomalies dans Argus.",
    "reason": "Python est le langage le plus demandé en Data Engineering/Data Science ; PySpark permet de combiner cette accessibilité avec la puissance de calcul distribué de Spark.",
},
"dbt": {
    "label": "dbt (data build tool)",
    "definition": "Un outil qui permet d'écrire les transformations de données en SQL versionné, testé et documenté, organisées en modèles dépendants les uns des autres.",
    "importance": "dbt construit les modèles métier d'audit d'Argus (zone Silver → Gold), avec des tests de qualité intégrés à chaque modèle.",
    "reason": "Il apporte au SQL analytique les bonnes pratiques du génie logiciel (versioning, tests, documentation, revue de code), ce que des scripts SQL ad hoc ne permettent pas.",
},

# ============ C. STREAMING ============
"kafka": {
    "label": "Apache Kafka",
    "definition": "Une plateforme de streaming distribuée qui permet de publier, stocker et consommer des flux d'événements en continu et à grande échelle.",
    "importance": "C'est le backbone streaming d'Argus (Epic E2) : il transporte le flux de transactions financières en quasi temps réel.",
    "reason": "C'est le standard de facto de l'event streaming en entreprise, indispensable pour la détection d'anomalies au fil de l'eau plutôt qu'uniquement en fin de période.",
},
"kafka_connect": {
    "label": "Kafka Connect",
    "definition": "Un framework qui standardise l'intégration entre Kafka et des systèmes externes (bases de données, moteurs de recherche) via des connecteurs prêts à l'emploi, sans code custom.",
    "importance": "Utilisé dans Argus pour écrire automatiquement les événements Kafka vers Cassandra et Elasticsearch (sinks).",
    "reason": "Il évite d'écrire et de maintenir du code consommateur répétitif pour chaque intégration, et illustre une compétence distincte de l'usage brut de producteurs/consommateurs Kafka.",
},
"avro": {
    "label": "Apache Avro",
    "definition": "Un format de sérialisation de données binaire et compact, associé à un schéma explicite qui décrit la structure de chaque enregistrement.",
    "importance": "C'est le format utilisé pour tous les messages publiés sur Kafka dans Argus, contrôlé par le Schema Registry.",
    "reason": "Il est plus compact et plus rapide à traiter que JSON, tout en imposant un contrat de schéma strict — essentiel pour des données financières sensibles.",
},
"windowing": {
    "label": "Fenêtre glissante (windowing)",
    "definition": "Une technique de traitement streaming qui regroupe les événements par intervalles de temps (ex. les 5 dernières minutes) pour calculer des agrégats en continu.",
    "importance": "Utilisée dans Argus pour appliquer des règles de détection légères sur le flux de transactions en quasi temps réel.",
    "reason": "Un flux infini de données ne peut pas être agrégé d'un coup ; les fenêtres permettent de calculer des indicateurs (ex. montant cumulé) sur des tranches de temps gérables.",
},

# ============ D. STOCKAGE / LAKEHOUSE ============
"minio": {
    "label": "MinIO",
    "definition": "Un serveur de stockage objet open source, compatible avec l'API Amazon S3, que l'on peut héberger soi-même.",
    "importance": "C'est le support physique du Data Lake d'Argus : tous les fichiers Parquet/Iceberg y sont stockés.",
    "reason": "Il permet de développer et tester en local exactement comme sur un vrai stockage cloud S3, sans dépendre d'un compte cloud payant, avec une migration triviale vers S3/OCI Object Storage plus tard.",
},
"iceberg": {
    "label": "Apache Iceberg",
    "definition": "Un format de table ouvert pour les lacs de données, qui apporte des garanties transactionnelles (ACID), l'évolution de schéma et le time travel, sans dépendre d'un moteur de calcul unique.",
    "importance": "C'est le format de table principal du lakehouse Argus (ADR-0002), utilisé dans toutes les zones Bronze/Silver/Gold.",
    "reason": "Contrairement à Delta Lake, il est nativement multi-moteur (Spark, Trino, DuckDB), ce qui correspond exactement à la stack volontairement plurielle d'Argus, et c'est un standard en forte adoption sur le marché.",
},
"parquet": {
    "label": "Apache Parquet",
    "definition": "Un format de fichier colonnaire, compressé et optimisé pour l'analyse de grands volumes de données.",
    "importance": "C'est le format de stockage physique sous-jacent à toutes les tables Iceberg d'Argus.",
    "reason": "Le stockage colonnaire permet de ne lire que les colonnes nécessaires à une requête et offre une compression bien supérieure à des formats ligne comme CSV — indispensable à l'échelle visée.",
},
"delta_lake": {
    "label": "Delta Lake",
    "definition": "Un format de table transactionnel pour les lacs de données, créé par Databricks, avec une intégration native très poussée avec Spark.",
    "importance": "Étudié comme alternative à Iceberg (ADR-0002) et testé ponctuellement dans un spike comparatif, sans être le format principal d'Argus.",
    "reason": "Sa comparaison avec Iceberg permet de démontrer une compréhension réelle des compromis entre les deux standards du marché, valorisable en entretien technique.",
},
"postgresql": {
    "label": "PostgreSQL",
    "definition": "Un système de gestion de base de données relationnelle open source, robuste et très largement utilisé en entreprise.",
    "importance": "Argus l'utilise comme base opérationnelle pour les métadonnées applicatives, les référentiels et les résultats agrégés servis par l'API.",
    "reason": "C'est le choix standard pour des données structurées à cohérence forte (transactions ACID), plus adapté que le lakehouse pour ce type d'usage applicatif au quotidien.",
},
"cassandra": {
    "label": "Apache Cassandra",
    "definition": "Une base de données NoSQL distribuée, optimisée pour un très haut débit d'écriture et une disponibilité continue, au prix d'une cohérence plus souple qu'une base relationnelle.",
    "importance": "Argus l'utilise pour historiser en continu les transactions et alertes issues du flux Kafka (serving haute fréquence).",
    "reason": "Le flux de transactions temps réel génère un volume d'écritures très élevé que PostgreSQL gérerait moins bien à cette échelle et cette vélocité.",
},
"elasticsearch": {
    "label": "Elasticsearch",
    "definition": "Un moteur de recherche et d'analyse distribué, spécialisé dans l'indexation et la recherche full-text rapide sur de grands volumes de documents.",
    "importance": "Argus l'utilise pour permettre aux auditeurs de rechercher rapidement dans les écritures comptables et les alertes lors d'une investigation.",
    "reason": "Une base relationnelle classique est mal adaptée à la recherche libre et floue dans du texte ; Elasticsearch est le standard pour ce besoin d'investigation.",
},
"rest_catalog": {
    "label": "REST Catalog (catalogue technique Iceberg)",
    "definition": "Un service qui référence l'emplacement et les métadonnées de toutes les tables Iceberg, accessible via une API REST standardisée.",
    "importance": "Il permet à Spark, Trino et DuckDB de retrouver et lire les mêmes tables Iceberg d'Argus de façon cohérente.",
    "reason": "Il évite la dépendance à un Hive Metastore classique et s'intègre proprement avec OpenMetadata pour la gouvernance.",
},

# ============ E. ORCHESTRATION ============
"airflow": {
    "label": "Apache Airflow",
    "definition": "Une plateforme d'orchestration qui permet de programmer, planifier et surveiller des workflows de données complexes (DAGs), avec gestion des dépendances et des reprises sur erreur.",
    "importance": "C'est l'orchestrateur retenu pour Argus (ADR-0001) : il déclenche et enchaîne tous les pipelines batch (ingestion, qualité, transformation).",
    "reason": "C'est le standard de facto de l'orchestration de données en entreprise, très demandé sur le marché de l'emploi et doté d'un écosystème mature pour Spark/dbt/Kafka.",
},
"dag": {
    "label": "DAG (Directed Acyclic Graph)",
    "definition": "Un graphe orienté sans cycle : une représentation des tâches d'un pipeline et de leurs dépendances, garantissant qu'aucune tâche ne dépend, directement ou indirectement, d'elle-même.",
    "importance": "Chaque pipeline batch d'Argus est modélisé comme un DAG Airflow.",
    "reason": "C'est la structure qui permet à Airflow de déterminer automatiquement l'ordre d'exécution correct des tâches et de paralléliser celles qui sont indépendantes.",
},
"dagster": {
    "label": "Dagster",
    "definition": "Un orchestrateur de données moderne, basé sur une approche 'asset-based' (on déclare les données produites plutôt que les tâches), avec une intégration native soignée de dbt et OpenLineage.",
    "importance": "Étudié comme alternative à Airflow (ADR-0001) et testé dans un spike optionnel, sans remplacer Airflow en production dans Argus.",
    "reason": "Comparer les deux approches (task-centric vs asset-centric) démontre une compréhension approfondie des choix d'orchestration, un vrai plus en entretien.",
},

# ============ F. QUALITÉ & GOUVERNANCE ============
"great_expectations": {
    "label": "Great Expectations",
    "definition": "Une bibliothèque Python qui permet de définir, exécuter et documenter des règles de validation de données ('expectations'), avec des rapports de conformité automatiques.",
    "importance": "C'est l'outil qui implémente les Data Quality Gates d'Argus entre les zones Bronze et Silver.",
    "reason": "Il rend les contrôles qualité explicites, versionnés et documentés plutôt qu'implicites dans du code dispersé — essentiel pour prouver la fiabilité d'une donnée d'audit.",
},
"soda": {
    "label": "Soda",
    "definition": "Un outil de qualité de données qui permet de définir des contrôles ('checks') en langage proche du naturel (SodaCL) et de les intégrer dans des pipelines.",
    "importance": "Alternative à Great Expectations envisagée mais non retenue comme outil principal d'Argus.",
    "reason": "Mentionné pour montrer la connaissance des deux options dominantes du marché de la qualité de données.",
},
"openlineage": {
    "label": "OpenLineage",
    "definition": "Un standard ouvert et une spécification d'API pour capturer automatiquement le lineage des données depuis différents outils (Airflow, Spark, dbt).",
    "importance": "Argus l'intègre à Airflow, Spark et dbt pour construire automatiquement le graphe de traçabilité de bout en bout (Epic E7).",
    "reason": "Un standard ouvert évite de dépendre d'un seul outil de catalogue et reste portable si l'outil de gouvernance change un jour.",
},
"openmetadata": {
    "label": "OpenMetadata",
    "definition": "Une plateforme open source de catalogue de données, de gouvernance et de gestion de la qualité, qui consomme notamment les événements OpenLineage.",
    "importance": "C'est le catalogue retenu pour Argus (ADR-0003), qui centralise la documentation, la classification de sensibilité et le lineage.",
    "reason": "Il est plus simple à opérer seul que DataHub (moins de dépendances lourdes) tout en offrant une intégration OpenLineage de premier ordre — un choix pragmatique pour un projet solo.",
},
"datahub": {
    "label": "DataHub",
    "definition": "Une plateforme open source de catalogue de données créée par LinkedIn, très largement adoptée dans les grandes entreprises technologiques, mais avec une architecture d'exploitation plus lourde.",
    "importance": "Étudiée comme alternative à OpenMetadata (ADR-0003) mais non retenue pour Argus.",
    "reason": "Mentionnée pour documenter le compromis fait (simplicité d'exploitation solo vs adoption enterprise plus large), un vrai point de discussion en entretien.",
},
"rgpd": {
    "label": "RGPD (Règlement Général sur la Protection des Données)",
    "definition": "Le règlement européen qui encadre la collecte, le traitement et la conservation des données à caractère personnel.",
    "importance": "Argus doit identifier et classifier toute donnée personnelle présente dans les jeux de données d'audit (ex. noms d'utilisateurs dans les écritures comptables).",
    "reason": "Un cabinet d'audit traitant des données de multiples pays européens ne peut pas se permettre une non-conformité — c'est une exigence 'by design', pas ajoutée après coup.",
},
"secret_pro": {
    "label": "Secret professionnel",
    "definition": "L'obligation légale et déontologique pour un auditeur de ne jamais divulguer ni mélanger les informations d'une mission client avec celles d'une autre.",
    "importance": "C'est la justification métier directe du cloisonnement multi-tenant et du RBAC dans l'architecture d'Argus.",
    "reason": "Une violation du secret professionnel expose le cabinet à des sanctions et à une perte de confiance client majeure — l'isolation des données par mission est donc non négociable.",
},

# ============ G. EXPOSITION & SERVICE ============
"fastapi": {
    "label": "FastAPI",
    "definition": "Un framework Python moderne pour construire des API web, reconnu pour sa performance, sa validation de données intégrée et sa documentation automatique.",
    "importance": "C'est le framework utilisé pour exposer les résultats d'Argus (marts d'audit, alertes) aux consommateurs via une API REST.",
    "reason": "Il est rapide à développer, performant en production, et génère automatiquement une documentation interactive — un standard très demandé en Python.",
},
"graphql": {
    "label": "GraphQL",
    "definition": "Un langage de requête pour API qui permet au client de demander précisément les champs de données dont il a besoin, en un seul appel, plutôt que de multiplier les appels REST.",
    "importance": "Utilisé dans Argus en complément de l'API REST pour le portail de restitution auditeur (Epic E9), où les besoins d'affichage varient beaucoup d'un écran à l'autre.",
    "reason": "Il évite le sur-chargement ou sous-chargement de données typique des API REST classiques lorsque différents consommateurs (auditeurs, partners) ont des besoins hétérogènes.",
},
"rest_api": {
    "label": "API REST",
    "definition": "Un style d'architecture pour exposer des données et fonctionnalités sur le web, via des ressources identifiées par des URL et manipulées avec les verbes HTTP standards.",
    "importance": "C'est le mode d'exposition principal des données d'Argus vers les consommateurs externes (portail, intégrations).",
    "reason": "C'est le standard le plus universellement compris et outillé pour exposer des services, complété par GraphQL là où la flexibilité de requête est nécessaire.",
},
"bi": {
    "label": "BI (Business Intelligence)",
    "definition": "L'ensemble des outils et pratiques qui transforment des données en tableaux de bord et rapports exploitables par des utilisateurs métier non techniques.",
    "importance": "Les Associés responsables de mission d'Argus consultent des tableaux de bord BI construits à partir des marts Gold.",
    "reason": "Les décideurs métier ont besoin d'une restitution visuelle immédiate, sans écrire de requêtes eux-mêmes.",
},

# ============ H. INFRASTRUCTURE & DEVOPS ============
"docker": {
    "label": "Docker",
    "definition": "Une technologie de conteneurisation qui permet d'empaqueter une application avec toutes ses dépendances dans une unité isolée et portable, exécutable de façon identique partout.",
    "importance": "Chaque composant d'Argus (Kafka, Spark, Airflow, bases de données...) tourne dans un conteneur Docker.",
    "reason": "Il garantit un environnement de développement reproductible, identique entre le poste local et le déploiement cloud, et évite les conflits de dépendances entre outils.",
},
"docker_compose": {
    "label": "Docker Compose",
    "definition": "Un outil qui permet de définir et lancer, avec un seul fichier de configuration, une application composée de plusieurs conteneurs Docker liés entre eux.",
    "importance": "C'est l'outil utilisé pour l'environnement de développement local d'Argus, structuré en profils par sprint (voir guide d'environnement local).",
    "reason": "Il simplifie radicalement le démarrage d'une stack multi-services complexe, avec une seule commande, adaptée à un poste de développement aux ressources limitées.",
},
"kubernetes": {
    "label": "Kubernetes",
    "definition": "Une plateforme d'orchestration de conteneurs qui automatise leur déploiement, leur mise à l'échelle et leur gestion sur un cluster de machines.",
    "importance": "C'est la cible de déploiement 'production' d'Argus (Epic E11), sur un cluster k3s hébergé gratuitement (ADR-0005).",
    "reason": "Il apporte l'élasticité nécessaire pour absorber les pics de charge de la 'busy season' d'audit, sans surdimensionner l'infrastructure en permanence.",
},
"k3s": {
    "label": "k3s",
    "definition": "Une distribution légère de Kubernetes, empaquetée en un seul binaire, conçue pour les environnements aux ressources limitées.",
    "importance": "C'est la distribution Kubernetes installée sur l'instance Oracle Cloud gratuite d'Argus (ADR-0005).",
    "reason": "Elle permet d'opérer un vrai cluster Kubernetes sans les coûts d'un service managé (EKS/GKE) ni la lourdeur d'une distribution complète, tout en restant pédagogiquement proche d'un vrai Kubernetes.",
},
"terraform": {
    "label": "Terraform",
    "definition": "Un outil d'Infrastructure as Code qui permet de décrire l'infrastructure cloud souhaitée dans des fichiers de configuration, puis de la provisionner et la faire évoluer de façon automatisée et reproductible.",
    "importance": "Argus l'utilise pour provisionner l'instance Oracle Cloud et le cluster k3s (Epic E11, ADR-0005).",
    "reason": "Il évite le provisionnement manuel sujet à erreurs, rend l'infrastructure versionnée comme du code, et documente exactement ce qui est déployé.",
},
"iac": {
    "label": "Infrastructure as Code (IaC)",
    "definition": "La pratique consistant à gérer et provisionner l'infrastructure informatique via des fichiers de configuration versionnés plutôt que par des actions manuelles.",
    "importance": "C'est le principe général derrière l'usage de Terraform dans Argus.",
    "reason": "Elle rend l'infrastructure reproductible, traçable (via Git) et revuable comme n'importe quel autre changement de code.",
},
"github_actions": {
    "label": "GitHub Actions",
    "definition": "Le service d'intégration et de déploiement continu intégré à GitHub, qui permet d'automatiser des workflows (tests, build, déploiement) déclenchés par des événements du dépôt.",
    "importance": "C'est le moteur de CI/CD d'Argus : chaque Pull Request y déclenche les tests et vérifications avant fusion.",
    "reason": "Gratuit et illimité sur un dépôt public, il évite de dépendre d'un service de CI/CD tiers payant, tout en étant un standard largement utilisé en entreprise.",
},
"cicd": {
    "label": "CI/CD (Intégration et Déploiement Continus)",
    "definition": "Un ensemble de pratiques qui automatisent la vérification (tests, lint) et la mise en production du code à chaque changement, plutôt que par des livraisons manuelles ponctuelles.",
    "importance": "Chaque contribution à Argus passe par un pipeline CI/CD avant d'être considérée comme terminée (Definition of Done).",
    "reason": "Elle détecte les régressions tôt, accélère les cycles de livraison et fait partie des standards non négociables d'une plateforme de niveau entreprise.",
},
"prometheus": {
    "label": "Prometheus",
    "definition": "Un système de collecte et de stockage de métriques temporelles, qui interroge périodiquement les services surveillés pour en récupérer l'état.",
    "importance": "Argus l'utilise pour collecter les métriques techniques (latence des pipelines, débit Kafka, santé des services) et métier (Epic E10).",
    "reason": "Sans observabilité, impossible de détecter une dégradation de performance ou une panne avant qu'elle n'affecte les auditeurs utilisateurs.",
},
"grafana": {
    "label": "Grafana",
    "definition": "Un outil de visualisation qui construit des tableaux de bord interactifs à partir de sources de métriques comme Prometheus.",
    "importance": "Argus l'utilise pour visualiser en direct la santé de la plateforme (Epic E10), démontré en Sprint Review.",
    "reason": "Il transforme des métriques brutes difficiles à interpréter en tableaux de bord lisibles par l'équipe et les parties prenantes.",
},
"wsl2": {
    "label": "WSL2 (Windows Subsystem for Linux 2)",
    "definition": "Une couche de compatibilité de Windows qui exécute un vrai noyau Linux, permettant de faire tourner des outils Linux/Docker nativement sous Windows avec de bonnes performances.",
    "importance": "C'est le backend recommandé pour Docker Desktop sur le poste de développement d'Argus.",
    "reason": "Il consomme moins de ressources et offre de meilleures performances I/O que l'ancien backend Hyper-V, un point important sur une machine à 16 Go de RAM.",
},
"observability": {
    "label": "Observabilité",
    "definition": "La capacité à comprendre l'état interne d'un système à partir de ses signaux externes (métriques, logs, traces), pour détecter et diagnostiquer les problèmes.",
    "importance": "C'est l'objectif de l'Epic E10 d'Argus, porté par Prometheus et Grafana.",
    "reason": "Une plateforme utilisée pour des missions d'audit doit prouver sa fiabilité (SLA/SLO) — cela commence par pouvoir mesurer objectivement son propre comportement.",
},

# ============ I. REQUÊTAGE ============
"trino": {
    "label": "Trino",
    "definition": "Un moteur de requêtage SQL distribué, capable d'interroger de très grands volumes de données stockées dans un lakehouse, avec une architecture coordinateur/workers.",
    "importance": "Envisagé comme moteur de requêtage optionnel d'Argus, testé sur le cluster cloud (ADR-0006), en complément de DuckDB.",
    "reason": "Il est très demandé pour les architectures lakehouse à grande échelle, mais son empreinte mémoire est trop lourde pour un usage quotidien sur le poste de développement — d'où son usage limité à un spike cloud.",
},
"duckdb": {
    "label": "DuckDB",
    "definition": "Un moteur de requêtage SQL analytique 'in-process' (sans serveur séparé), qui s'exécute directement dans l'application qui l'utilise, avec une empreinte mémoire minimale.",
    "importance": "C'est le moteur de requêtage interactif principal d'Argus (ADR-0006), utilisé au quotidien en développement local.",
    "reason": "Il ne nécessite aucune infrastructure à maintenir et démarre instantanément, ce qui est décisif sur un poste de développement à ressources limitées (16 Go de RAM).",
},

# ============ J. AGILE / SCRUM ============
"scrum": {
    "label": "Scrum",
    "definition": "Un cadre de travail Agile itératif, organisé en cycles courts (Sprints), avec des rôles, des cérémonies et des artefacts définis pour livrer de la valeur régulièrement.",
    "importance": "C'est le mode de fonctionnement adopté pour l'ensemble du projet Argus, y compris en configuration solo.",
    "reason": "Il structure le travail en incréments courts et démontrables, ce qui correspond à l'attente de la direction fictive de Véridien (voir 02-entreprise-fictive-veridian.md) et aux pratiques réelles des grandes entreprises.",
},
"product_vision": {
    "label": "Product Vision",
    "definition": "Un énoncé synthétique qui décrit la raison d'être d'un produit : pour qui il existe, quel problème il résout, et ce qui le distingue des alternatives.",
    "importance": "Elle cadre toutes les décisions de priorisation d'Argus tout au long du projet (voir `product-vision.md`).",
    "reason": "Sans vision partagée, chaque décision de backlog risquerait d'être arbitraire plutôt qu'alignée sur un objectif métier commun.",
},
"product_backlog": {
    "label": "Product Backlog",
    "definition": "La liste priorisée et évolutive de tout ce qui reste à faire sur un produit (fonctionnalités, corrections, dette technique), maintenue par le Product Owner.",
    "importance": "Il centralise les Epics et User Stories d'Argus, mis à jour à chaque Sprint Planning.",
    "reason": "C'est l'outil qui rend visible, à tout moment, ce qui a de la valeur et ce qui est prioritaire, plutôt que de travailler sur des tâches décidées au fil de l'eau.",
},
"epic": {
    "label": "Epic",
    "definition": "Un ensemble de travail trop volumineux pour être livré en un seul Sprint, regroupant plusieurs User Stories autour d'un même objectif fonctionnel.",
    "importance": "Argus est structuré en 12 Epics (E1 à E12), chacun correspondant à un grand domaine fonctionnel de la plateforme.",
    "reason": "Découper le projet en Epics permet de raisonner à un niveau macro pour la planification, avant de le détailler en User Stories exécutables sprint par sprint.",
},
"user_story": {
    "label": "User Story",
    "definition": "Une description courte d'un besoin fonctionnel formulée du point de vue de l'utilisateur, au format 'En tant que... je veux... afin de...'.",
    "importance": "Chaque tâche confiée pendant les Sprints d'Argus est formulée comme une User Story, avec ses critères d'acceptation.",
    "reason": "Ce format garde le focus sur la valeur métier ('pourquoi') plutôt que sur la seule tâche technique ('quoi'), ce qui évite de développer des fonctionnalités déconnectées d'un besoin réel.",
},
"story_points": {
    "label": "Story Points",
    "definition": "Une unité relative (souvent en suite de Fibonacci) utilisée pour estimer la complexité et l'effort d'une User Story, indépendamment du temps en heures.",
    "importance": "Utilisés pour dimensionner le Sprint Backlog d'Argus à chaque Sprint Planning.",
    "reason": "L'estimation relative est plus fiable qu'une estimation en heures pour une équipe (même solo) qui découvre de nouvelles technologies, car elle se calibre sur l'expérience acquise sprint après sprint.",
},
"sprint": {
    "label": "Sprint",
    "definition": "Un cycle de travail court et à durée fixe (ici 2 semaines) au terme duquel une valeur démontrable doit être livrée.",
    "importance": "Toute la roadmap d'Argus est découpée en Sprints, chacun avec un objectif clair (Sprint Goal).",
    "reason": "Le rythme court force à livrer des incréments concrets régulièrement plutôt que de risquer un grand projet livré en bloc, tardivement, avec un retour utilisateur tardif.",
},
"sprint_planning": {
    "label": "Sprint Planning",
    "definition": "La cérémonie de début de Sprint où l'équipe sélectionne les User Stories du Product Backlog à réaliser, et définit le Sprint Goal.",
    "importance": "Chaque Sprint d'Argus démarre par cette cérémonie simulée entre le Tech Lead et le Data Engineer.",
    "reason": "Elle garantit que chaque Sprint a un objectif clair et un périmètre de travail explicitement négocié, plutôt qu'implicite.",
},
"sprint_goal": {
    "label": "Sprint Goal",
    "definition": "Un objectif unique et clair qui résume ce que le Sprint doit accomplir, au-delà de la simple liste des tâches.",
    "importance": "Chaque Sprint d'Argus est ancré à un Sprint Goal explicite (voir la roadmap dans `05-plan-de-travail.md`).",
    "reason": "Il donne un sens commun au travail du Sprint, utile pour arbitrer les priorités si tout ne peut pas être fait.",
},
"sprint_backlog": {
    "label": "Sprint Backlog",
    "definition": "Le sous-ensemble du Product Backlog sélectionné pour le Sprint en cours, avec le plan nécessaire pour l'accomplir.",
    "importance": "Défini à chaque Sprint Planning d'Argus à partir du Product Backlog global.",
    "reason": "Il rend visible et engageant le périmètre exact du Sprint en cours, évitant l'ambiguïté sur ce qui est prévu ou non.",
},
"daily_scrum": {
    "label": "Daily Scrum",
    "definition": "Un point de synchronisation court et régulier (traditionnellement quotidien) où chacun partage ce qui est fait, en cours, et les blocages.",
    "importance": "Simulé à chaque reprise de session pendant un Sprint actif d'Argus (voir `03-organisation-agile.md`).",
    "reason": "Il permet de détecter tôt les blocages plutôt qu'à la fin du Sprint, quand il est trop tard pour ajuster.",
},
"sprint_review": {
    "label": "Sprint Review",
    "definition": "La cérémonie de fin de Sprint où le travail réalisé est démontré aux parties prenantes, qui donnent leur retour.",
    "importance": "Chaque Sprint d'Argus se termine par une démonstration concrète (voir les scénarios de démo dans `05-plan-de-travail.md`).",
    "reason": "Elle force à livrer quelque chose de réellement démontrable, pas seulement 'du code écrit', et recueille un feedback tôt.",
},
"sprint_retro": {
    "label": "Sprint Retrospective",
    "definition": "La cérémonie de fin de Sprint où l'équipe (ici, toi et moi) revient sur ce qui a bien fonctionné, moins bien fonctionné, et les actions d'amélioration à mener.",
    "importance": "Elle clôture chaque Sprint d'Argus, avec un rappel explicite des compétences acquises.",
    "reason": "Elle transforme l'expérience de chaque Sprint en amélioration continue du fonctionnement, plutôt que de répéter les mêmes erreurs.",
},
"dod": {
    "label": "Definition of Done (DoD)",
    "definition": "La liste de critères objectifs qu'une User Story ou un Sprint doit remplir pour être considéré comme réellement terminé (code revu, testé, documenté, démontrable...).",
    "importance": "Argus a une DoD explicite (voir `05-plan-de-travail.md` section 14), appliquée à chaque livrable.",
    "reason": "Elle évite le flou sur ce que signifie 'terminé', un point de désaccord fréquent en développement logiciel.",
},
"adr": {
    "label": "ADR (Architecture Decision Record)",
    "definition": "Un document court et structuré qui capture une décision d'architecture, son contexte, les options considérées et la justification du choix retenu.",
    "importance": "Toutes les décisions techniques majeures d'Argus sont documentées en ADR (dossier `docs/adr/`).",
    "reason": "Il permet à toute personne rejoignant le projet, ou à toi-même dans six mois, de comprendre pourquoi une décision a été prise, pas seulement ce qui a été décidé.",
},
"pull_request": {
    "label": "Pull Request",
    "definition": "Une proposition de modification du code, soumise pour revue avant d'être fusionnée dans la branche principale du dépôt.",
    "importance": "Chaque contribution à Argus passe par une Pull Request, même en projet solo, pour simuler le processus réel d'une équipe.",
    "reason": "Elle impose une étape de relecture et de validation avant toute intégration, réduisant le risque de régression.",
},
"code_review": {
    "label": "Code Review (revue de code)",
    "definition": "L'examen critique du code d'une Pull Request par une autre personne (ici, le mentor simulé), avant sa fusion.",
    "importance": "Chaque Pull Request d'Argus fait l'objet d'une revue simulée avec commentaires et demandes de changement.",
    "reason": "Elle détecte les erreurs, transmet les bonnes pratiques et garantit une cohérence de style et de qualité à travers le projet.",
},
"release_notes": {
    "label": "Release Notes",
    "definition": "Un document qui liste, de façon lisible, les changements livrés à chaque version ou Sprint d'un produit.",
    "importance": "Mises à jour à chaque Sprint d'Argus pour tracer l'évolution du produit.",
    "reason": "Elles donnent une vue d'ensemble rapide de ce qui a changé, utile pour toi-même en rétrospective et pour un futur recruteur qui consulterait le dépôt.",
},
"tribu_squad": {
    "label": "Entité / Équipe",
    "definition": "Un modèle d'organisation où le Pôle est structuré en plusieurs 'entités', chacune responsable d'un périmètre produit précis et elle-même composée de plusieurs 'équipes' autonomes. Ce modèle s'inspire de l'organisation par 'Tribus/Squads' popularisée par Spotify, ici renommée en français ('entité'/'équipe') pour la cohérence terminologique du projet.",
    "importance": "Argus est porté par l'entité Technologie Audit & Confiance de Véridien, elle-même composée de 5 équipes (voir `03-organisation-agile.md`).",
    "reason": "Ce modèle illustre une organisation moderne réelle des grandes entreprises tech et de conseil, et structure les rôles que tu occuperas tour à tour selon le Sprint.",
},

# ============ K. CONCEPTS MÉTIER AUDIT / RISQUE ============
"audit_continu": {
    "label": "Audit continu (Continuous Auditing)",
    "definition": "Une approche d'audit qui analyse les données financières en continu tout au long de l'année, plutôt qu'uniquement lors d'une revue annuelle ponctuelle.",
    "importance": "C'est la promesse centrale d'Argus, portée par la combinaison batch (grand livre) et streaming (transactions).",
    "reason": "Elle permet de détecter une anomalie significative en quasi temps réel plutôt que plusieurs mois après les faits, lors de la seule clôture annuelle.",
},
"isa315": {
    "label": "ISA 315 (révisée)",
    "definition": "Une norme internationale d'audit qui définit comment l'auditeur doit identifier et évaluer les risques d'anomalies significatives, avec une attention renforcée à l'usage des systèmes d'information.",
    "importance": "C'est une des pressions réglementaires qui justifie l'existence même du projet Argus chez Véridien.",
    "reason": "Elle pousse explicitement les cabinets à documenter leur usage des données et des systèmes du client, ce qu'une plateforme comme Argus permet de prouver.",
},
"regulateurs": {
    "label": "PCAOB / H3C (régulateurs de l'audit)",
    "definition": "Des autorités de supervision de la profession d'audit (PCAOB aux États-Unis, H3C en France) qui fixent des exigences et contrôlent la qualité des audits réalisés.",
    "importance": "Ils représentent, dans le scénario fictif de Véridien, la pression externe qui exige une traçabilité et une qualité renforcées des analyses d'audit.",
    "reason": "Mentionnés pour ancrer le projet dans une réalité réglementaire crédible, justifiant les exigences de lineage et de qualité de données d'Argus.",
},
"benford": {
    "label": "Loi de Benford",
    "definition": "Une loi statistique empirique qui prédit la fréquence attendue du premier chiffre significatif dans des ensembles de données naturelles ; un écart important à cette loi peut signaler une manipulation.",
    "importance": "Utilisée dans Argus (Epic E8) comme un des indicateurs de détection d'anomalies sur les montants comptables.",
    "reason": "C'est une technique reconnue et peu coûteuse en calcul pour prioriser les comptes à investiguer en priorité, sans nécessiter de modèle ML complexe.",
},
"sod": {
    "label": "Séparation des tâches (Segregation of Duties)",
    "definition": "Un principe de contrôle interne qui exige qu'aucune personne seule ne puisse initier, valider et enregistrer une même transaction, afin de limiter les risques de fraude ou d'erreur.",
    "importance": "Argus vérifie automatiquement le respect de ce principe dans les écritures comptables analysées (Epic E4/E8).",
    "reason": "Un contournement de séparation des tâches est un signal classique de fraude potentielle, une des anomalies prioritaires que les auditeurs cherchent à détecter.",
},
"kyc": {
    "label": "KYC (Know Your Customer)",
    "definition": "Un ensemble de procédures réglementaires visant à vérifier l'identité des clients d'une institution financière avant d'entrer en relation d'affaires.",
    "importance": "Mentionné dans le cadre du projet alternatif Sentinel (Projet B) et de l'Epic bonus E13, non développé dans le périmètre ferme d'Argus.",
    "reason": "Cité pour situer Argus par rapport aux enjeux voisins de conformité financière, dont il s'inspire partiellement pour son Epic d'extension.",
},
"aml": {
    "label": "AML (Anti-Money Laundering / Lutte anti-blanchiment)",
    "definition": "L'ensemble des réglementations et dispositifs visant à détecter et prévenir le blanchiment d'argent à travers les circuits financiers.",
    "importance": "Cœur du projet alternatif Sentinel (Projet B) et de l'Epic bonus E13 d'extension d'Argus (backlog d'extensions futures).",
    "reason": "Mentionné pour montrer la proximité entre détection d'anomalies comptables (Argus) et détection de transactions suspectes (AML), un axe d'extension naturel du projet.",
},
"forensic": {
    "label": "Forensic (audit judiciaire / investigation)",
    "definition": "Une pratique d'audit spécialisée dans l'investigation de fraudes ou d'irrégularités, souvent utilisée en support de procédures judiciaires ou disciplinaires.",
    "importance": "C'est un des consommateurs potentiels des résultats de détection d'anomalies d'Argus.",
    "reason": "Mentionné pour illustrer un des métiers réels de la Métier Gestion des Risques qui bénéficierait des capacités d'Argus.",
},
"engagement_partner": {
    "label": "Associé responsable de mission",
    "definition": "L'associé responsable d'une mission d'audit chez un client donné, qui en porte la responsabilité finale et signe l'opinion d'audit.",
    "importance": "C'est une partie prenante clé d'Argus, consommatrice des tableaux de bord exécutifs par mission.",
    "reason": "Ses attentes (fiabilité, rapidité, défendabilité des résultats) orientent directement les priorités du Product Backlog.",
},
"journal_entry": {
    "label": "Écriture comptable / Grand livre (Journal Entry)",
    "definition": "Un enregistrement comptable élémentaire (débit/crédit sur un compte, à une date, pour un montant) ; le grand livre est l'ensemble de ces écritures sur une période.",
    "importance": "C'est la donnée métier centrale ingérée en batch par Argus (Epic E1) depuis les ERP clients.",
    "reason": "C'est l'unité d'analyse de base de tout audit financier moderne — sa maîtrise technique est indispensable pour crédibiliser le projet.",
},
"erp": {
    "label": "ERP (Enterprise Resource Planning)",
    "definition": "Un logiciel de gestion intégré (ex. SAP, Oracle EBS, Dynamics 365) qui centralise les processus d'une entreprise, dont la comptabilité.",
    "importance": "Les ERP des clients audités sont les systèmes sources qu'Argus doit ingérer, avec des formats d'export hétérogènes.",
    "reason": "Gérer cette hétérogénéité de sources est une contrainte réelle et incontournable du métier de l'audit multi-clients.",
},

# ============ L. ML / SÉCURITÉ ============
"isolation_forest": {
    "label": "Isolation Forest",
    "definition": "Un algorithme de détection d'anomalies non supervisé qui isole les observations atypiques en les séparant plus rapidement que les observations normales via des partitionnements aléatoires successifs.",
    "importance": "Utilisé dans Argus (Epic E8) pour détecter des écritures comptables statistiquement atypiques sans étiquette préalable.",
    "reason": "Il ne nécessite pas de données déjà labellisées comme frauduleuses (rares en pratique), contrairement à un modèle supervisé classique.",
},
"anomaly_scoring": {
    "label": "Scoring d'anomalie",
    "definition": "L'attribution d'un score numérique à chaque transaction ou écriture, reflétant sa probabilité d'être anormale, afin de prioriser les investigations.",
    "importance": "C'est le résultat final produit par le pipeline de détection d'Argus (Epic E8), consommé ensuite par l'API et les alertes.",
    "reason": "Un score continu permet de prioriser l'attention des auditeurs plutôt que de leur fournir une liste binaire suspecte/non-suspecte, souvent trop grossière.",
},
"encryption": {
    "label": "Chiffrement (TLS / au repos)",
    "definition": "La transformation de données pour les rendre illisibles sans une clé de déchiffrement, appliquée aux données en transit (TLS) et/ou stockées (au repos).",
    "importance": "Argus chiffre les données en transit entre tous ses services et au repos dans MinIO/PostgreSQL/Cassandra (Epic E12).",
    "reason": "C'est une exigence de sécurité de base pour des données financières sensibles, renforcée par le contexte de secret professionnel.",
},
"jvm_heap": {
    "label": "Mémoire JVM (Heap)",
    "definition": "La zone de mémoire allouée à une application tournant sur la machine virtuelle Java (JVM — utilisée par Kafka, Cassandra, Elasticsearch, Spark), dont la taille se configure explicitement.",
    "importance": "Chaque service basé sur la JVM dans Argus a une taille de heap volontairement réduite pour tenir sur le poste de développement (voir `06-guide-environnement-local.md`).",
    "reason": "Une JVM non configurée réserve souvent plus de mémoire que nécessaire par défaut ; la contrainte des 16 Go de RAM impose de la plafonner explicitement pour chaque service.",
},
}

DOC_TERMS = {
"docs/00-analyse-marche-besoins.md": [
    "audit_continu","isa315","regulateurs","testing_100","streaming","batch",
    "dq_gate","lineage","data_catalog","rgpd","secret_pro","multi_tenant",
    "erp","kubernetes","spark","kafka",
],
"docs/01-selection-projet.md": [
    "spark","kafka","dbt","iceberg","minio","trino","duckdb","openmetadata",
    "openlineage","fastapi","graphql","airflow","kubernetes","multi_tenant",
    "data_mesh","cdc","aml","kyc","forensic","anomaly_scoring","benford",
    "cassandra","elasticsearch",
],
"docs/02-entreprise-fictive-veridian.md": [
    "erp","rgpd","secret_pro","isa315","regulateurs","multi_tenant","rbac",
    "encryption","kubernetes","terraform","dq_gate","lineage","data_catalog",
    "engagement_partner","journal_entry",
],
"docs/03-organisation-agile.md": [
    "tribu_squad","kafka","kafka_connect","schema_registry_concept","spark",
    "minio","iceberg","trino","duckdb","airflow","great_expectations",
    "openlineage","openmetadata","dbt","fastapi","graphql","docker",
    "kubernetes","terraform","github_actions","prometheus","grafana",
    "sprint_planning","daily_scrum","sprint_review","sprint_retro",
    "code_review","pull_request","product_backlog","engagement_partner",
],
"docs/04-architecture-globale.md": [
    "medallion","lambda_architecture","airflow","kafka","kafka_connect",
    "schema_registry_concept","minio","iceberg","parquet","spark","pyspark",
    "trino","duckdb","dbt","great_expectations","postgresql","cassandra",
    "elasticsearch","openmetadata","openlineage","fastapi","graphql",
    "docker","docker_compose","kubernetes","terraform","github_actions",
    "prometheus","grafana","multi_tenant","rbac","encryption","adr",
    "avro","cdc","data_lake","lakehouse","data_warehouse","data_vault",
    "kimball","time_travel","schema_evolution","rest_catalog","dag",
],
"docs/05-plan-de-travail.md": [
    "epic","user_story","story_points","sprint","sprint_goal","dod",
    "sprint_review","product_backlog","erp","journal_entry","benford",
    "isolation_forest","anomaly_scoring","duckdb","trino","dagster",
    "delta_lake","kafka","spark","dbt","iceberg","airflow","openmetadata",
    "openlineage","fastapi","graphql","kubernetes","terraform","prometheus",
    "grafana","rgpd","multi_tenant","aml","testing_100",
],
"docs/06-guide-environnement-local.md": [
    "wsl2","docker_compose","kafka","cassandra","elasticsearch","spark",
    "openmetadata","jvm_heap","k3s","terraform","trino","duckdb","docker",
    "iceberg","minio","airflow",
],
"docs/adr/0001-orchestrateur-airflow.md": [
    "airflow","dagster","dag","openlineage","adr","dbt","kafka","spark",
],
"docs/adr/0002-format-table-lakehouse-iceberg.md": [
    "iceberg","delta_lake","spark","trino","duckdb","time_travel",
    "schema_evolution","partitioning","rest_catalog","parquet","adr",
    "openmetadata","dbt",
],
"docs/adr/0003-catalogue-lineage-openmetadata.md": [
    "openmetadata","datahub","openlineage","data_catalog","lineage",
    "rgpd","secret_pro","adr","airflow","spark","dbt",
],
"docs/adr/0004-streaming-backbone-kafka.md": [
    "kafka","kafka_connect","schema_registry_concept","avro",
    "schema_evolution","cassandra","elasticsearch","adr",
],
"docs/adr/0005-hebergement-cloud-oracle-k3s.md": [
    "kubernetes","terraform","k3s","iac","adr","docker_compose",
],
"docs/adr/0006-moteur-requetage-duckdb.md": [
    "duckdb","trino","dbt","iceberg","jvm_heap","adr","kubernetes",
],
"docs/product-vision.md": [
    "product_vision","rgpd","isa315","multi_tenant","testing_100",
    "audit_continu","lineage",
],
"docs/product-backlog.md": [
    "product_backlog","epic","user_story","story_points","sprint_planning",
    "sprint",
],
}

def render_lexicon(doc_key):
    term_keys = DOC_TERMS[doc_key]
    lines = []
    lines.append("\n\n---\n")
    lines.append("\n## Lexique des termes utilisés dans ce document\n")
    lines.append(
        "\n*Pour chaque terme technique, technologique, méthodologique ou métier "
        "mentionné ci-dessus : une courte définition, son importance dans le "
        "projet Argus, et la raison pour laquelle il est utilisé.*\n"
    )
    for key in term_keys:
        t = TERMS[key]
        lines.append(f"\n### {t['label']}\n")
        lines.append(f"\n**Définition** : {t['definition']}\n")
        lines.append(f"\n**Importance dans Argus** : {t['importance']}\n")
        lines.append(f"\n**Pourquoi ce choix** : {t['reason']}\n")
    return "".join(lines)

def main():
    missing = []
    for doc, keys in DOC_TERMS.items():
        for k in keys:
            if k not in TERMS:
                missing.append((doc, k))
    if missing:
        raise SystemExit(f"Termes manquants dans TERMS: {missing}")

    for doc_key in DOC_TERMS:
        path = doc_key
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Remove any previously injected lexicon (idempotent re-run)
        content = re.split(r"\n---\n\n## Lexique des termes utilisés dans ce document\n", content)[0]
        content = content.rstrip("\n") + "\n"
        content += render_lexicon(doc_key)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"OK  {doc_key}  (+{len(DOC_TERMS[doc_key])} termes)")

if __name__ == "__main__":
    main()
