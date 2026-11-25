# THE DAILY GLOBE — Wednesday, 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Yetu89/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Yetu89/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A single front page that sums up the world news of Wednesday,
25 November 2026. The lead: two oil tankers are left ablaze after
mine strikes in the Strait of Hormuz, and Brent crude slides. Also
on the page: the Houthi strike on Saudi Arabia's Ras Tanura
refinery, Ukrainian drones setting two Russian refineries alight,
the Huawei verdict in New York, the killing of Hamas security
chief Mohammad Abuelouf in Gaza, the Australia–Solomon Islands
no-base treaty, and Shenzhou-24 docking with Pakistan's first
astronaut aboard — with the AI sell-off across Asian markets, the
Dow's first close above 50,000, and the Wednesday closes below.

## How the page is painted

- `tools/stories.json` — the day's stories, briefs and closes.
- `tools/build_image.py` — Pillow plus the standard library; it
  paints the 1024x1024 front page and saves `entry.png`.
- `main.py` — standard library only; it checks `entry.png`
  (exists, is a PNG, fits the 1 MiB gate) and copies it to
  `/output/entry.png`, or to `$OUTPUT_DIR/entry.png`.

```sh
python3 tools/build_image.py
python3 main.py
```

Running `build_image.py` twice paints byte-identical output, and
`main.py` verifies the copy with a SHA-256 digest every run.

## Verification

- `entry.png`: 1024x1024 PNG, 155,560 bytes (under the 1 MiB gate).
- SHA-256: `588a4d818e7aa61aebef87e70e9fe187d8e2d37d46db7a87c61f5e7f0d9115cd`
  (identical across two runs of `tools/build_image.py`).
- `main.py` copies the same bytes to the output directory and
  confirms the digest matches before reporting success.

## License

MIT. See `LICENSE`.
