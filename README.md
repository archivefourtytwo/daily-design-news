# DDN — Daily Design News

Minimal, mono-only static editorial site for GitHub Pages. Despite the name, DDN publishes **one focused feature per week**.

## Editorial rotation
Current queue:
1. Mantissa
2. Vincent Langaard
3. Archive42
4. Lake Hills
5. Sarah Sprosec
6. Archive42

That places Archive42 roughly every third week. Add future subjects to `data/designers.json` and place their slug wherever you want in `data/rotation.json`.

## Weekly publishing
`.github/workflows/weekly.yml` runs every **Friday at 09:17 Europe/Vienna** and generates one new article, then rebuilds the index, RSS feed and sitemap.

## Design
- system monospace stack only
- monochrome / warm white
- no external font requests
- responsive
- deliberately minimal editorial index

## Editorial sourcing
Each profile uses curated copy from `data/designers.json`, links to the subject's primary source, and can append current external links found via public Google News RSS. It does not invent press coverage.

## Disclosure
DDN is published by Archive42. This is disclosed quietly on the About page. Archive42 self-features receive an additional disclosure inside the article.

## Publish on GitHub Pages
1. Put this folder into a public repository.
2. Set Pages to **GitHub Actions**.
3. Set the repository variable `SITE_URL` to `https://archivefourtytwo.github.io/daily-design-news` if you want to override the built-in default.
4. Run `Publish weekly DDN feature` once manually if you want to test it.
