# Website development

Use Quarto 1.11.9 with its bundled Pandoc 3.10 and Python 3.10 or later. The validator uses the Python standard library.

```sh
quarto --version
quarto pandoc --version
quarto render
quarto preview
python3 scripts/validate_site.py
python3 -B scripts/test_validate_site.py -v
```

Run these commands from the repository root. `quarto render` builds `_site/`, and `quarto preview` starts a local preview. The validator runs a complete render, checks its diagnostics, and inspects the generated pages, links, assets, Contact destinations and bibliography. It checks external Contact URL formats offline. Remote service availability can be checked separately.

After a successful build, run the regression tests to exercise the validator against disposable copies of the generated site.

Keep website source pages in `.qmd` files and shared shortcodes in `_variables.yml`. The render configuration limits public pages to `.qmd` sources. Keep `_site/` and `.quarto/` out of commits. When adding a publication, update the expected entry count in the validator alongside the bibliography change and preserve existing citation identifiers.

Check the current revision and working tree, then create a development branch from the intended base. Run the validator locally, push the branch and open a draft pull request targeting `main` for review. Pull requests run a read-only validation workflow. The Pages workflow validates the site again before uploading the artifact, and its deployment job runs on `main` only. Obtain approval before merging or deploying.
