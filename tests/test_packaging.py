import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
LINK_TARGET = re.compile(r"\]\(([^)\s]+)")


def test_readme_links_also_work_on_pypi() -> None:
    readme = PYPROJECT["project"]["readme"]
    targets = LINK_TARGET.findall((ROOT / readme).read_text(encoding="utf-8"))

    assert targets
    assert [target for target in targets if not target.startswith(("https://", "#"))] == []


def test_package_has_no_runtime_dependency() -> None:
    assert PYPROJECT["project"]["dependencies"] == []
