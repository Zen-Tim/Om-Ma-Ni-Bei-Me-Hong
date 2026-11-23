# Om Mani Padme Hom course site

A static website: one landing page and 8 lesson pages. Light theme only.

## What's where

- `public/` — the website itself. This is the only folder Vercel publishes.
  - `index.html` — landing page
  - `lesson-1.html` … `lesson-8.html` — one page per lesson: video, section list, notes, quiz
  - `assets/videos.js` — **the YouTube links for all 8 lessons**
- `tools/build_site.py` — rebuilds the pages from the two source files below.
- `Landing_Page_Mockup_*.html` and `Om_Mani_Padme_Hom_Study_Notes_*.html` — the source files. Not published.

## Add a lesson video

Open `public/assets/videos.js`. Paste the YouTube link between the quotes for that lesson:

```js
3: "https://www.youtube.com/watch?v=abc123XYZ_0",
```

That one line updates the Lesson 3 page and its thumbnail on the landing page.

## Update the notes

Put the new notes file (for example `..._v8.0_...html`) in this folder, then run:

```
python tools/build_site.py
```

The newest notes file wins. Your video links are kept.

## Deploy on Vercel

1. Push this repo to GitHub.
2. In Vercel: Add New → Project → import this repo. Leave every setting as it is.
   `vercel.json` already tells Vercel to publish the `public` folder with no build step.
3. Every push to `main` then updates the live site.

Pages open without `.html` on the live site, for example `/lesson-3`.
