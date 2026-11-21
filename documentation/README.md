# Hendrix QMS documentation sources

How the user manual, the in-depth videos, the validation and certification pack and the introduction brochure are produced. Everything published uses a made-up company (Northfield Labs, MFG-48213, Colorado) and made-up people: never real company names, license numbers or staff.

## User manual (Training Center and PDF)
- **manual/**: the chapter text (`front.md`, `ch_flow.md` "How it all fits together", `ch_*.md`), `understand.md` (the "Understand it first" box of every module: what it is, why we do it, if it's skipped, an example) and `glossary.md`.
- Screenshots: `shots_<group>.py` take them against the mock Supabase (`tests/browser/mock_c.py`), run through `run_shots.py`, which freezes the clock at the sample-data date and applies `scrub.py` (fictional names on every shot). Groups: found, qual, mgmt, supply, facility, prod, secure; `--fiction` also rewrites the sample data (needed for qual and secure, whose PDFs are drawn from data). `shots_trc.py` takes the Training Center picture. A few pictures (Line Map, Facility Map, phone QR form, sign-in) come from the film kit; they are kept in `site/training/manual/img/`.
- Builders: `build_manual.py <pdf>` (Chromium PDF with contents, page numbers and the "What do I fill in when…" index) and `build_web.py` (one searchable page at `site/training/manual/` plus `toc.js`, the access each section needs, used by the Training Center).

## In-depth videos (Training Center)
- **video/deep/deep.py** builds one narrated video per manual section from the same text: the "Understand it first" box as large-type cards, then when to use it, the steps with the button highlighted on the screenshot (found by OCR), what Hendrix checks and tips. The overview chapter is read table row by row. Output: `site/training/media/deep/*.mp4|jpg` and `site/training/deep.js`. Needs piper-tts and its voice (`HX_VOICE`), tesseract and ffmpeg.

## Weekly update (after features are added)
1. Update the chapter text and `understand.md` for what changed; add new modules to `build_web.py` ACCESS.
2. `python3 documentation/manual/run_shots.py <group>` for the groups whose pages changed (`--fiction` for qual and secure); OCR the new shots for real names before publishing.
3. `python3 documentation/manual/build_manual.py site/training/manual/Hendrix_QMS_User_Manual.pdf` and `python3 documentation/manual/build_web.py`.
4. `python3 documentation/video/deep/deep.py <changed-section-slugs>` (then it rewrites the catalog).
5. Run `tests/browser/test_trc.py` and `test_site.py`, commit and push: GitHub Actions publishes hendrixqms.com.

## Older material
- **manual/** also holds the controls lists, the certification pack (`cert_content.md`, `cert_data.py`, `build_cert.py`) and the introduction brochure (`build_intro.py`) from Release 41.
- **video/kit** and **video/series** are the October 2026 narrated series (recorded live in the app with `hxvideo.py`).
