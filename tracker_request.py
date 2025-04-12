# Standard imports
import random

# Third-party imports
import requests

# Local imports
from torrent_parser import parse_torrent


def get_peers(tracker_url, info_hash):
    peer_id = "-PYWORKSHOP-" + "".join(random.choices("0123456789ABCDEF", k=12))
    params = {
        "info_hash": info_hash,
        "peer_id": peer_id.encode(),
        "port": 6881,
        "uploaded": 0,
        "downloaded": 0,
        "left": 0,
        "compact": 1,
    }

    response = requests.get(tracker_url, params=params)
    peers = response.content

    # Parse compact peer list (6 bytes per peer: 4 for IP, 2 for port)
    peer_list = []
    for i in range(0, len(peers), 6):
        ip = ".".join(map(str, peers[i : i + 4]))
        port = int.from_bytes(peers[i + 4 : i + 6], byteorder="big")
        peer_list.append((ip, port))

    print("Peers:", peer_list)
    return peer_list


if __name__ == "__main__":
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"
    tracker_url, info_hash = parse_torrent(torrent_file)
    peer_list = get_peers(tracker_url, info_hash)
