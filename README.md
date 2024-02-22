# Pygyt - Python Gtk frontend of yt-dlp

**Pygyt** developed on Ubuntu 22.04 with Python 3.10 and tested on WSL Ubuntu of the same version with [WSLg](https://github.com/microsoft/wslg) available.

## Installation

- Follow the steps of "**Getting Started**" section in [PyGObject Documentation](https://gnome.pages.gitlab.gnome.org/pygobject/) to setup Python Gtk4 environment. You may need to install additional mesa libraries and fonts to eliminate Gtk warning messages.
- Install [ffmpeg](https://ffmpeg.org/) for your system, e.g. `sudo apt install ffmpeg` on Ubuntu.
- Clone the [pygyt](https://github.com/twMr7/pygyt) repository. `git clone https://github.com/twMr7/pygyt.git`
- Clone the [yt-dlp](https://github.com/yt-dlp/yt-dlp)  repository. `git clone https://github.com/yt-dlp/yt-dlp.git`
- Create a symbolic link in "**pygyt**" folder and link to "**yt_dlp**" folder in the "**yt-dlp**" source tree.

```shell
pygyt
├── assets
│   ├── pygyt_gleaner.png
│   ├── pygyt_wink.png
│   ├── screenshot_ubuntu.png
│   └── screenshot_windows.png
├── DownloadItem.py
├── pygyt.py
├── PygytWin.py
├── README.md
├── yt_dlp -> ../yt-dlp_repo/yt_dlp
└── ytdlp_tasks.py
```

## Screenshots

![pygyt_on_ubuntu](/assets/screenshot_ubuntu.png)

![pygyt_on_windows](/assets/screenshot_windows.png)

---

Some images used in *Pygyt* are created with *Microsoft Copilot Designer*.