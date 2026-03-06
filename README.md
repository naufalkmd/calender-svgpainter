# calender-svgpainter

Paint your own GitHub-style name banner visually, save it as `canvas.json`, and let GitHub Actions regenerate the banner for you.

## What this is for

This repo is made for one simple flow:

1. Open the visual painter
2. Draw your name or word on the grid
3. Save the new `canvas.json`
4. Push it to GitHub
5. Let the workflow generate the updated banner image
6. Use that image in your profile README

You do not need to edit SVG or GIF files by hand.

## What you will use

- `painter/helper.html`: the visual editor
- `painter/canvas.json`: your saved drawing
- `Assets/github-painter-preview.svg`: grey preview board
- `Assets/github-painter-banner.svg`: transparent static banner
- `Assets/github-painter-banner.gif`: animated glitch banner

## How to paint your own name

Open [painter/helper.html](./painter/helper.html) in your browser.

The board is a GitHub-style grid, so you can paint your text by eye just like a contribution graph.

### Controls

- Drag with the mouse to paint
- Right click to erase a cell
- `space` switches to erase
- `a`, `s`, `d`, `f` switch between the 4 green levels
- `esc` clears the whole board

### Recommended way to draw letters

1. Start with the brightest green for the main letter shape.
2. Leave at least one empty column between letters.
3. Keep letters simple and blocky so they stay readable.
4. Paint the shape first, then add darker shades only if you want extra depth.
5. Use the preview board for spacing and alignment, not the transparent export.

If you are drawing a short name, center it by leaving some empty columns on both sides.

## How to save your drawing

When your design looks right in the helper:

1. Click `Download canvas.json ->`
2. Replace the repo file at `painter/canvas.json` with the downloaded file
3. Commit and push

You can also:

- click `Copy canvas JSON` and paste it into `painter/canvas.json`
- click `Import canvas.json` to load a previous drawing back into the helper
- click `Reload committed canvas` to load the version already in the repo

## How GitHub Actions works

This repo already includes the workflow:

- [painter-banner.yml](./.github/workflows/painter-banner.yml)

After you push a new `painter/canvas.json`, GitHub Actions automatically:

1. reads your updated drawing
2. regenerates the grey preview board
3. regenerates the transparent static banner
4. regenerates the animated glitch GIF banner
5. commits the new generated assets back into the repo

That means your only normal job is to update `painter/canvas.json`. The workflow handles the image generation for you.

## Required GitHub setting

Because the workflow commits generated files back into the repo, you need to enable write access for workflows:

1. Open your repository on GitHub
2. Go to `Settings`
3. Go to `Actions`
4. Open `General`
5. Under `Workflow permissions`, choose `Read and write permissions`
6. Save

If you skip this, the workflow may run but it will not be able to push the updated banner files back to the repository.

## How to run the workflow

### Automatic way

This is the normal flow:

1. Change `painter/canvas.json`
2. Commit and push to `main`
3. GitHub Actions runs automatically

### Manual way

If you want to rerun it manually:

1. Open the repository on GitHub
2. Go to `Actions`
3. Select `GitHub Painter Banner`
4. Click `Run workflow`

## Where the output goes

After the workflow finishes, these files are updated:

- `Assets/github-painter-preview.svg`
- `Assets/github-painter-banner.svg`
- `Assets/github-painter-banner.gif`

Use them like this:

- `github-painter-preview.svg`: full grey-board preview, useful for checking layout
- `github-painter-banner.svg`: transparent static banner
- `github-painter-banner.gif`: animated glitch banner for your README

## How to use the banner in your README

Use the animated GIF at the top of your profile or project README:

```html
<p align="center">
  <img src="https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/Assets/github-painter-banner.gif" alt="GitHub Painter banner" width="100%" />
</p>
```

If you want the non-animated version instead, use `Assets/github-painter-banner.svg`.

## Typical workflow

1. Open `painter/helper.html`
2. Paint your name
3. Download `canvas.json`
4. Replace `painter/canvas.json`
5. Commit and push
6. Wait for `GitHub Painter Banner` to finish
7. Use the generated GIF banner in your README

## Tips

- Keep the letters wide and simple
- Avoid packing too many words into one row
- Use darker shades only as accents
- Check the generated preview after each push
- If the output looks off, repaint in the helper and push again
