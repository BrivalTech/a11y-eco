"""Sobriety measures of a page."""

from __future__ import annotations

from collections import Counter

from a11y_eco.dom import Document
from a11y_eco.models import Metrics
from a11y_eco.resources import find_resources, is_external


def measure(document: Document) -> Metrics:
    """Measure the sobriety of a page from its HTML.

    Args:
        document: The parsed page.

    Returns:
        The measures; counts of requests and resources are minimum values.
    """
    resources = find_resources(document)
    at_load = [resource for resource in resources if not resource.deferred]
    external_hosts = {resource.host for resource in at_load if is_external(resource, document)}

    return Metrics(
        requests=1 + len(at_load),
        resources_by_type=dict(Counter(resource.type for resource in at_load)),
        deferred=len(resources) - len(at_load),
        external=sum(1 for resource in at_load if is_external(resource, document)),
        domains=1 + len(external_hosts),
        dom_elements=sum(1 for _ in document.root.iter()),
    )
