# pygyt - Python Gtk frontend of yt-dlp

**pygyt** developed on Ubuntu 22.04 with Python 3.10 and tested on WSL Ubuntu of the same version.

## Installation

- Follow the steps of "**Getting Started**" section in [PyGObject Documentation](https://gnome.pages.gitlab.gnome.org/pygobject/) to setup Python Gtk4 environment.
- Install [ffmpeg](https://ffmpeg.org/) for your system.
- Clone or download the source of [pygyt](https://github.com/twMr7/pygyt) repository.
- (Option 1, not tested) `pip install yt-dlp`, or 
- (Option 2) Clone the [yt-dlp](https://github.com/yt-dlp/yt-dlp) and create a symbolic link in "**pygyt**" folder and link to "**yt_dlp**" folder in the "**yt-dlp**" source tree.

```shell
pygyt
├── DownloadItem.py
├── pygyt_gleaner.png
├── pygyt.py
├── pygyt_wink.png
├── PygytWin.py
├── README.md
├── yt_dlp -> ../yt-dlp_repo/yt_dlp
└── ytdlp_tasks.py
```
