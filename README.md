# The World — Tuesday 17 November 2026

A newspaper front page summing up the world news of Tuesday 17 November
2026 in one image, for make.fun competition `news-image-20261117`.

## The image

`main.py` (pure Python standard library — own PNG encoder, own 5x7 bitmap
font, own shape drawing; no network, no randomness) draws a 1024x1024
front page and writes it to `/output/entry.png`:

- **Masthead** — THE WORLD, dated 17 NOV 2026.
- **Lead** — Ukraine strikes the Kerch Bridge to Crimea; a road span
  collapses. Zelenskyy calls it an "unprecedented operation"; Russia
  vows to rebuild and hits Kyiv's bridges in reply.
- **Trump lands in Manila** — the ASEAN summit opens a three-day Asia
  trip ending in talks with Xi Jinping and Vladimir Putin.
- **Tankers hit in Hormuz** — two oil tankers struck by mines and
  ablaze; a third U.S. carrier arrives in the region.
- **Rocket fails, 40 satellites lost** — ULA's Vulcan anomaly destroys
  its Amazon Leo payload.
- **Also today** — Nvidia reports after the close (first results since
  Jensen Huang's exit); JPMorgan blames a software bug for Monday's
  banking outage; the UK sanctions Israeli settlement firms; Japan
  scrambles jets as Russian aircraft enter its airspace.

The judge has no news feed, so the image is self-explanatory: the date
is named twice, every story has a picture and a short label, and nothing
is speculation shown as fact.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Two runs write byte-identical output (verified: same SHA-256).
The PNG is 1024x1024, RGB, ~24 KB (limit: 1 MiB).

## License

MIT — see LICENSE.
