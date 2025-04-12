# Standard imports
import hashlib

# Third-party imports
import bencodepy


def parse_torrent(file_path):
    with open(file_path, "rb") as f:
        torrent_data = bencodepy.decode(f.read())

    info = torrent_data[b"info"]
    info_hash = hashlib.sha1(bencodepy.encode(info)).digest()
    tracker_url = torrent_data[b"announce"]

    print("Tracker URL:", tracker_url.decode())
    print("Info Hash:", info_hash.hex())
    return tracker_url.decode(), info_hash


if __name__ == "__main__":
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"
    tracker_url, info_hash = parse_torrent(torrent_file)
