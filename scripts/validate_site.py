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
REQUIRED_ASSETS = (
    "assets/W_Hellwing_CV.pdf",
    "assets/Hellwing_CV_04_2024.pdf",
    "assets/portrait.jpg",
    "assets/logo.svg",
    "assets/hero-stars.svg",
    "assets/papers/drozda2025_aniso_skew.png",
    "assets/papers/hellwing2021_cw_conc.png",
    "assets/papers/jaber2024_pv.png",
)
SELECTED_PAPERS = (
    "ref-2025arXiv250601762D",
    "ref-2021PhRvD.103f3517H",
    "ref-2024PhRvD.109l3528J",
)
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
        self.citations = set()
        self.references = set()
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
        if identifier.startswith("ref-") and "csl-entry" in attrs.get("class", "").split():
            self.citations.add(identifier)
        if tag == "a":
            if attrs.get("name"):
                self.anchors.add(attrs["name"])
            if "href" in attrs:
                self.link = (attrs["href"], [])
        if tag == "style":
            self.in_style = True

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
    print("Site validation passed (render, local links and assets, Contact URLs, bibliography).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
