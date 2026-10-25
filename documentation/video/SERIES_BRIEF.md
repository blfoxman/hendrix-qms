# Hendrix QMS training video series: brief for chapter video makers

## Goal
Make ONE narrated training video for one chapter of the Hendrix QMS User Manual. It must show, in the real app, how to do the main tasks of every module in that chapter.

- **Chapters:** one MP4 chapter marker per module, so viewers can jump to the module they use.
- **Viewer:** a facility employee (production tech, QA, manager) learning the module.
- **Tone:** calm, plain, practical ("To report a deviation, click…").

## Inputs
- **Kit:** read `scratchpad/video/kit/KIT.md` first. The kit is `scratchpad/video/kit/hxvideo.py`; use it exactly as the guide says. It has the recorder, visible cursor, beats, TTS, captions, build, chapters and loudness.
- **Facts:** take them from `scratchpad/manual/ch_<group>.md`, the accurate user manual chapter for your modules. Narrate only what the screens really do.
- **Selectors and seed data:** use `scratchpad/manual/shots_<group>.py`. Everything before `with sync_playwright()` is setup; load it with `hv.load_setup('<group>', ...)`. The rest of the script shows verified selectors for every form.
- **App snapshot:** `scratchpad/video/index_snapshot2.html`. It is the current app, including the Line Map. Do not read or serve `/home/claude/hendrix/index.html` directly.

## Rules
- **Working folder:** only `scratchpad/video/series/<NN>_<group>/`. Final files go to `scratchpad/video/series/<NN> - <Chapter title>.mp4` and `.srt`.
- **Do not modify** anything else: `/home/claude/hendrix`, `manual/`, `mock_c.py`, `test_*.py`, the kit, or the tutorial.
- **Length:** about 60 to 120 seconds per module, giving a total of roughly 8 to 14 minutes.
- **Per module:**
  - a one-line purpose;
  - the 1 to 3 most important tasks, with forms filled in realistically and saved where the mock supports it;
  - one "Hendrix checks" rule (what it blocks);
  - a one-line tip if useful.
- **Card scenes:** start with a short title card ("Hendrix QMS training · Video NN · <title>", with the modules listed) and end with an end card ("Next: Video NN+1 · <next title>" and "Full details in the User Manual, Chapter NN+1").
- **Numbering:** the video number and the manual chapter number differ by one, because manual Chapter 1 is "Getting started". Never use the word "Chapter" for the video number, including in the narration.
- **Chapter titles:** match the left-menu names in the chapter markers ("Suppliers", "Receiving", …), plus "Introduction" and "Wrap-up".
- **Recording quality:** viewport and frames exactly as the kit does (1920x1080). Visible cursor. Captions burned in, and a separate `.srt`.
- **Pronunciation:** use the kit's respellings (CAPA, COA, SKU, CSV, HACCP …) and add your own where needed.
- **The mock:** it doesn't number records or stamp users and times. Where a saved record would show "undefined", fill those fields the way the existing scene scripts in `scratchpad/video/scene*.py` do.
- **CPU:** this machine has 2 cores and other recordings may be running. Use the kit's low-priority, 2-thread encoding. Never run more than one browser recording at a time in your own work.

## Check before finishing
- Run `ffprobe` and confirm the duration, the streams and the chapters.
- Extract about 10 stills spread across the video and look at them with the Read tool. Confirm the cursor, captions and correct screens. There must be no blank frames, no "undefined", no error messages, and no captions covering the thing being explained.
- Fix anything wrong.

## Reply
Reply briefly with:
- the file paths and the duration;
- the chapter list with timestamps;
- anything you could not show.
