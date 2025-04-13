# Standard imports
import random
from typing import Tuple

# Third-party imports
import requests

# Local imports
from torrent_parser import parse_torrent


def get_peers(tracker_url: str, info_hash: bytes) -> list[Tuple[str, int]]:
    """
    Contacts the tracker at the given URL to retrieve a list of peers.

    Args:
        tracker_url: The URL of the torrent tracker.
        info_hash: The info hash of the torrent.

    Returns:
        list: A list of tuples, where each tuple contains the IP address (string)
              and port (integer) of a peer. Returns an empty list if an error occurs
              or no peers are found.
    """
    peer_id = None  # Initialize peer_id
    params = None  # Initialize params
    response = None  # Initialize response
    peer_list = []  # Initialize peer_list

    # --- Task 2.1: Generate a unique peer ID ---
    # The peer ID is a 20-byte string that identifies this client to the tracker and peers.
    # A common convention is to start with a client identifier. For this exercise, use "-PYEXERCISE-".
    # Append 12 random hexadecimal characters (0-9, A-F) to this identifier to make it unique.
    # Assign the generated 20-byte peer ID (as a string) to the 'peer_id' variable.
    # Hint: Use 'random.choices' and string concatenation.
    peer_id = "-PYEXERCISE-" + "".join(random.choices("0123456789ABCDEF", k=12))

    # --- Task 2.2: Construct the request parameters ---
    # The tracker URL requires specific parameters to be sent in the GET request.
    # Create a dictionary named 'params' with the following keys and values:
    #   - "info_hash": The 'info_hash' (must be the bytes object).
    #   - "peer_id": The 'peer_id' (must be encoded to bytes).
    #   - "port": The port this client is listening on (use 6881).
    #   - "uploaded": The total number of bytes uploaded (start with 0).
    #   - "downloaded": The total number of bytes downloaded (start with 0).
    #   - "left": The number of bytes remaining to download (for simplicity, start with 0).
    #   - "compact": Set to 1 to receive a compact list of peers.
    # Assign this dictionary to the 'params' variable.
    params = {
        "info_hash": info_hash,
        "peer_id": peer_id.encode(),
        "port": 6881,
        "uploaded": 0,
        "downloaded": 0,
        "left": 0,
        "compact": 1,
    }

    try:
        # --- Task 2.3: Make the GET request to the tracker ---
        # Use the 'requests.get()' function to send a GET request to the 'tracker_url'
        # with the 'params' dictionary.
        # Assign the response object to the 'response' variable.
        response = requests.get(tracker_url, params=params)

        # --- Task 2.4: Extract the peer list from the response ---
        # The tracker's response (in 'response.content') contains a compact list of peers.
        # Each peer is represented by 6 bytes: 4 bytes for the IP address and 2 bytes for the port (big-endian).
        # Iterate through the 'response.content' in chunks of 6 bytes.
        # For each 6-byte chunk:
        #   - Extract the first 4 bytes and convert them to an IP address string (e.g., "192.168.1.1").
        #     Hint: Use '.".join(map(str, ...))'.
        #   - Extract the last 2 bytes and convert them to an integer representing the port.
        #     Hint: Use 'int.from_bytes(..., byteorder="big")'.
        #   - Append a tuple of (ip, port) to the 'peer_list'.
        peers = response.content
        peer_list = []
        for i in range(0, len(peers), 6):
            ip_bytes = peers[i : i + 4]
            port_bytes = peers[i + 4 : i + 6]
            ip = ".".join(map(str, ip_bytes))
            port = int.from_bytes(port_bytes, byteorder="big")
            peer_list.append((ip, port))

        print("Peers:", peer_list)

    except requests.exceptions.RequestException as e:
        print(f"Error contacting tracker: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while processing tracker response: {e}")
        return []

    return peer_list


if __name__ == "__main__":
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"
    tracker_url, info_hash = parse_torrent(torrent_file)
    if tracker_url and info_hash:
        peer_list = get_peers(tracker_url, info_hash)
        if peer_list:
            print("Found", len(peer_list), "peers.")
        else:
            print("No peers found.")
