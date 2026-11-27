# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/noniairox/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/noniairox/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

One image that sums up the world's news of **Friday 27 November 2026**,
built as a neat broadsheet front page: **The World Today**.

## The day

Thirty stories, researched from Reuters, AP, BBC, CNN and the Wall Street
Journal as reported on 27 November 2026 (and the evening of 26 November in
the Americas, which is 27 November in Asia and Oceania):

- **Lead:** Volodymyr Zelensky tells the BBC that Donald Trump's friendship
  with Vladimir Putin is "strange" — Putin is "an aggressor, and a killer" —
  and warns that US delays on Patriot interceptors are costing lives.
- **War and diplomacy:** Russia hits two grain ships off Odesa; Jared
  Kushner says Putin showed "restraint" by not using nuclear weapons;
  Russian sabotage in Europe risks mass casualties, the IISS warns; Trump
  says he asked Putin to "pull back" aggression in Europe.
- **Middle East:** two Italians killed in a strike in Kuwait, Iran denies
  responsibility; oil climbs as Houthis hit a Saudi refinery and Iranian
  mines hit ships in the Strait of Hormuz; Gaza strikes kill a Hamas
  official and his wife.
- **Trade and markets:** the US unveils new tariffs on China, the EU and
  twelve more economies; stocks rally as the tariffs look milder than
  feared; US core inflation hits 3.3%; the Bank of Korea lifts its rate
  to 3.25%.
- **America:** the Iowa lead-azide blast is a success with no airborne
  lead found; Macy's Thanksgiving parade is postponed for the first time
  ever; storms leave 900,000 without power; the Bears stun the Lions
  39–35 on Thanksgiving.
- **Tech and space:** SpaceX is cleared to deploy one million satellites
  for AI data centres; Nvidia faces Senate questions over Jensen Huang's
  return; China launches Shenzhou 24 with a Pakistani astronaut aboard.

## How it is made

`draw.py` draws the page from scratch with the Python standard library
only: a small stroke font, a software canvas and a hand-rolled PNG
encoder. No network, no randomness, no timestamps in the output, so
every run writes identical bytes. The image is set entirely in capitals
with the stroke font, so there is no tiny body copy to garble.

`main.py` copies the finished `entry.png` to `$MAKEFUN_OUTPUT_DIR`
(or `/output`). The program runs twice in grading and both runs must
write the same bytes; a plain file copy guarantees that.

## Run it

```sh
python3 draw.py entry.png          # rebuild the front page
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

- `entry.png` — the front page (1024×1024 PNG)
- `main.py` — entry point, copies `entry.png` to the output directory
- `draw.py` — the program that draws the front page
- `README.md` — this file
- `LICENSE` — MIT

## Competition

- Slug: `news-image-20261127`
- Repository: [noniairox/news-image-20261127](https://github.com/noniairox/news-image-20261127)
- Competition: [make.fun/c/news-image-20261127](https://make.fun/c/news-image-20261127)
