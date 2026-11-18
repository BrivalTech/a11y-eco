# a11y-eco

[![CI](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml/badge.svg)](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml)

🇬🇧 [Read in English](README.md)

Audit d'**accessibilité** et d'**éco-conception** d'une page web, en ligne de commande,
**sans aucune dépendance** à l'exécution.

> **Statut : alpha.** Les règles et le format JSON peuvent encore évoluer avant la 1.0.

## Installation

Nécessite Python 3.12 ou plus récent. a11y-eco n'a aucune dépendance.

```sh
pipx install a11y-eco        # recommandé pour un outil en ligne de commande
python -m pip install a11y-eco
```

Sur macOS, la commande `python3` fournie par le système peut être trop ancienne.
Installez un Python récent (depuis [python.org](https://www.python.org/downloads/) ou
Homebrew), puis indiquez à pipx lequel utiliser :

```sh
pipx install --python python3.12 a11y-eco
```

## Objectifs

- Détecter les défauts d'accessibilité les plus fréquents dans le HTML statique : alternatives
  d'images manquantes, hiérarchie des titres incorrecte, langue de la page absente, liens et
  boutons sans nom accessible. Chaque règle renvoie au critère
  [RGAA](https://accessibilite.numerique.gouv.fr/) correspondant.
- Fournir des indicateurs d'éco-conception (requêtes, ressources, hôtes, taille du DOM) et
  des vérifications fondées sur le RWEB, le référentiel d'écoconception web (« 115 bonnes
  pratiques »).
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
a11y-eco audit page.html --lang en       # rapport en anglais
a11y-eco audit https://example.com --fetch-resources                     # mesures réseau réelles
a11y-eco audit https://example.com --fetch-resources --include-external  # tiers compris
a11y-eco audit https://example.com --format json                       # pour les programmes
a11y-eco audit https://example.com --format html --output a11y-eco-report.html
```

Les rapports sont rédigés en français ou en anglais. La langue est prise dans `--lang`,
sinon dans la langue du système (`LANG`, `LC_ALL`…), et le français est utilisé par défaut.

| Code de sortie | Signification                                                           |
|----------------|-------------------------------------------------------------------------|
| `0`            | Aucun problème n'atteint la sévérité `--fail-on` (par défaut : `error`) |
| `1`            | Au moins un problème l'atteint                                          |
| `2`            | Arguments invalides, ou page impossible à charger                       |

Les couleurs ne sont utilisées que dans un terminal interactif, et jamais quand `NO_COLOR` est définie.

### Mesures réseau

Par défaut, seul le HTML de la page est téléchargé. Avec `--fetch-resources`, a11y-eco
télécharge aussi de nouveau la page et les fichiers qu'elle charge, 50 au plus, quatre à
la fois, comme un navigateur : en annonçant gzip et Brotli, sans rien décompresser, afin
que les octets comptés soient ceux réellement transférés. Rien n'est exécuté.

Le rapport comporte alors une section séparée « Mesures réseau (valeurs réelles) », et
quatre règles supplémentaires vérifient la compression (`RWEB_0076`), les en-têtes de
cache (`RWEB_0075`), les cookies sur les fichiers statiques (`RWEB_0081`) et les
redirections (`RWEB_0112`).

Les fichiers des autres hôtes (CDN, polices, mesure d'audience, publicité) sont exclus,
sauf avec `--include-external` : les télécharger révèle votre adresse IP à ces tiers. Un
fichier local n'a pas d'hôte : ses adresses relatives ne peuvent pas être téléchargées,
et toutes ses adresses absolues comptent comme d'autres hôtes. Sur un fichier local,
`--fetch-resources` ne mesure donc rien sans `--include-external`.

### Formats de rapport

`--format` choisit le rapport : `console` (par défaut), `json` ou `html`. Les rapports
sont écrits sur la sortie standard, ou dans un fichier UTF-8 avec `--output FICHIER`.
`--fail-on` s'applique quel que soit le format : un job de CI peut garder un rapport et
échouer en une seule commande.

Le **rapport HTML** est une page autonome, sans JavaScript ni fichier externe. Il est
vérifié par a11y-eco lui-même dans la suite de tests, et tout ce qui provient de la page
auditée est échappé.

Le **rapport JSON** est destiné aux programmes. Ses clés sont stables pour une même
`schema_version` :

| Clé | Contenu |
|---|---|
| `schema_version` | Version de la structure, augmentée à chaque changement incompatible |
| `tool` | `name` et `version` d'a11y-eco |
| `language` | Langue des champs `message` (`en` ou `fr`) |
| `page` | `location` (chemin ou URL) et `size` en octets |
| `summary` | Nombre de problèmes `error`, `warning` et `info` |
| `metrics` | Mesures lues dans le HTML (valeurs minimales), ou `null` |
| `network` | Mesures prises avec `--fetch-resources`, avec la liste des `downloads`, ou `null` |
| `findings` | `rule_id`, `severity`, `reference`, `message`, `line`, `column`, `snippet`, `details` |

Seul `message` est traduit. `line` et `column` valent `null` quand un problème n'a pas
de position dans le HTML, et `details` contient des nombres bruts comme `count` et
`limit`. Les en-têtes HTTP ne sont jamais inclus : ils peuvent contenir des cookies de
session.

La liste complète des règles est dans [docs/rules.fr.md](docs/rules.fr.md) (ou avec
`a11y-eco rules`), et le rapport JSON est décrit par un
[JSON Schema](schema/report-v1.schema.json).

## Règles d'éco-conception et crédits

Les règles d'éco-conception renvoient aux bonnes pratiques du **RWEB** (*Référentiel
d'écoconception web*, 5ᵉ édition), par leur identifiant, par exemple `RWEB_0047`. Le RWEB
est publié par GreenIT.fr dans le cadre des travaux du Collectif conception numérique
responsable, selon les termes de la licence
[Creative Commons BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.fr) :
<https://collectif.greenit.fr> · <https://www.ecoconceptionweb.com> ·
<https://rweb.greenit.fr>.

a11y-eco ne reproduit pas le contenu du RWEB : les messages sont rédigés pour l'outil, et
seuls les identifiants des bonnes pratiques et les seuils de leurs règles de validation
sont utilisés.

## Limites d'un audit automatique

- Seul le HTML envoyé par le serveur est lu : aucun JavaScript n'est exécuté. Les
  feuilles de style et les scripts ne sont téléchargés qu'avec `--fetch-resources`, et ne
  sont jamais interprétés : les ressources qu'ils chargent (polices déclarées en CSS,
  fichiers demandés par un script) restent invisibles.
- Les nombres de requêtes et de ressources sont donc des **valeurs minimales**. Une règle
  d'éco-conception ne signale un problème que si ce minimum dépasse déjà le seuil de la
  bonne pratique : une page qui la respecte n'est jamais signalée, mais certains problèmes
  ne sont pas détectés.
- La plupart des bonnes pratiques du RWEB portent sur la conception, les serveurs ou les
  contenus, et ne peuvent pas être vérifiées à partir du HTML. Il en va de même pour la
  plupart des critères du RGAA. Un audit automatique ne remplace jamais un audit manuel.
- Les outils tiers (mesure d'audience, boutons sociaux, carrousels, bibliothèques
  d'animation) sont reconnus d'après une liste d'outils connus : un outil absent de la
  liste n'est pas détecté.
- Les règles réseau ne voient que les réponses des serveurs : les cookies déposés par
  JavaScript ne sont pas détectés, et une chaîne de redirections compte pour une seule.

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

[MIT](https://github.com/brivaltech/a11y-eco/blob/main/LICENSE)
