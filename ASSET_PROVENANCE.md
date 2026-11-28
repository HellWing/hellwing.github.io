# Homepage asset provenance

Sprint 02 uses the portrait already published in this repository. The site owner is the portrait subject. Photographer credit and any reuse terms beyond this site are unrecorded. Quarto serves the original JPEG at its existing path and scales it proportionally.

| Filename | Source | Alt text | Pixel dimensions | Bytes |
| --- | --- | --- | --- | ---: |
| `assets/portrait.jpg` | Existing repository portrait, originally added in `0053f5c` | Portrait of Wojciech A. Hellwing | 488 × 529 | 70,471 |

The navy hero uses CSS gradients. The research cards and selected contributions use typography without scientific imagery. The prototype's illustrative imagery was excluded.

The public paths for the legacy figures are retained. Their repository history contains screenshots without documented image-specific reuse terms. The Drozda file shows the counts-in-ellipsoids diagram and distributions described by [Figure 1 of the preprint](https://arxiv.org/html/2506.01762v1). The exact source version and reuse terms for the repository screenshot are unconfirmed. The Hellwing file shows a cosmic-web map without its surrounding annotations. The Jaber file shows an upper portion of a pairwise-velocity plot. The latter two files require matching to the source figures and locating complete copies before prominent reuse.

A group-owned COCO density rendering is the preferred future hero. A complete, cleared figure for each research strand remains optional. Candidates include the [COCO paper](https://doi.org/10.1093/mnras/stw214), the [Naidoo et al. Local-Universe paper](https://doi.org/10.1103/PhysRevD.107.043533), the [DiRAC COCO feature](https://dirac.ac.uk/virgo-constraining-the-nature-of-dark-matter-using-the-coco-simulations/), [COWS](https://doi.org/10.1093/mnras/stac1382), and the [V-web classification paper](https://doi.org/10.1051/0004-6361/202453376). Before adding an asset, confirm the version, panel, credit and reuse terms with the source or rights holder. Preserve axes, scale annotations and legends.

# Sprint 03 research assets

## COWS simulation example

Simon Pfeifer's repository includes a worked example that applies COsmic Web Skeleton (COWS) to a 64 × 64 × 64 V-web data cube cut from a periodic simulation. The notebook records the original Matplotlib PNGs. The two files below are direct extractions of the complete embedded outputs, with no rerun, crop, resampling or colour changes. The panels retain all plotted tick marks, and the website caption identifies the grid axes and the difference between the two slices. [COWS example notebook at commit `4c492af`](https://github.com/SimonPfeifer/cows/blob/4c492af95522c8d668ea7aa6dc57b7843c9de929/docs/example.ipynb)

| Local file | Source panel | Pixel dimensions | Bytes |
| --- | --- | --- | ---: |
| `assets/science/cows-v-web.png` | Notebook cell headed “Plot a slice of the V-web centred of a big knot”, at grid depth 11 | 251 × 248 | 5,575 |
| `assets/science/cows-filament-spines.png` | Notebook cell headed “Remove cells that are knots in the V-web”, projecting the separated spines across a 10-cell-thick slice | 251 × 248 | 4,973 |

Copyright © 2022 Simon Pfeifer. The upstream BSD 3-Clause terms cover redistribution of the notebook outputs, which have no separate credit or third-party notice in the notebook. The upstream licence is included verbatim at `assets/science/cows-license.txt` and linked from the caption. The original licence file also contains an acknowledgment for the scikit-image implementation used in the code. [Upstream licence at the same commit](https://github.com/SimonPfeifer/cows/blob/4c492af95522c8d668ea7aa6dc57b7843c9de929/LICENSE.txt)

The method is described in Simon Pfeifer, Noam I. Libeskind, Yehuda Hoffman, Wojciech A. Hellwing, Maciej Bilicki and Krishna Naidoo, “COWS: a filament finder for Hessian cosmic web identifiers”, *Monthly Notices of the Royal Astronomical Society* **514**, 470–479 (2022). The notebook panels are distinct from the journal figures. [Published paper, DOI 10.1093/mnras/stac1382](https://doi.org/10.1093/mnras/stac1382)

## Figure candidates for review

| Candidate | Reuse evidence and acquisition | File or evidence still needed |
| --- | --- | --- |
| COCO dark matter density rendering for the homepage | No group-supplied original was present. Reuse terms for the journal and DiRAC renderings are unconfirmed. The homepage retains its gradient. [COCO paper](https://doi.org/10.1093/mnras/stw214), [DiRAC feature](https://dirac.ac.uk/virgo-constraining-the-nature-of-dark-matter-using-the-coco-simulations/) | PI-approved original rendering with creator credit, reuse terms and any scale information. |
| Wang et al. (2023), Fig. 2, COCO merger-tree mass histories | Durham identifies the published article's original content as CC BY 4.0. The arXiv version also identifies CC BY 4.0. Its Fig. 2 caption describes original COCO analysis. The managed environment denied source downloads, so a complete panel from either version could not be acquired. [Durham repository record](https://durham-repository.worktribe.com/output/2287108/ghostly-galaxies-accretion-dominated-stellar-systems-in-low-mass-dark-matter-halos), [arXiv article](https://arxiv.org/html/2306.17454) | Complete panel or source PDF from a licensed version. Confirm the figure credit and preserve the mass and redshift axes and cooling-threshold annotation. |
| Olex et al. (2025), V-web classification, arXiv v1 Fig. 7 | UWA lists CC BY alongside a general publisher copyright note. The exact arXiv v1 separately lists CC BY 4.0, and Fig. 7 shows the authors' classification at the constant-volume threshold. A journal-version panel and its terms were unconfirmed. Source downloads were denied. [UWA record](https://research-repository.uwa.edu.au/en/publications/a-universal-physically-motivated-threshold-for-hessian-based-cosm/), [arXiv v1](https://arxiv.org/html/2412.09531v1) | Complete Fig. 7 with legend from the licensed arXiv version or exact journal-version rights and file. |
| Naidoo et al. (2023), constrained local simulations, arXiv v2 Fig. 5 | The exact arXiv v2 identifies CC BY 4.0. Fig. 5 and its caption describe the authors' density maps and displacement arrows. Source downloads were denied. No rights determination was made for the APS figure. [arXiv v2](https://arxiv.org/html/2209.14386v2), [APS article](https://doi.org/10.1103/PhysRevD.107.043533) | Complete Fig. 5 from arXiv v2 with shared colour scale and coordinate units, or a cleared original file from the authors. |
| Drozda et al. (2025), counts-in-ellipsoids diagram and distributions | The arXiv anisotropic counts-in-cells record identifies CC BY 4.0. The exact journal figure terms and the source version of the existing screenshot are unconfirmed. No full panel was acquired. [arXiv preprint](https://arxiv.org/html/2506.01762), [APS paper](https://doi.org/10.1103/71cc-223l) | Complete Fig. 1 from the licensed preprint or a cleared original file. |
| COWS journal Fig. 1 or 2 | The institutional record provides an article copy. Journal-figure reuse terms and a standalone figure were unconfirmed. The first-party repository outputs above were acquired and licensed independently. [UCL record](https://discovery.ucl.ac.uk/id/eprint/10165841/) | Optional journal panel with version-specific reuse terms. |
