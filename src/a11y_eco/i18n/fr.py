"""Messages en français."""

from a11y_eco.i18n.catalog import Catalog, PluralForm


def _plural_form(count: int) -> PluralForm:
    # In French, 0 takes the singular: "0 erreur", "1 erreur", "2 erreurs".
    return "one" if count in {0, 1} else "other"


CATALOG = Catalog(
    language="fr",
    plural_form=_plural_form,
    thousands_separator="\N{NARROW NO-BREAK SPACE}",
    messages={
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
            "  2  arguments invalides, page non chargée ou rapport non écrit\n"
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
        "cli.audit.fetch_resources": (
            "télécharge aussi la page et les fichiers qu'elle charge, {limit} au plus, "
            "pour mesurer ce qui transite réellement sur le réseau"
        ),
        "cli.audit.include_external": (
            "avec --fetch-resources, télécharge aussi les fichiers des autres "
            "hôtes\N{NO-BREAK SPACE}: ils verront votre adresse IP"
        ),
        "cli.audit.format": "format du rapport (par défaut\N{NO-BREAK SPACE}: %(default)s)",
        "cli.audit.output": "écrit le rapport dans FILE au lieu de la sortie standard",
        "cli.cannot_write": "impossible d'écrire {path}\N{NO-BREAK SPACE}: {reason}",
        "cli.external_needs_fetch": "--include-external ne fonctionne qu'avec --fetch-resources",
        "load.unreadable": "impossible de lire {path}\N{NO-BREAK SPACE}: {reason}",
        "load.too_large": "{location} dépasse la limite de {limit} octets",
        "load.not_html": "{url} n'est pas une page HTML ({content_type})",
        "load.http_status": "{url} a répondu avec le code HTTP {status}",
        "load.unreachable": "impossible de joindre {url}\N{NO-BREAK SPACE}: {reason}",
        "load.timeout": "{url} n'a pas répondu en {timeout}\N{NO-BREAK SPACE}s",
        "metrics.title": "Sobriété (valeurs minimales, d'après le seul HTML)",
        "metrics.requests": "Requêtes au chargement\N{NO-BREAK SPACE}: au moins {count}",
        "metrics.resources": "Ressources\N{NO-BREAK SPACE}: {list}",
        "metrics.none": "aucune",
        "metrics.deferred": "Chargées à la demande\N{NO-BREAK SPACE}: {count}",
        "metrics.external": "Servies par un autre hôte\N{NO-BREAK SPACE}: {count}",
        "metrics.domains": "Domaines\N{NO-BREAK SPACE}: {count}",
        "metrics.dom": "Éléments du DOM\N{NO-BREAK SPACE}: {count}",
        "network.title": "Mesures réseau (valeurs réelles)",
        "network.requests": "Requêtes\N{NO-BREAK SPACE}: {count}",
        "network.failed": "Téléchargements en échec\N{NO-BREAK SPACE}: {count}",
        "network.transferred": "Données transférées\N{NO-BREAK SPACE}: {size} octets",
        "network.transferred_minimum": (
            "Données transférées\N{NO-BREAK SPACE}: au moins {size} octets"
        ),
        "network.skipped": "Non téléchargées, limite atteinte\N{NO-BREAK SPACE}: {count}",
        "resource.stylesheet.one": "{count} feuille de style",
        "resource.stylesheet.other": "{count} feuilles de style",
        "resource.script.one": "{count} script",
        "resource.script.other": "{count} scripts",
        "resource.image.one": "{count} image",
        "resource.image.other": "{count} images",
        "resource.font.one": "{count} police",
        "resource.font.other": "{count} polices",
        "resource.media.one": "{count} fichier audio ou vidéo",
        "resource.media.other": "{count} fichiers audio ou vidéo",
        "resource.frame.one": "{count} contenu intégré",
        "resource.frame.other": "{count} contenus intégrés",
        "resource.other.one": "{count} autre",
        "resource.other.other": "{count} autres",
        "report.title": "Audit de {location} ({size} octets)",
        "report.clean": (
            "Aucun problème détecté par les vérifications automatiques. "
            "Un audit manuel reste nécessaire."
        ),
        "report.summary": "Résumé\N{NO-BREAK SPACE}: {counts}",
        "cli.rules.help": "liste les règles d'audit",
        "cli.rules.description": "Liste les règles d'audit, avec leur sévérité et leur référence.",
        "cli.rules.format": "format de la liste (par défaut\N{NO-BREAK SPACE}: %(default)s)",
        "rules.title": "Règles d'a11y-eco",
        "rules.generated": (
            "Généré par `a11y-eco rules --format markdown --lang {language}`\N{NO-BREAK SPACE}: "
            "ne pas modifier à la main."
        ),
        "rules.count": "{count} règles.",
        "rules.group.a11y": "Accessibilité (RGAA)",
        "rules.group.eco": "Éco-conception (RWEB), d'après le HTML",
        "rules.group.network": "Éco-conception (RWEB), avec --fetch-resources",
        "rules.column.rule": "Règle",
        "rules.column.severity": "Sévérité",
        "rules.column.reference": "Référence",
        "rules.column.about": "Ce qui est vérifié",
        "about.A11Y-LANG-MISSING": (
            "La langue par défaut de la page doit être déclarée sur l'élément html."
        ),
        "about.A11Y-LANG-INVALID": "La langue déclarée doit être un code de langue bien formé.",
        "about.A11Y-PAGE-TITLE": (
            "La page doit avoir un titre, la première chose qu'annonce un lecteur d'écran."
        ),
        "about.A11Y-IMG-ALT": (
            "Chaque image doit avoir une alternative textuelle, vide si l'image est décorative."
        ),
        "about.A11Y-HEADING-H1-MISSING": "La page devrait avoir un titre de niveau 1.",
        "about.A11Y-HEADING-H1-MULTIPLE": (
            "Plusieurs titres de niveau 1 sont permis, mais révèlent souvent un problème de "
            "structure."
        ),
        "about.A11Y-HEADING-SKIP": (
            "Un titre ne doit pas descendre de plus d'un niveau sous le titre précédent."
        ),
        "about.A11Y-HEADING-EMPTY": (
            "Un titre doit avoir un texte, éventuellement l'alternative d'une image."
        ),
        "about.A11Y-ARIA-LABELLEDBY": (
            "Chaque id cité dans aria-labelledby doit exister dans la page."
        ),
        "about.A11Y-LINK-NAME": "Chaque lien doit avoir un nom accessible.",
        "about.A11Y-BUTTON-NAME": "Chaque bouton doit avoir un nom accessible.",
        "about.ECO-REQUESTS": "La page ne devrait pas faire plus de 40 requêtes à son chargement.",
        "about.ECO-STYLESHEETS": "La page ne devrait pas charger plus de 10 feuilles de style.",
        "about.ECO-DOMAINS": (
            "La page et ses ressources ne devraient pas venir de plus de 5 domaines."
        ),
        "about.ECO-INLINE-CODE": (
            "Les gros blocs de CSS et de JavaScript devraient être dans des fichiers externes, "
            "que le navigateur garde en cache."
        ),
        "about.ECO-MEDIA-AUTOLOAD": (
            "L'audio et la vidéo ne devraient être téléchargés qu'à la demande de l'utilisateur."
        ),
        "about.ECO-LAZY-LOADING": (
            "Les images et les cadres qui peuvent être hors de l'écran devraient être chargés à "
            "la demande."
        ),
        "about.ECO-EMBEDDED-DOCUMENT": (
            "Les documents (PDF, bureautique) devraient être proposés en lien, pas affichés "
            "dans la page."
        ),
        "about.ECO-GIF": (
            "Les animations devraient être des vidéos plutôt que des images GIF, bien plus lourdes."
        ),
        "about.ECO-WEB-FONTS": "La page ne devrait pas télécharger plus de 2 polices.",
        "about.ECO-CANVAS": (
            "Un canvas est redessiné par script\N{NO-BREAK SPACE}: HTML et CSS suffisent "
            "souvent, et sont plus légers."
        ),
        "about.ECO-VIEWPORT": (
            "La page devrait déclarer un viewport, pour que les navigateurs mobiles ne "
            "réduisent pas une page de bureau."
        ),
        "about.ECO-TITLE": (
            "La page devrait avoir un titre, pour que les personnes et les moteurs de recherche "
            "la trouvent tout de suite."
        ),
        "about.ECO-META-DESCRIPTION": (
            "La page devrait avoir une meta description, qui la résume dans les résultats de "
            "recherche."
        ),
        "about.ECO-ANALYTICS": "La page devrait utiliser au plus un outil de mesure d'audience.",
        "about.ECO-SOCIAL-BUTTONS": (
            "Les réseaux sociaux devraient être proposés par de simples liens, pas par leurs "
            "lourds scripts officiels."
        ),
        "about.ECO-CAROUSEL": "La page devrait avoir au plus un carrousel.",
        "about.ECO-ANIMATIONS": "La page ne devrait pas avoir plus de 2 animations.",
        "about.ECO-SVG-METADATA": (
            "Le SVG intégré devrait être débarrassé des métadonnées laissées par les logiciels "
            "de dessin."
        ),
        "about.ECO-COMPRESSION": (
            "Les fichiers HTML, CSS, JavaScript et SVG devraient être envoyés compressés (gzip, "
            "Brotli)."
        ),
        "about.ECO-CACHE-HEADERS": (
            "Les fichiers statiques devraient indiquer combien de temps les garder, avec "
            "Expires ou Cache-Control."
        ),
        "about.ECO-COOKIE-DOMAINS": (
            "Les fichiers statiques devraient venir d'au plus un domaine qui utilise des cookies."
        ),
        "about.ECO-REDIRECTS": (
            "Le chargement de la page ne devrait pas passer par plus d'une redirection."
        ),
        "html.description": (
            "Rapport d'audit d'accessibilité et d'éco-conception produit par a11y-eco"
        ),
        "html.findings": "Problèmes détectés",
        "html.finding": "{severity}\N{NO-BREAK SPACE}: {message}",
        "html.position": "ligne {line}, colonne {column}",
        "html.generated": "Rapport généré par a11y-eco {version}",
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
        "rule.A11Y-PAGE-TITLE": (
            "La page n'a pas de titre\N{NO-BREAK SPACE}: "
            "les lecteurs d'écran ne peuvent pas l'annoncer"
        ),
        "rule.A11Y-IMG-ALT": "Image sans alternative textuelle",
        "rule.A11Y-HEADING-H1-MISSING": "La page n'a pas de titre de niveau 1",
        "rule.A11Y-HEADING-H1-MULTIPLE": "La page a plusieurs titres de niveau 1",
        "rule.A11Y-HEADING-SKIP": "Niveau de titre sauté par rapport au titre précédent",
        "rule.A11Y-HEADING-EMPTY": "Titre sans texte",
        "rule.A11Y-ARIA-LABELLEDBY": "aria-labelledby fait référence à un id inexistant",
        "rule.A11Y-LINK-NAME": "Lien sans intitulé",
        "rule.A11Y-BUTTON-NAME": "Bouton sans intitulé",
        "rule.ECO-REQUESTS": (
            "Au moins {count} requêtes au chargement "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-STYLESHEETS": (
            "{count} feuilles de style (maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-DOMAINS": (
            "Ressources servies par {count} domaines "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-INLINE-CODE": (
            "{count} blocs volumineux de CSS ou JavaScript dans la page "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-MEDIA-AUTOLOAD": "Audio ou vidéo téléchargé sans que l'utilisateur le demande",
        "rule.ECO-LAZY-LOADING": (
            "Image ou contenu intégré chargé même s'il n'est jamais affiché "
            '(ajouter loading="lazy")'
        ),
        "rule.ECO-EMBEDDED-DOCUMENT": (
            "Document affiché dans la page (proposer plutôt un lien vers le fichier)"
        ),
        "rule.ECO-GIF": "Image GIF, peut-être animée (une vidéo est bien plus légère)",
        "rule.ECO-WEB-FONTS": (
            "Au moins {count} polices téléchargées (maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-CANVAS": (
            "Canvas\N{NO-BREAK SPACE}: vérifier que du HTML et du CSS "
            "ne pourraient pas le remplacer"
        ),
        "rule.ECO-VIEWPORT": (
            "Pas de balise meta viewport\N{NO-BREAK SPACE}: la page n'est peut-être pas "
            "conçue pour le mobile"
        ),
        "rule.ECO-TITLE": (
            "La page n'a pas de titre, ce qui la rend plus difficile à trouver "
            "dans les résultats de recherche"
        ),
        "rule.ECO-META-DESCRIPTION": "La page n'a pas de meta description, ou une description vide",
        "rule.ECO-ANALYTICS": (
            "Outil de mesure d'audience, l'un des {count} de la page "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-SOCIAL-BUTTONS": (
            "Script officiel de réseau social (de simples liens de partage suffisent)"
        ),
        "rule.ECO-CAROUSEL": (
            "Carrousel, l'un des {count} de la page (maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-ANIMATIONS": (
            "Animation, l'une des {count} de la page "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-SVG-METADATA": (
            "Image SVG contenant encore les métadonnées de son logiciel de dessin"
        ),
        "rule.ECO-COMPRESSION": (
            "Fichier texte envoyé sans compression (gzip ou Brotli l'allégerait)"
        ),
        "rule.ECO-CACHE-HEADERS": (
            "Ni Expires ni Cache-Control\N{NO-BREAK SPACE}: le navigateur ne sait pas "
            "combien de temps le garder"
        ),
        "rule.ECO-COOKIE-DOMAINS": (
            "Fichiers statiques servis avec des cookies par {count} domaines "
            "(maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
        "rule.ECO-REDIRECTS": (
            "Redirection, l'une des {count} (maximum recommandé\N{NO-BREAK SPACE}: {limit})"
        ),
    },
)
