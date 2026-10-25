# hxvideo: narrated training videos of Hendrix QMS

`hxvideo.py` records the real app (served from a snapshot of `index.html`) against the mock database,
with a visible gold cursor, click ripples, Kokoro narration, captions (burned in + `.srt`),
loudness normalization (-16 LUFS) and one MP4 chapter per scene. Output: 1920x1080, H.264 + AAC, 30 fps.

The Hendrix tutorial in `../` (`build.py`, `scene*.py`) uses this kit to build `Hendrix_QMS_Tutorial.mp4`.

## Quick start (the 20-second sample)

```
cd .../scratchpad/video/kit/sample
python3 make_sample.py          # TTS -> record 2 scenes -> sample.mp4 + sample.srt
```

## A project folder

```
myvideo/
  index_snapshot.html   cp /home/claude/hendrix/index.html  (never serve the live file: people edit it)
  narration.py          NARR = [(key, text), ...]   SAY = [(written, spoken), ...]
  make.py               your scenes + the build call (example below)
  tts/  work/           made by the kit
```

## (a) Seed data

`hv.load_setup('qual', snapshot=SNAP)` execs everything before `with sync_playwright() as pw:` in
`manual/shots_qual.py` in a fresh dict and returns it: `ns['T']` (tables), `ns['handle']` (route handler),
`ns['BASE']` (app URL). Groups: `found qual mgmt supply facility prod`; any other shots script works with
`path=`. Use one fresh `load_setup()` per scene. You can edit `ns['T']` before recording, or wrap
`ns['handle']` to emulate what the real database does (numbering, who/when stamps), as in `../scene4.py`.

- `hv.new_context(b, ns, session=hv.session_script())` gives a logged-in admin at Missouri / Black Fox.
  Leave out `session=` and add `routes=[hv.token_route()]` to show a real sign-in.
- The browser clock is fixed at 2026-10-24 10:40 CDT. Pass `fixed=None` when the data comes from the real
  clock, for example the Line Map (Postgres `now()`).

## (b) Beats

A beat is a narration key plus the actions that run while it plays. `r.beat(key, fn)` starts the audio
clock, runs `fn()`, then waits until the sentence has finished (+0.45 s). Use the helpers so the cursor
moves visibly: `r.click(loc)`, `r.type(loc, text, delay=38, clear=False)`, `r.select(loc, value=...)`
(native dropdowns are not captured, so it ripples and sets the value), `r.fill(loc, '2026-10-31')` for date
inputs, `r.point(loc)`, `r.wheel(dy)`, `r.sign(canvas)`, `r.wait(s)`. Never use `time.sleep`.
`hv.field(scope, 'Label')` finds a Hendrix form field by its label. Load the page before `r.start()`.
Long typing makes silent gaps: keep typed text short or the narration a little longer.
Run with `PROBE=1` and `r.snap('name')` to save screenshots to `work/probe/` while you write the scene.

## (c) Several scenes -> one MP4

Record each scene with its own `hv.Rec(ctx, page, 'name')` ... `r.stop()`, then:
`hv.build([('name1', 'Chapter title'), ('name2', '...')], 'out.mp4')`. Encoded scenes are cached, so only
changed scenes are re-encoded. `hv.synth()` regenerates only changed sentences.
CPU: everything runs at `nice 10` with 2 x264 threads. Record and build one scene at a time, never in parallel.

## (d) Pronunciation respellings

These change the speech only; captions keep the written text. Respellings used so far:

| Written | Spoken as |
|---|---|
| CAPA / CAPAs | kay-pa / kay-pahs |
| COA, SKU, CSV | C O A, S K U, C S V (spaces, not dots: dots add pauses) |
| HACCP | hassip |
| 800 to 812 | eight hundred to eight hundred twelve |
| read only | read-only |

QMS, CSQ, QR, CCP, QC and TV are fine as written. To check a word, run
`Kokoro(...).tokenizer.phonemize('word', 'en-us')`. Voice: `af_heart`, speed 1.0.

## Complete minimal example (`sample/make_sample.py`)

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))           # .../video/kit
import hxvideo as hv
from playwright.sync_api import sync_playwright

hv.set_project(HERE)
SNAP = HERE + '/index_snapshot.html'
hv.synth()                                             # narration.py -> tts/

def scene_qms(pw):
    ns = hv.load_setup('qual', snapshot=SNAP)          # (a) seed
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script())
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(600)
    r = hv.Rec(ctx, pg, 'qms'); r.start()
    r.beat('q1', lambda: (r.click(pg.locator('.nav').get_by_role('button', name='QMS', exact=True)),
                          pg.wait_for_selector('text=Needs action'), r.point(pg.get_by_text('Needs action').first, 0.2)))
    def q2():                                          # (b) beat with several actions
        r.click(pg.get_by_role('button', name='+ Report deviation')); pg.wait_for_selector('.md')
        r.type(hv.field(pg.locator('.md'), 'Deviation title'), 'Drum seal broken on receipt')
    r.beat('q2', q2)
    r.stop(); b.close()

def scene_receiving(pw):
    ns = hv.load_setup('supply', snapshot=SNAP)
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script())
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(600)
    r = hv.Rec(ctx, pg, 'receiving'); r.start()
    def r1():
        r.click(pg.locator('.nav').get_by_role('button', name='Receiving', exact=True)); pg.wait_for_selector('tr >> text=RCV-2026-018')
        r.point(pg.locator('tr', has_text='RCV-2026-018'), 0.15)
    r.beat('r1', r1)
    r.stop(); b.close()

with sync_playwright() as pw:                          # (c) several scenes -> one MP4 with chapters
    scene_qms(pw); scene_receiving(pw)
hv.build([('qms', 'Report a deviation'), ('receiving', 'Receiving')], HERE + '/sample.mp4')
```

with `sample/narration.py`:

```python
NARR = [
    ('q1', "Open QMS from the left menu. The dashboard shows open and overdue deviations, and what needs action."),
    ('q2', "Click Report deviation, and give the problem a short title."),
    ('r1', "In Receiving, every delivery is a numbered lot, with its COA and inspection result."),
]
SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('HACCP', 'hassip')]
```

Title or end cards are plain HTML pages served by a route (see `../card.html` and `../scene_card.py`).
To check a build: run `ffprobe` on the MP4, look at a few stills (`ffmpeg -ss T -i out.mp4 -frames:v 1 x.jpg`),
and list the chapters with `ffprobe -show_chapters`.
