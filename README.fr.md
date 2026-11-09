# a11y-eco

[![CI](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml/badge.svg)](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml)

🇬🇧 [Read in English](README.md)

Audit d'**accessibilité** et d'**éco-conception** d'une page web, en ligne de commande,
**sans aucune dépendance** à l'exécution.

> **Statut : pré-alpha.** Le projet est en cours de développement, sprint après sprint.
> Rien n'est encore publié sur PyPI.

## Objectifs

- Détecter les défauts d'accessibilité les plus fréquents dans le HTML statique : alternatives
  d'images manquantes, hiérarchie des titres incorrecte, langue de la page absente, liens et
  boutons sans nom accessible. Chaque règle renvoie au critère
  [RGAA](https://accessibilite.numerique.gouv.fr/) correspondant.
- Fournir des indicateurs d'éco-conception : poids de la page, nombre de ressources et
  vérifications inspirées des
  [115 bonnes pratiques d'écoconception web](https://github.com/cnumr/best-practices).
- Produire des rapports en console, en JSON (pour la CI et l'outillage) ou sous forme de page
  HTML autonome.
- Fonctionner en français ou en anglais.

## Hors périmètre

- Le rendu JavaScript : seul le HTML envoyé par le serveur est analysé.
- Un audit RGAA complet : les vérifications automatiques couvrent une petite partie des critères
  et ne remplacent jamais un audit manuel.

## Utilisation

```sh
a11y-eco audit page.html                 # un fichier local
a11y-eco audit https://example.com       # une page web
a11y-eco audit page.html --fail-on warning
```

| Code de sortie | Signification                                                           |
|----------------|-------------------------------------------------------------------------|
| `0`            | Aucun problème n'atteint la sévérité `--fail-on` (par défaut : `error`) |
| `1`            | Au moins un problème l'atteint                                          |
| `2`            | Arguments invalides, ou page impossible à charger                       |

Les couleurs ne sont utilisées que dans un terminal interactif, et jamais quand `NO_COLOR` est définie.

## Développement

Nécessite Python 3.12 ou plus récent et pip 25.1 ou plus récent.

```sh
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --group dev -e .
pre-commit install                 # lint, formatage et typage avant chaque commit

python -m pytest --cov             # tests et couverture
ruff check . && ruff format .      # lint et formatage
a11y-eco --version
```

## Licence

[MIT](LICENSE)
