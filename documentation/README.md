# Hendrix QMS documentation sources

How the user manual, the validation and certification pack, the introduction brochure and the training videos were produced.

- **manual/**: the chapter text (`ch_*.md`, `front.md`, `glossary.md`), the controls lists (`controls_*.md`), the certification pack content (`cert_content.md`, `cert_data.py`), the screenshot scripts (`shots_*.py`, built on `tests/browser/mock_c.py`) and the PDF builders (`hxpdf.py`, `build_manual.py`, `build_cert.py`, `build_intro.py`). The PDFs are rendered with Chromium (Playwright).
- **video/**: the narrated video kit (`kit/hxvideo.py`, with its guide `kit/KIT.md`), the series brief, and the scene scripts of each video in the series (`series/NN_group/`).

When a module changes, update its `ch_*.md` section and its controls list. Then re-run its screenshot script and the builders. The scripts were written in a work folder, so adjust the paths at the top of each one before running them elsewhere.
