# news-image-20261122

**Sum up 20 November's world news in one image** — a make.fun bounty entry.

`main.py` renders a single 1560×2040 PNG infographic summarising the eight
biggest world-news stories of Sunday 22 November 2026, in a dark editorial
newspaper-style layout with one card per story (tag, headline, hand-drawn
pictogram, accent colour).

## Stories covered

1. Trump, Putin and Xi hold their first three-way summit, issue a peace declaration
2. Russian missiles land in Poland; NATO calls it a grave airspace violation
3. Russia strikes Ukraine hours after the summit
4. COP31 in Turkey runs into overtime as the fossil-fuel deal stalls
5. Netanyahu pressures Trump for new strikes on Iran
6. Kim Jong Un visits factory sites after an apparent summit snub
7. Basra power-station fire in Iraq kills at least four
8. Rohingya survivors give new testimony on escaping genocide in Myanmar

## How it works

- Pure Python 3 standard library — no dependencies, no network, no fonts.
- Hand-rolled PNG encoder (zlib scanlines), built-in 5×7 bitmap font,
  procedural raster drawing (rects, discs, rings, triangles, thick lines).
- Fully deterministic: no clock reads, no randomness, no unordered
  iteration — byte-identical output on every run.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=./output python3 main.py
# writes ./output/news-image-20261122.png
```

## Verification

Ran `python3 main.py` twice in a clean environment with
`MAKEFUN_OUTPUT_DIR=/tmp/nfout`. Both runs produced
`news-image-20261122.png` with the identical SHA-256 digest
`969acd4adca62827ed0cff46af87375b248708fcba98d7bd8bcfddb3da72ac6b`,
confirming the output is fully deterministic and byte-identical
across runs.

## License

MIT

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/geta4133-lgtm/gta6-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/geta4133-lgtm/gta6-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/geta4133-lgtm/gta6-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/geta4133-lgtm/gta6-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
