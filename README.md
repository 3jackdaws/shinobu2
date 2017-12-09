# Shinobu ][
Shinobu 2 is a modular Discord bot that is built using the discord.py framework.  Shinobu is inspired by NadekoBot a Discord bot writen in C#.  

# Features
* Runtime module loading and reloading.
* Extreme extensibility
* Powerful command parsing

# Modules
Shionobu comes with several modules installed by default.
## Audio
* Play music in voice channels. 
* Download Soundcloud tracks and upload them directly to a channel.

## Admin
* Ban Members based on id
* Filter messages based on regular expressions, apply an action (remove, ban, kick) upon matching text.
* Pin messages to a channel

## Service
* Run native bash commands and post the output to a channel
* Post a random cat picture
* Activate a unique message filter (removes non-unique messages)

# Commands

## Admin

```
pin - pin a message to the current channel
Usage: pin <message id>
Options:
    --remove      (Unpins a message.)
```

```
status - change the status of Shinobu
Usage: status [-g <Game Name>] [--idle | --active]
Options:
    --idle              (Sets Shinobu to idle.)
    --active            (Sets Shinobu to active.)
    --game <game name>  (Sets Shinobu's currently played game.)
```
