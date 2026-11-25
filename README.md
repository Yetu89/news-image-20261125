# THE DAILY GLOBE — 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Yetu89/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Yetu89/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One image that sums up the world news of Wednesday, 25 November 2026:
two tankers ablaze after mine strikes in the Strait of Hormuz, Houthi
forces strike Saudi Arabia's biggest oil refinery, Ukrainian drones set
two Russian refineries ablaze, Huawei is found guilty on 10 of 12 counts
in a US trial, Israel kills a Hamas security chief in Gaza, Australia
and the Solomon Islands sign a no-base treaty, and Shenzhou-24 docks
with Pakistan's first astronaut aboard — plus the AI sell-off hitting
Asian stocks, the Dow closing above 50,000, and Wednesday's market
close.

## How it is made

`tools/stories.json` holds the day's stories, briefs and market figures.
`tools/build_image.py` (Pillow plus the standard library) draws the
1024x1024 newspaper front page and writes `entry.png`. `main.py`
(standard library only) copies `entry.png` to `/output/entry.png`
(or `$OUTPUT_DIR/entry.png`).

```sh
python3 tools/build_image.py
python3 main.py
```

The build is deterministic: running `build_image.py` twice produces
byte-identical output, and `main.py` copies the same file every run.

## License

MIT. See `LICENSE`.
