# Merivale I/O

Merivale I/O is a puzzle game with computer science elements based on Shenzhen I/O by Zachtronics.

# Features
Merivale I/O has a number of features, which include:
- Music volume control
- A tutorial and credits screen
- Placement and programming of microcontrollers, and placement of wires connecting them
- Simulation of a circuit, with a graph to visualize input/output

## Installation

1. Download the git repository for the project
2. Install all dependencies. They are as follows:

    a. `pygame`: install with [pip](https://pypi.org/project/pip/), used for most game functions.
    ```bash
    pip install pygame
    ```
    b. `pytube`: install with [pip](https://pypi.org/project/pip/), used to download music files.
    ```bash
    pip install pytube
    ```
    c. `glom`: install with [pip](https://pypi.org/project/pip/), used for accessing assets within code.
    ```bash
    pip install glom
    ```
    d. `FFmpeg`: downloads [here](https://ffmpeg.org/download.html), used to convert music files into the right format.  
    Windows users may be able to run:
    ```bash
    winget install ffmpeg
    ```
    On Windows, ensure `ffmpeg` is available in your [PATH](https://superuser.com/a/284351)  
    Linux users may be able to install it from their package managers. With the apt package manager:
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

## Known Bugs
- Wires sometimes fail to place, due to fast movement of mouse which update ticks cannot keep up with.
- WIP

## Cheat Codes
This section contains full solutions to each puzzle. Images are initially hidden, click to reveal.  
  
[//]: # (I learned how to do markdown comments from this stackoverflow post: https://stackoverflow.com/questions/4823468/comments-in-markdown)  
[//]: # (I learned how to make 'spoilered' images from this stackoverflow post: https://stackoverflow.com/questions/32814161/how-to-make-spoiler-text-in-github-wiki-pages)  
  
<details>
    <summary>Puzzle 1</summary>
    <img src="https://i.imgur.com/kTpNVyp.png" alt="Solution to Puzzle 1"></img>
</details>
<details>
    <summary>Puzzle 2</summary>
    <img src="https://i.imgur.com/Do6HsgN.png" alt="Solution to Puzzle 2"></img>
</details>
<details>
    <summary>Puzzle 3</summary>
    <img src="https://i.imgur.com/yOivS7B.png" alt="Solution to Puzzle 3"></img>
</details>
<details>
    <summary>Puzzle 4</summary>
    <img src="https://i.imgur.com/3UKHtF2.png" alt="Solution to Puzzle 4"></img>
</details>

## Support
For any questions, support, or contact, please email me at `jogst1@ocdsb.ca`  
You can also create an issue on the [GitHub repository](https://github.com/Jogst1/ICS3U_Final)

## Sources
See the [reference tracker](https://docs.google.com/document/d/1-7uoMtHautyOPwjpPivfaJ6HS_USsd2cKbdPfraUUYE/edit?usp=sharing)  
Additionally, check out the in-game credits screen.  
There are also sources included throughout the project code.  