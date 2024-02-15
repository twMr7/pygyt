# pygyt - Python Gtk frontend of yt-dlp

**Pygyt** developed on Ubuntu 22.04 with Python 3.10 and tested on WSL Ubuntu of the same version with [WSLg](https://github.com/microsoft/wslg) available.

![screenshot](/assets/Screenshot.png)

## Installation

- Follow the steps of "**Getting Started**" section in [PyGObject Documentation](https://gnome.pages.gitlab.gnome.org/pygobject/) to setup Python Gtk4 environment.
- Install [ffmpeg](https://ffmpeg.org/) for your system, e.g. `sudo apt install ffmpeg` on Ubuntu.
- Clone or download the source of [pygyt](https://github.com/twMr7/pygyt) repository.
- Clone the [yt-dlp](https://github.com/yt-dlp/yt-dlp) and create a symbolic link in "**pygyt**" folder and link to "**yt_dlp**" folder in the "**yt-dlp**" source tree.

```shell
pygyt
├── assets
│   ├── pygyt_gleaner.png
│   ├── pygyt_wink.png
│   └── Screenshot.png
├── DownloadItem.py
├── pygyt.py
├── PygytWin.py
├── README.md
├── yt_dlp -> ../yt-dlp_repo/yt_dlp
└── ytdlp_tasks.py
```

---

Images used in Pygyt are created with *Microsoft Copilot Designer*.