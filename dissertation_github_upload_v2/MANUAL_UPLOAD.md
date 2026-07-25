# Manual upload — GitHub web UI drag-and-drop

If you prefer not to use the command line, you can upload this folder
to GitHub entirely through the web browser.

## Steps

1. **Create the repository on GitHub.**
   Log into github.com → click *New repository* → choose a name
   (e.g. `dissertation-envy-psi-purchase`) → make it Public or Private
   as you prefer → do NOT tick "Initialize this repository with a
   README" (this ZIP already contains one) → click *Create repository*.

2. **Extract this ZIP** to a folder on your computer.

3. **Drag the folder contents into the GitHub web UI:**
   - On the new empty repo page, click *uploading an existing file*
     (there is a link on the page).
   - Open Finder / File Explorer in the extracted folder.
   - Select ALL contents (files AND subfolders) inside the extracted
     folder — but not the folder itself — and drag them into the
     GitHub upload area.
   - Wait for the green ticks to appear next to each file.

4. **Commit:** below the file upload area, add a commit message
   ("Initial commit: dissertation code") → click *Commit changes*.

5. **Done.** Your repository is live.

## Verify before you drag

Before dragging, double-check that the extracted folder does NOT contain:
- `.env`, `comments_raw*.csv`, `pseudonym_mapping.csv`, or any
  `validation_*.csv` file. These were excluded by the ZIP-building
  script, but a quick visual check in Finder is worth 10 seconds.

## Alternative — command-line setup

If you have `git` installed and prefer a scripted push, use
`setup_github.sh` in the extracted folder instead. It runs the same
safety checks and pushes in one step.
