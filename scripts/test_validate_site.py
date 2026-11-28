"""Exercise the validator with disposable copies of a successful site build."""

import io
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import validate_site


class OutputTests(unittest.TestCase):
    def setUp(self):
        original = validate_site.ROOT / "_site"
        self.assertTrue(original.is_dir(), "Run scripts/validate_site.py first.")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.site = Path(temporary.name) / "_site"
        shutil.copytree(original, self.site)

    def replace(self, relative_path, original, replacement):
        path = self.site / relative_path
        content = path.read_text(encoding="utf-8")
        self.assertIn(original, content)
        path.write_text(content.replace(original, replacement, 1), encoding="utf-8")

    def assert_rejected(self, diagnostic):
        self.assertIn(diagnostic, "\n".join(validate_site.validate_output(self.site)))

    def test_clean_build_and_private_docs(self):
        self.assertEqual(validate_site.validate_output(self.site), [])
        for name in (
            "AGENTS.md", "AGENTS.html", "CONTRIBUTING.md", "CONTRIBUTING.html",
            "ASSET_PROVENANCE.md", "ASSET_PROVENANCE.html",
            "_review",
        ):
            self.assertFalse((self.site / name).exists())

    def test_unresolved_variable_in_generated_html(self):
        self.replace("index.html", "</main>", "<p>?var:missing</p></main>")
        self.assert_rejected("index.html: unresolved Quarto variable placeholder")

    def test_missing_internal_link(self):
        self.replace("index.html", "</main>", '<a href="/missing.html">Missing</a></main>')
        self.assert_rejected("index.html: missing local target '/missing.html'")

    def test_missing_fragment(self):
        self.replace(
            "index.html", "</main>",
            '<a href="https://hellwing.github.io/research.html#missing">Missing</a></main>',
        )
        self.assert_rejected("index.html: missing fragment #missing in research.html")

    def test_missing_research_section(self):
        self.replace("research.html", 'id="novel-statistics"', 'id="changed-section"')
        self.assert_rejected("research.html: missing research section #novel-statistics")

    def test_missing_research_index_link(self):
        self.replace("research.html", 'href="#computational-foundation"', 'href="#top"')
        self.assert_rejected("research.html: missing in-page link to #computational-foundation")

    def test_missing_homepage_pillar_link(self):
        self.replace("index.html", 'href="./research.html#cosmic-web"', 'href="./research.html"')
        self.assert_rejected("index.html: missing pillar link to research.html#cosmic-web")

    def test_missing_published_research_doi(self):
        self.replace("research.html", 'href="https://doi.org/10.1103/71cc-223l"', 'href="#top"')
        self.assert_rejected("research.html: missing published DOI 10.1103/71cc-223l")

    def test_missing_research_bibliography_anchor(self):
        self.replace("publications.html", 'id="ref-2025A&amp;A...700A..65H"', 'id="ref-other"')
        self.assert_rejected("publications.html: missing research-paper anchor #ref-2025A&A...700A..65H")

    def test_missing_research_figure_alt_text(self):
        self.replace(
            "research.html",
            'alt="A simulation slice with green filaments and yellow knots against blue sheets and purple voids."',
            'alt=""',
        )
        self.assert_rejected("research.html: missing image or alt text for assets/science/cows-v-web.png")

    def test_missing_research_figure_file(self):
        figure = "assets/science/cows-filament-spines.png"
        (self.site / figure).unlink()
        self.assert_rejected(f"research.html: missing local target '{figure}'")

    def test_missing_linked_scientific_graphic(self):
        figure = "assets/papers/jaber2024_pv.png"
        self.replace("index.html", "</main>", f'<img src="{figure}" alt="Figure"></main>')
        self.assertEqual(validate_site.validate_output(self.site), [])
        (self.site / figure).unlink()
        self.assert_rejected(f"index.html: missing local target '{figure}'")
        self.assert_rejected(f"Missing or empty generated asset {figure}")

    def test_missing_css_asset(self):
        with (self.site / "styles.css").open("a", encoding="utf-8") as css:
            css.write("\n.example { background-image: url('assets/missing.svg'); }\n")
        self.assert_rejected("styles.css: missing local target 'assets/missing.svg'")

    def test_missing_legacy_cv(self):
        (self.site / "assets/Hellwing_CV_04_2024.pdf").unlink()
        self.assert_rejected("Missing or empty generated asset assets/Hellwing_CV_04_2024.pdf")

    def test_missing_page(self):
        (self.site / "about.html").unlink()
        self.assert_rejected("Missing generated page about.html")

    def test_each_contact_destination(self):
        contact = self.site / "contact.html"
        html = contact.read_text(encoding="utf-8")
        page = validate_site.Page(html)
        for label, href in page.links:
            if href.startswith("mailto:"):
                expected = "expected an email link matching its displayed address"
            elif label in validate_site.CONTACT_URLS:
                expected = f"missing or malformed {label} destination"
            else:
                continue
            with self.subTest(destination=label):
                contact.write_text(
                    html.replace(f'href="{href}"', 'href="https://example.org/"'),
                    encoding="utf-8",
                )
                self.assert_rejected(f"contact.html: {expected}")

    def test_each_selected_paper_anchor(self):
        publications = self.site / "publications.html"
        html = publications.read_text(encoding="utf-8")
        for identifier in validate_site.SELECTED_PAPERS:
            with self.subTest(anchor=identifier):
                publications.write_text(
                    html.replace(f'id="{identifier}"', 'id="ref-test"'), encoding="utf-8",
                )
                self.assert_rejected(f"publications.html: missing selected-paper anchor #{identifier}")

    def test_bibliography_entry_count(self):
        self.replace("publications.html", 'class="csl-entry"', 'class="test"')
        self.assert_rejected("bibliography entries, found 97")


class RenderTests(unittest.TestCase):
    def check_render(self, returncode, output, diagnostic):
        process = subprocess.CompletedProcess(["quarto", "render"], returncode, stdout=output)
        stderr = io.StringIO()
        with (
            patch.object(validate_site.subprocess, "run", return_value=process),
            patch.object(validate_site, "validate_output", return_value=[]),
            redirect_stdout(io.StringIO()),
            redirect_stderr(stderr),
        ):
            self.assertEqual(validate_site.main(), 1)
        self.assertIn(diagnostic, stderr.getvalue())

    def test_nonzero_render_status_fails(self):
        self.check_render(2, "Broken document\n", "Quarto render failed with exit code 2.")

    def test_warning_fails_even_with_clean_html_and_zero_status(self):
        self.check_render(
            0, "WARNING Unknown var example specified in a var shortcode.\n",
            "Quarto reported unresolved variable warnings.",
        )


if __name__ == "__main__":
    unittest.main()
