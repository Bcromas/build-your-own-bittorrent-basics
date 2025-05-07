# build-your-own-bittorrent-basics
This repository guides you through the implementation of some basic BitTorrent functionality: parsing torrent metadata, communicating with trackers for peer discovery, establishing peer connections via handshakes, and downloading data pieces.

**This repository contains two branches:**

* **`exercise`**: This is the branch you should work in. It contains the initial file structure and prompts to guide your implementation.
* **`solution`**: This branch provides a complete, functional example of the BitTorrent basics implemented in this repository. You can refer to this branch if you get stuck or want to see how the code should work.

## Setup Instructions
### Install Python
Ensure Python 3.6+ is installed on your machine. You can download the latest version from the official Python website (https://www.python.org/downloads/).

### Clone the GitHub Repository
Clone the repository containing the project files to your local machine using the following command:
```bash 
git clone https://github.com/Bcromas/build-your-own-bittorrent-basics.git
cd build-your-own-bittorrent-basics
```

### Create a Virtual Environment
It's highly recommended to create a virtual environment to isolate the project's dependencies. Navigate to the project directory in your terminal or command prompt and run the following command to create a virtual environment named .venv:
```bash
python -m venv .venv
```

This command creates a new hidden directory named .venv (the leading dot makes it hidden on Unix-like systems) containing a copy of the Python interpreter and necessary supporting files.

### Activate the Virtual Environment
Before installing any libraries, you need to activate the virtual environment.

On macOS and Linux:
```bash 
source .venv/bin/activate
```

On Windows:
```bash 
.\.venv\Scripts\activate
```

Your command prompt should now be prefixed with (.venv), indicating that the virtual environment is active.

### Install Required Libraries from requirements.txt
The repository includes a requirements.txt file that lists the necessary Python libraries. With the virtual environment activated, run the following command in your terminal to install these dependencies:
```bash
pip install -r requirements.txt
```

This command will read the requirements.txt file and install the latest compatible versions of the required libraries (e.g., bencodepy, requests, asyncio) within your isolated virtual environment.

### Obtain a Local .torrent File
To run the code in this repo, you'll need a local .torrent file in the project directory. It's crucial to use a small, legal, and reliably seeded torrent. A good option is an Ubuntu ISO torrent. You can download one from the Ubuntu website: https://ubuntu.com/download/alternative-downloads (look for the "Torrent" links). Place this file in the same directory as the Python scripts.

## Start Implementing
Finish the implementation by working through the files and following the prompts. The recommended order is:
1. torrent_parser.py
1. tracker_request.py
1. peer_handshake.py
1. data_download.py
1. bittorrent_client.py

# Helpful Resources
[Building a BitTorrent Client - Jesse Li](https://roadmap.sh/guides/torrent-client) **Recommended**

[How to Write a Bittorrent Client, Part 1 - Kristen Widman](http://www.kristenwidman.com/blog/33/how-to-write-a-bittorrent-client-part-1/)

[Unofficial BitTorrent Specification](https://wiki.theory.org/BitTorrentSpecification)
