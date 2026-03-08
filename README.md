# calender-svgpainter

Fork this repo, paint a GitHub-style banner in the visual helper, commit `painter/canvas.json`, and let GitHub Actions generate the SVG and GIF assets for your fork.

![GitHub Painter Banner](./Assets/github-painter-banner.gif)

## What you edit

- `painter/helper.html`: local visual editor
- `painter/canvas.json`: the only file you normally change by hand
- `Assets/github-painter-preview.svg`: generated full-board preview
- `Assets/github-painter-banner.svg`: generated transparent static banner
- `Assets/github-painter-banner.gif`: generated animated banner

You do not need to edit SVG or GIF files manually. The workflow regenerates them from `painter/canvas.json`.

## Fork-first workflow

### 1. Fork the repository

Create your own fork on GitHub so the generated banner files live in a repo you control.

### 2. Enable workflow write access in your fork

The workflow commits generated assets back into the repository, so your fork must allow GitHub Actions to write:

1. Open your fork on GitHub.
2. Go to `Settings`.
3. Go to `Actions`.
4. Open `General`.
5. Under `Workflow permissions`, choose `Read and write permissions`.
6. Save.

### 3. Open the painter and draw

Open [painter/helper.html](./painter/helper.html) in your browser.

Controls:

- Drag to paint
- Right click to erase
- `space` switches to erase
- `a`, `s`, `d`, `f` switch between the 4 green levels
- `esc` clears the board

Useful helper actions:

- `Reload committed canvas` loads the current repo version
- `Import canvas.json` loads a saved drawing
- `Copy canvas JSON` copies the current canvas data
- `Download canvas.json ->` exports the file you should commit

### 4. Replace `painter/canvas.json`

When the drawing looks right:

1. Click `Download canvas.json ->`.
2. Replace `painter/canvas.json` in your fork with the downloaded file.
3. Commit the change.
4. Push it to `main`.

The included workflow listens for pushes to `main`, so committing `painter/canvas.json` there is the simplest path.

### 5. Let GitHub Actions generate the assets

After your push, the [`GitHub Painter Banner`](./.github/workflows/painter-banner.yml) workflow will:

1. read `painter/canvas.json`
2. regenerate `Assets/github-painter-preview.svg`
3. regenerate `Assets/github-painter-banner.svg`
4. regenerate `Assets/github-painter-banner.gif`
5. commit those generated files back into your fork

Your normal job is to update `painter/canvas.json`. The workflow handles the rendered outputs.

## Commit loop

This is the full repeatable loop:

1. Open `painter/helper.html`.
2. Paint or revise the banner.
3. Export `canvas.json`.
4. Replace `painter/canvas.json`.
5. Commit and push to `main` in your fork.
6. Wait for `GitHub Painter Banner` to finish.
7. Use the generated asset URL in your profile README or project README.

If you want to rerun rendering without making a new commit, open `Actions`, select `GitHub Painter Banner`, and click `Run workflow`.

## Use the generated banner in a README

Point your README image tag at the asset inside your fork:

```html
<p align="center">
  <img
    src="https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/Assets/github-painter-banner.gif"
    alt="GitHub Painter banner"
    width="100%"
  />
</p>
```

Use `Assets/github-painter-banner.svg` instead if you want the static version.

## Drawing tips

- Keep letters wide and blocky so they stay readable
- Leave at least one empty column between letters
- Start with the brightest green for the main letter shape
- Use darker shades only as accents
- Check `Assets/github-painter-preview.svg` after each run if spacing looks off
