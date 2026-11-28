"""Render the Quarto website and check its generated output offline."""

import re
import subprocess
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://hellwing.github.io/"
SITE_HOST = urlsplit(SITE_URL).hostname
REQUIRED_PAGES = (
    "index.html", "about.html", "contact.html", "cv.html", "data.html",
    "news.html", "posts/2025-09-26-site-refresh.html", "publications.html",
    "research.html", "software.html", "supervision.html", "teaching.html",
)
RESEARCH_FIGURES = (
    "assets/science/cows-v-web.png",
    "assets/science/cows-filament-spines.png",
)
REQUIRED_ASSETS = (
    "assets/W_Hellwing_CV.pdf",
    "assets/Hellwing_CV_04_2024.pdf",
    "assets/portrait.jpg",
    "assets/logo.svg",
    "assets/hero-stars.svg",
    "assets/papers/drozda2025_aniso_skew.png",
    "assets/papers/hellwing2021_cw_conc.png",
    "assets/papers/jaber2024_pv.png",
    *RESEARCH_FIGURES,
    "assets/science/cows-license.txt",
)
SELECTED_PAPERS = (
    "ref-2025arXiv250601762D",
    "ref-2021PhRvD.103f3517H",
    "ref-2024PhRvD.109l3528J",
)
RESEARCH_PILLARS = ("novel-statistics", "simulation-campaigns", "cosmic-web")
RESEARCH_SECTIONS = (*RESEARCH_PILLARS, "computational-foundation")
RESEARCH_PAPERS = {
    "10.1103/PhysRevLett.112.221102": "2014PhRvL.112v1102H",
    "10.1103/PhysRevD.109.123528": "2024PhRvD.109l3528J",
    "10.1103/PhysRevD.107.083525": "2023PhRvD.107h3525G",
    "10.1103/PhysRevD.105.043538": "2022PhRvD.105d3538G",
    "10.1103/PhysRevD.103.103524": "2021PhRvD.103j3524G",
    "10.1103/4sxk-z8z4": "2025arXiv250412820D",
    "10.1103/71cc-223l": "2025arXiv250601762D",
    "10.1103/PhysRevD.107.043533": "2023PhRvD.107d3533N",
    "10.1103/PhysRevD.109.083511": "2024PhRvD.109h3511N",
    "10.1093/mnrasl/slw081": "2016MNRAS.461L..11H",
    "10.1093/mnras/stw214": "2016MNRAS.457.3492H",
    "10.1093/mnras/stw2686": "2017MNRAS.464.4520B",
    "10.1093/mnras/stw1046": "2016MNRAS.460.1214L",
    "10.3847/1538-4357/ad011d": "2023ApJ...958..166W",
    "10.1093/mnras/stab2452": "2021MNRAS.507.4826L",
    "10.1093/mnras/staa2525": "2020MNRAS.498..702L",
    "10.1093/mnras/stab3524": "2022MNRAS.511.4044D",
    "10.1051/0004-6361/202453376": "2025A&A...696A.142O",
    "10.1093/mnras/stac1382": "2022MNRAS.514..470P",
    "10.1103/PhysRevD.103.063517": "2021PhRvD.103f3517H",
    "10.1051/0004-6361/202452246": "2025A&A...700A..65H",
    "10.1093/mnras/stad3347": "2024MNRAS.527.4087J",
    "10.1103/PhysRevD.106.023521": "2022PhRvD.106b3521C",
    "10.1103/PhysRevD.110.083520": "2024PhRvD.110h3520G",
}
EXPECTED_BIBLIOGRAPHY_ENTRIES = 98

ORCID_ID = r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
CONTACT_URLS = {
    "GitHub": r"https://github\.com/[A-Za-z0-9-]+/?",
    "ADS": rf"https://ui\.adsabs\.harvard\.edu/search/q=orcid:{ORCID_ID}",
    "ORCID": rf"https://orcid\.org/{ORCID_ID}",
    "Scholar": r"https://scholar\.google\.com/citations\?user=[\w-]+",
}
MAILTO = re.compile(r"mailto:[^@\s/?#]+@(?:[\w-]+\.)+[\w-]+")
VAR_WARNING = re.compile(r"unknown var\b[^\n]*\bvar shortcode\b", re.I)
VAR_PLACEHOLDER = re.compile(r"\?var:[\w.-]+|\{\{\s*<\s*var\b", re.I)
CSS_REFERENCE = re.compile(
    r"""url\(\s*["']?([^"')]+)["']?\s*\)|@import\s+["']([^"']+)["']""",
    re.I,
)


def css_references(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [url.strip() for match in CSS_REFERENCE.findall(css) for url in match if url]


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.anchors = set()
        self.sections = set()
        self.citations = set()
        self.references = set()
        self.images = {}
        self.links = []
        self.link = None
        self.in_style = False
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = {name: value for name, value in attrs if value is not None}
        identifier = attrs.get("id", "")
        if identifier:
            self.anchors.add(identifier)
            if tag == "section":
                self.sections.add(identifier)
        if identifier.startswith("ref-") and "csl-entry" in attrs.get("class", "").split():
            self.citations.add(identifier)
        if tag == "a":
            if attrs.get("name"):
                self.anchors.add(attrs["name"])
            if "href" in attrs:
                self.link = (attrs["href"], [])
        if tag == "style":
            self.in_style = True
        if tag == "img" and "src" in attrs:
            self.images[attrs["src"]] = attrs.get("alt", "")

        fields = ["href", "src", "poster", "xlink:href"]
        if tag == "object":
            fields.append("data")
        self.references.update(attrs[field] for field in fields if attrs.get(field))
        if "srcset" in attrs:
            self.references.update(
                re.findall(r"(?:^|,)\s*(data:[^\s]+|[^,\s]+)", attrs["srcset"])
            )
        self.references.update(css_references(attrs.get("style", "")))

    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            href, text = self.link
            self.links.append(("".join(text).strip(), href))
            self.link = None
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.link is not None:
            self.link[1].append(data)
        if self.in_style:
            self.references.update(css_references(data))


def check_reference(site, pages, source, reference):
    try:
        url = urlsplit(urljoin(SITE_URL + quote(source.as_posix()), reference.strip()))
    except ValueError:
        return f"{source}: invalid URL {reference!r}"
    if url.scheme not in ("http", "https") or url.hostname != SITE_HOST:
        return None

    path = (site / unquote(url.path).lstrip("/")).resolve()
    if not path.is_relative_to(site):
        return f"{source}: URL escapes the output directory {reference!r}"
    if path.is_dir():
        path /= "index.html"
    if not path.is_file():
        return f"{source}: missing local target {reference!r}"

    fragment = unquote(url.fragment).split(":~:", 1)[0]
    page = pages.get(path.relative_to(site))
    if page and fragment and fragment.lower() != "top" and fragment not in page.anchors:
        return f"{source}: missing fragment #{fragment} in {path.relative_to(site)}"
    return None


def check_contact(page):
    errors = []
    mail_links = [(label, href) for label, href in page.links if href.startswith("mailto:")]
    if len(mail_links) != 1 or not (
        MAILTO.fullmatch(mail_links[0][1]) and f"mailto:{mail_links[0][0]}" == mail_links[0][1]
    ):
        errors.append("contact.html: expected an email link matching its displayed address")

    valid_urls = {}
    for label, pattern in CONTACT_URLS.items():
        urls = [unquote(href) for text, href in page.links if text == label]
        if len(urls) == 1 and re.fullmatch(pattern, urls[0]):
            valid_urls[label] = urls[0]
        else:
            errors.append(f"contact.html: missing or malformed {label} destination")
    if {"ORCID", "ADS"} <= valid_urls.keys():
        if valid_urls["ORCID"].rsplit("/", 1)[1] != valid_urls["ADS"].rsplit(":", 1)[1]:
            errors.append("contact.html: ADS and ORCID use different ORCID identifiers")
    return errors


def check_research(research, home):
    errors = []
    links = {href for _, href in research.links}
    for identifier in RESEARCH_SECTIONS:
        if identifier not in research.sections:
            errors.append(f"research.html: missing research section #{identifier}")
        if f"#{identifier}" not in links:
            errors.append(f"research.html: missing in-page link to #{identifier}")
    for doi in RESEARCH_PAPERS:
        if f"https://doi.org/{doi}" not in links:
            errors.append(f"research.html: missing published DOI {doi}")
    for figure in RESEARCH_FIGURES:
        if not research.images.get(figure, "").strip():
            errors.append(f"research.html: missing image or alt text for {figure}")
    if home:
        if "research" not in home.anchors:
            errors.append("index.html: missing research section #research")
        home_links = {(label, href.removeprefix("./")) for label, href in home.links}
        if ("Research", "research.html") not in home_links:
            errors.append("index.html: Research navigation must link to research.html")
        destinations = {url for _, url in home_links}
        for identifier in RESEARCH_PILLARS:
            if f"research.html#{identifier}" not in destinations:
                errors.append(f"index.html: missing pillar link to research.html#{identifier}")
    return errors


def validate_output(site):
    site = site.resolve()
    pages = {}
    errors = []
    files = sorted(site.rglob("*.html"))
    for file in files:
        source = file.relative_to(site)
        html = file.read_text(encoding="utf-8")
        if VAR_PLACEHOLDER.search(unescape(unquote(html))):
            errors.append(f"{source}: unresolved Quarto variable placeholder")
        pages[source] = Page(html)

    for name in REQUIRED_PAGES:
        if Path(name) not in pages:
            errors.append(f"Missing generated page {name}")
    for name in REQUIRED_ASSETS:
        asset = site / name
        if not asset.is_file() or asset.stat().st_size == 0:
            errors.append(f"Missing or empty generated asset {name}")

    references = {path: page.references for path, page in pages.items()}
    for file in sorted(site.rglob("*.css")):
        references[file.relative_to(site)] = set(css_references(file.read_text(encoding="utf-8")))
    for source, urls in references.items():
        for url in sorted(urls):
            error = check_reference(site, pages, source, url)
            if error:
                errors.append(error)

    contact = pages.get(Path("contact.html"))
    if contact:
        errors.extend(check_contact(contact))
    research = pages.get(Path("research.html"))
    if research:
        errors.extend(check_research(research, pages.get(Path("index.html"))))
    publications = pages.get(Path("publications.html"))
    if publications:
        count = len(publications.citations)
        if count != EXPECTED_BIBLIOGRAPHY_ENTRIES:
            errors.append(
                f"publications.html: expected {EXPECTED_BIBLIOGRAPHY_ENTRIES} "
                f"bibliography entries, found {count}"
            )
        for identifier in SELECTED_PAPERS:
            if identifier not in publications.citations:
                errors.append(f"publications.html: missing selected-paper anchor #{identifier}")
        for key in RESEARCH_PAPERS.values():
            if f"ref-{key}" not in publications.citations:
                errors.append(f"publications.html: missing research-paper anchor #ref-{key}")
    return errors


def main():
    try:
        render = subprocess.run(
            ["quarto", "render"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", errors="replace", check=False,
        )
    except OSError as error:
        print(f"Could not run Quarto: {error}", file=sys.stderr)
        return 1
    print(render.stdout, end="", flush=True)
    if render.returncode:
        print(f"Quarto render failed with exit code {render.returncode}.", file=sys.stderr)
        return 1

    errors = validate_output(ROOT / "_site")
    if VAR_WARNING.search(render.stdout):
        errors.insert(0, "Quarto reported unresolved variable warnings.")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Site validation passed (render, local links and assets, Contact URLs, Research, bibliography).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
