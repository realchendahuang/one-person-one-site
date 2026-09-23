# One Person, One Site

> A curated collection of remarkable personal websites, independent blogs, digital gardens, portfolios, and other spaces people truly own on the web.

We believe:

> Everyone deserves a place on the Internet that is truly their own.

This repository is not a collection of website templates. It is a directory of **real people and the websites they maintain over time**.

[中文](./README.md) · [Browse directory](./DIRECTORY.md) · [Contribute](./CONTRIBUTING.md)

## What belongs here?

We welcome:

- Personal websites
- Independent blogs
- Digital gardens
- Portfolios
- Personal knowledge bases
- Creator websites
- Indie hacker websites
- Long-running sites with a strong personal voice

We generally avoid company sites, social profile pages, scraper sites, SEO spam, deceptive websites, and mass-generated content farms with little genuine personal expression.

## How to submit a site

Use the **Submit a site** issue template, or edit `data/sites.json` and open a pull request.

Example entry:

```json
{
  "name": "Site Name",
  "url": "https://example.com",
  "owner": "Creator Name",
  "description": "A short description.",
  "languages": ["en"],
  "region": "Global",
  "tags": ["blog", "developer"],
  "feed": "https://example.com/rss.xml"
}
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full rules.

## Online directory

The directory is published as a fully static website on GitHub Pages:

👉 **https://realchendahuang.github.io/one-person-one-site/**

It is built automatically from `data/sites.json` (GitHub Actions deploys on every push to main) and supports client-side search and tag filtering — no server required.

## Local validation

```bash
python3 scripts/validate.py
python3 scripts/generate_directory.py
python3 scripts/generate_site.py   # build the static site into site/ (gitignored)
```

## License

Code is released under the [MIT License](./LICENSE).
