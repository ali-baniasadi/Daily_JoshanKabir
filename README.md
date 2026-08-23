# Daily Joshan Kabir

Telegram bot for `@Daily_JoshanKabir`.

## What it does

- Sends exactly one section per day.
- Starts at section 1.
- Advances only after Telegram confirms successful delivery.
- Sends sections in strict order: 1 → 2 → ... → 100.
- Stops advancing after section 100.
- Appends:
  `🆔 @Daily_JoshanKabir | دعای جوشن کبیر`
- Uses a local JSON dataset after the one-time bootstrap.
- No daily scraping is required.

## Source

The one-time bootstrap uses Setare's complete page containing the Arabic text and Persian
translation of all 100 sections:
https://setare.com/fa/news/8699/

The page states that the prayer has 100 sections and presents the full Arabic text with
Persian translation.

## Setup

1. Create a Telegram bot with BotFather.
2. Add it as administrator to `@Daily_JoshanKabir` with permission to post messages.
3. Put the project in GitHub.
4. Add repository secret:
   `TELEGRAM_BOT_TOKEN`
5. Open Actions and run **Daily Joshan Kabir** manually once.

The workflow automatically builds and validates `data/joshan_kabir.json` if it is empty or
incomplete, then sends the current section and commits the dataset/state.

## Schedule

`30 4 * * *` = 04:30 UTC, which is 08:00 Iran time while Iran is UTC+3:30.

GitHub Actions cron is UTC.
