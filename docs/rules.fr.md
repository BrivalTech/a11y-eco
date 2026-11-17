# Règles d'a11y-eco

<!-- Généré par `a11y-eco rules --format markdown --lang fr` : ne pas modifier à la main. -->

33 règles.

## Accessibilité (RGAA)

| Règle | Sévérité | Référence | Ce qui est vérifié |
|---|---|---|---|
| `A11Y-LANG-MISSING` | erreur | RGAA 8.3 | La langue par défaut de la page doit être déclarée sur l'élément html. |
| `A11Y-LANG-INVALID` | erreur | RGAA 8.4 | La langue déclarée doit être un code de langue bien formé. |
| `A11Y-PAGE-TITLE` | erreur | RGAA 8.5 | La page doit avoir un titre, la première chose qu'annonce un lecteur d'écran. |
| `A11Y-IMG-ALT` | erreur | RGAA 1.1 | Chaque image doit avoir une alternative textuelle, vide si l'image est décorative. |
| `A11Y-HEADING-H1-MISSING` | avertissement | RGAA 9.1 | La page devrait avoir un titre de niveau 1. |
| `A11Y-HEADING-H1-MULTIPLE` | info | RGAA 9.1 | Plusieurs titres de niveau 1 sont permis, mais révèlent souvent un problème de structure. |
| `A11Y-HEADING-SKIP` | erreur | RGAA 9.1 | Un titre ne doit pas descendre de plus d'un niveau sous le titre précédent. |
| `A11Y-HEADING-EMPTY` | erreur | RGAA 9.1 | Un titre doit avoir un texte, éventuellement l'alternative d'une image. |
| `A11Y-ARIA-LABELLEDBY` | erreur | RGAA 8.2 | Chaque id cité dans aria-labelledby doit exister dans la page. |
| `A11Y-LINK-NAME` | erreur | RGAA 6.2 | Chaque lien doit avoir un nom accessible. |
| `A11Y-BUTTON-NAME` | erreur | RGAA 11.9 | Chaque bouton doit avoir un nom accessible. |

## Éco-conception (RWEB), d'après le HTML

| Règle | Sévérité | Référence | Ce qui est vérifié |
|---|---|---|---|
| `ECO-REQUESTS` | avertissement | RWEB_0047 | La page ne devrait pas faire plus de 40 requêtes à son chargement. |
| `ECO-STYLESHEETS` | avertissement | RWEB_0035 | La page ne devrait pas charger plus de 10 feuilles de style. |
| `ECO-DOMAINS` | avertissement | RWEB_0082 | La page et ses ressources ne devraient pas venir de plus de 5 domaines. |
| `ECO-INLINE-CODE` | info | RWEB_0042 | Les gros blocs de CSS et de JavaScript devraient être dans des fichiers externes, que le navigateur garde en cache. |
| `ECO-MEDIA-AUTOLOAD` | avertissement | RWEB_0106 | L'audio et la vidéo ne devraient être téléchargés qu'à la demande de l'utilisateur. |
| `ECO-LAZY-LOADING` | info | RWEB_0051 | Les images et les cadres qui peuvent être hors de l'écran devraient être chargés à la demande. |
| `ECO-EMBEDDED-DOCUMENT` | avertissement | RWEB_0033 | Les documents (PDF, bureautique) devraient être proposés en lien, pas affichés dans la page. |
| `ECO-GIF` | info | RWEB_0099 | Les animations devraient être des vidéos plutôt que des images GIF, bien plus lourdes. |
| `ECO-WEB-FONTS` | info | RWEB_0032 | La page ne devrait pas télécharger plus de 2 polices. |
| `ECO-CANVAS` | info | RWEB_0055 | Un canvas est redessiné par script : HTML et CSS suffisent souvent, et sont plus légers. |
| `ECO-VIEWPORT` | info | RWEB_0004 | La page devrait déclarer un viewport, pour que les navigateurs mobiles ne réduisent pas une page de bureau. |
| `ECO-TITLE` | avertissement | RWEB_0011 | La page devrait avoir un titre, pour que les personnes et les moteurs de recherche la trouvent tout de suite. |
| `ECO-META-DESCRIPTION` | avertissement | RWEB_0011 | La page devrait avoir une meta description, qui la résume dans les résultats de recherche. |
| `ECO-ANALYTICS` | avertissement | RWEB_0111 | La page devrait utiliser au plus un outil de mesure d'audience. |
| `ECO-SOCIAL-BUTTONS` | avertissement | RWEB_0059 | Les réseaux sociaux devraient être proposés par de simples liens, pas par leurs lourds scripts officiels. |
| `ECO-CAROUSEL` | info | RWEB_0010 | La page devrait avoir au plus un carrousel. |
| `ECO-ANIMATIONS` | avertissement | RWEB_0009 | La page ne devrait pas avoir plus de 2 animations. |
| `ECO-SVG-METADATA` | avertissement | RWEB_0100 | Le SVG intégré devrait être débarrassé des métadonnées laissées par les logiciels de dessin. |

## Éco-conception (RWEB), avec --fetch-resources

| Règle | Sévérité | Référence | Ce qui est vérifié |
|---|---|---|---|
| `ECO-COMPRESSION` | avertissement | RWEB_0076 | Les fichiers HTML, CSS, JavaScript et SVG devraient être envoyés compressés (gzip, Brotli). |
| `ECO-CACHE-HEADERS` | avertissement | RWEB_0075 | Les fichiers statiques devraient indiquer combien de temps les garder, avec Expires ou Cache-Control. |
| `ECO-COOKIE-DOMAINS` | avertissement | RWEB_0081 | Les fichiers statiques devraient venir d'au plus un domaine qui utilise des cookies. |
| `ECO-REDIRECTS` | avertissement | RWEB_0112 | Le chargement de la page ne devrait pas passer par plus d'une redirection. |
