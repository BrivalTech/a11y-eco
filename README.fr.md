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
```

Les rapports sont rédigés en français ou en anglais. La langue est prise dans `--lang`,
sinon dans la langue du système (`LANG`, `LC_ALL`…), et le français est utilisé par défaut.

| Code de sortie | Signification                                                           |
|----------------|-------------------------------------------------------------------------|
| `0`            | Aucun problème n'atteint la sévérité `--fail-on` (par défaut : `error`) |
| `1`            | Au moins un problème l'atteint                                          |
| `2`            | Arguments invalides, ou page impossible à charger                       |

Les couleurs ne sont utilisées que dans un terminal interactif, et jamais quand `NO_COLOR` est définie.

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

- Seul le HTML envoyé par le serveur est lu : aucun JavaScript n'est exécuté, et les
  feuilles de style et les scripts ne sont pas téléchargés.
- Les nombres de requêtes et de ressources sont donc des **valeurs minimales**. Une règle
  d'éco-conception ne signale un problème que si ce minimum dépasse déjà le seuil de la
  bonne pratique : une page qui la respecte n'est jamais signalée, mais certains problèmes
  ne sont pas détectés.
- La plupart des bonnes pratiques du RWEB portent sur la conception, les serveurs ou les
  contenus, et ne peuvent pas être vérifiées à partir du HTML. Il en va de même pour la
  plupart des critères du RGAA. Un audit automatique ne remplace jamais un audit manuel.

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
