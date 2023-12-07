# Discord Standup Bot

A Discord Bot for keeping track of who joined and who didn't join a Discord
voice channel, and who has spoken.

## Usage

1. Add the bot to your server/guild
2. Join any voice channel in the server/guild
3. Type `/start_standup` to start a standup
4.

## Running the bot locally

```sh
poetry install
poetry shell
python src/main.py
```

## Limitations

+ In-memory
+ Only 1 standup per server at a time
