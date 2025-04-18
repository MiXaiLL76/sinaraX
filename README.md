# SinaraX is a TUI for the [sinaraml](https://github.com/4-DS/sinaraml) library

[![license](https://img.shields.io/github/license/MiXaiLL76/sinaraX.svg)](https://github.com/MiXaiLL76/sinaraX/blob/main/LICENSE)

| lib      | pypy                                                                                     |
| -------- | ---------------------------------------------------------------------------------------- |
| SinaraX  | [![SinaraX](https://img.shields.io/pypi/v/sinarax)](https://pypi.org/project/sinarax)    |
| sinaraml | [![sinaraml](https://img.shields.io/pypi/v/sinaraml)](https://pypi.org/project/sinaraml) |
| textual  | [![textual](https://img.shields.io/pypi/v/textual)](https://pypi.org/project/textual)    |

## Install

```bash
pip install sinaraX
```

or install dev version

```bash
pip install git+https://github.com/MiXaiLL76/sinaraX.git -U
```

## Motivation

It is convenient to have a cli, but it is even more convenient to have a graphical interface for managing this cli.
As a regular user of [sinaraml](https://github.com/4-DS), I have developed a basic version of the sinaraX library.
It covers the capabilities of managing servers in [sinaraml](https://github.com/4-DS/sinaraml) without using commands in the console.

## Screens

### Main

- Move to server screen
- Move to update screen
- Check system for sinaraml
- Exit

### Server

- Create server (`sinara server create ...`)
- Remove server (`sinara server remove ...`)
- Start server (`sinara server start ...`)
- Stop server (`sinara server stop ...`)
- HELP (`sinara server -h`)
- Update images (`sinara server update ...`)
- Get config (**print used config to log**)
- Save config (**save config to ~/.sinaraX folder**)
- Back (**back to main screen**)
- Exit

### Update

- Update sinaracli (`pip install sinaraml --upgrade`)
- Update sinaraX (`pip install sinaraX --upgrade`)
- Back (**back to main screen**)
- Exit

## Quick Start

```bash
SinaraX
```

### Main Screen

![Main](https://raw.githubusercontent.com/MiXaiLL76/sinaraX/main/images/main.svg)

### Server Screen

![Server](https://raw.githubusercontent.com/MiXaiLL76/sinaraX/main/images/server.svg)

### Update Screen

![Update](https://raw.githubusercontent.com/MiXaiLL76/sinaraX/main/images/update.svg)
