"""Messages en français."""

from a11y_eco.i18n.catalog import Catalog, PluralForm


def _plural_form(count: int) -> PluralForm:
    # In French, 0 takes the singular: "0 erreur", "1 erreur", "2 erreurs".
    return "one" if count in {0, 1} else "other"


CATALOG = Catalog(
    language="fr",
    plural_form=_plural_form,
    # French groups digits with a narrow non-breaking space: 1 234.
    thousands_separator="\N{NARROW NO-BREAK SPACE}",
    messages={
        # Command line
        "cli.description": "Audite l'accessibilité et l'éco-conception d'une page web.",
        "cli.commands": "commandes",
        "cli.arguments": "arguments",
        "cli.options": "options",
        "cli.help": "affiche cette aide et quitte",
        "cli.version": "affiche le numéro de version et quitte",
        "cli.error": "{prog}\N{NO-BREAK SPACE}: erreur\N{NO-BREAK SPACE}: {message}",
        "cli.not_a_number": "{value!r} n'est pas un nombre",
        "cli.not_positive": "{value!r} doit être supérieur à 0",
        "cli.audit.help": "audite une page web",
        "cli.audit.description": "Audite une page web et affiche les problèmes détectés.",
        "cli.audit.epilog": (
            "code de sortie\N{NO-BREAK SPACE}:\n"
            "  0  aucun problème n'atteint la sévérité de --fail-on\n"
            "  1  au moins un problème atteint la sévérité de --fail-on\n"
            "  2  arguments invalides, ou page impossible à charger\n"
        ),
        "cli.audit.target": "URL (http ou https) ou chemin d'un fichier HTML",
        "cli.audit.fail_on": (
            "sévérité minimale qui fait échouer la commande "
            "(par défaut\N{NO-BREAK SPACE}: %(default)s)"
        ),
        "cli.audit.lang": (
            "langue du rapport (par défaut\N{NO-BREAK SPACE}: celle du système, sinon fr)"
        ),
        "cli.audit.timeout": (
            "délai d'attente réseau pour une URL, en secondes "
            "(par défaut\N{NO-BREAK SPACE}: %(default)s)"
        ),
        # Loading errors
        "load.unreadable": "impossible de lire {path}\N{NO-BREAK SPACE}: {reason}",
        "load.too_large": "{location} dépasse la limite de {limit} octets",
        "load.not_html": "{url} n'est pas une page HTML ({content_type})",
        "load.http_status": "{url} a répondu avec le code HTTP {status}",
        "load.unreachable": "impossible de joindre {url}\N{NO-BREAK SPACE}: {reason}",
        "load.timeout": "{url} n'a pas répondu en {timeout}\N{NO-BREAK SPACE}s",
        "report.title": "Audit de {location} ({size} octets)",
        "report.clean": (
            "Aucun problème détecté par les vérifications automatiques. "
            "Un audit manuel reste nécessaire."
        ),
        # French typography puts a non-breaking space before ":".
        "report.summary": "Résumé\N{NO-BREAK SPACE}: {counts}",
        "severity.error": "erreur",
        "severity.warning": "avertissement",
        "severity.info": "info",
        "count.error.one": "{count} erreur",
        "count.error.other": "{count} erreurs",
        "count.warning.one": "{count} avertissement",
        "count.warning.other": "{count} avertissements",
        "count.info.one": "{count} info",
        "count.info.other": "{count} infos",
        "rule.A11Y-LANG-MISSING": "La langue par défaut de la page n'est pas déclarée",
        "rule.A11Y-LANG-INVALID": "Le code de langue de la page n'est pas valide",
        "rule.A11Y-IMG-ALT": "Image sans alternative textuelle",
        "rule.A11Y-HEADING-H1-MISSING": "La page n'a pas de titre de niveau 1",
        "rule.A11Y-HEADING-H1-MULTIPLE": "La page a plusieurs titres de niveau 1",
        "rule.A11Y-HEADING-SKIP": "Niveau de titre sauté par rapport au titre précédent",
        "rule.A11Y-HEADING-EMPTY": "Titre sans texte",
        "rule.A11Y-ARIA-LABELLEDBY": "aria-labelledby fait référence à un id inexistant",
        "rule.A11Y-LINK-NAME": "Lien sans intitulé",
        "rule.A11Y-BUTTON-NAME": "Bouton sans intitulé",
    },
)
