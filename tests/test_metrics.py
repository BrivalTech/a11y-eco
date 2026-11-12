from a11y_eco.dom import parse_html
from a11y_eco.metrics import measure
from a11y_eco.models import Metrics, ResourceType

PAGE = "https://www.example.com/"

MARKUP = """
<html><head>
  <link rel="stylesheet" href="/site.css">
  <link rel="stylesheet" href="https://fonts.example.net/inter.css">
  <script src="https://cdn.example.org/lib.js"></script>
  <script src="https://cdn.example.org/plugin.js"></script>
</head><body>
  <img src="/logo.png" alt="">
  <img src="/photo.jpg" alt="" loading="lazy">
  <iframe src="https://maps.example.com/" loading="lazy"></iframe>
</body></html>
"""


def test_measures_requests_resources_and_hosts_of_a_web_page() -> None:
    metrics = measure(parse_html(MARKUP, url=PAGE))

    assert metrics == Metrics(
        requests=6,  # the HTML, 2 stylesheets, 2 scripts, 1 image
        resources_by_type={
            ResourceType.STYLESHEET: 2,
            ResourceType.SCRIPT: 2,
            ResourceType.IMAGE: 1,
        },
        deferred=2,  # the lazy image and the lazy iframe
        external=3,  # fonts.example.net, and cdn.example.org twice
        domains=3,  # www.example.com, fonts.example.net, cdn.example.org
        dom_elements=10,
    )


def test_page_without_resources_makes_one_request_on_one_domain() -> None:
    metrics = measure(parse_html("<p>Hello</p>", url=PAGE))

    assert (metrics.requests, metrics.domains, metrics.external) == (1, 1, 0)
    assert metrics.resources_by_type == {}


def test_local_file_counts_relative_resources_as_its_own() -> None:
    markup = '<img src="a.png"><script src="https://cdn.example.org/x.js"></script>'
    metrics = measure(parse_html(markup))

    assert (metrics.requests, metrics.external, metrics.domains) == (3, 1, 2)
