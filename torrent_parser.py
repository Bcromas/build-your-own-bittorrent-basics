# Standard imports
import hashlib
from typing import Optional, Tuple

# Third-party imports
import bencodepy


def parse_torrent(file_path: str) -> Tuple[Optional[str], Optional[bytes]]:
    """
    Parses a .torrent file to extract the tracker URL and info hash.

    Args:
        file_path: The path to the .torrent file.

    Returns:
        A tuple containing the tracker URL (string) and the info hash (bytes).
        Returns (None, None) if the file is not found, cannot be decoded,
        or if essential keys are missing.
    """
    tracker_url = None  # Initialize tracker_url as None
    info_hash = None  # Initialize info_hash as None

    try:
        with open(file_path, "rb") as f:
            torrent_data = bencodepy.decode(f.read())

        # --- Task 1.1: Extract the 'info' dictionary ---
        # The 'info' dictionary contains metadata about the torrent's files.
        # Assign the decoded value associated with the key 'b"info"' from 'torrent_data' to the variable 'info_dict'.
        info_dict = torrent_data.get(b"info")
        if info_dict is None:
            raise NotImplementedError(
                "Task 1.1: Extracting the 'info' dictionary is not implemented."
            )

        # --- Task 1.2: Calculate the info hash ---
        # The info hash is the SHA1 hash of the bencoded info dictionary.
        # Bencode the 'info_dict' using 'bencodepy.encode()'.
        bencoded_info = bencodepy.encode(info_dict)
        # Calculate the SHA1 hash of the bencoded data using 'hashlib.sha1()'.
        sha1_hash = hashlib.sha1(bencoded_info)
        # Get the digest of the hash using '.digest()'.
        # Assign the resulting bytes object to the 'info_hash' variable.
        info_hash = sha1_hash.digest()
        if info_hash is None:
            raise NotImplementedError(
                "Task 1.2: Calculating the info hash is not fully implemented."
            )

        # --- Task 1.3: Extract the tracker URL ---
        # The tracker URL is associated with the key 'b"announce"'.
        # Decode the byte string value associated with 'b"announce"' from 'torrent_data' to a UTF-8 string.
        # Assign the resulting string to the 'tracker_url' variable. Ensure you decode using 'utf-8' encoding.
        announce_bytes = torrent_data.get(b"announce")
        if announce_bytes:
            tracker_url = announce_bytes.decode("utf-8")
            if tracker_url is None:
                raise NotImplementedError(
                    "Task 1.3: Decoding the tracker URL is not implemented."
                )
        else:
            print("Warning: 'announce' key not found in torrent file.")

    except FileNotFoundError:
        print(f"Error: Torrent file not found at {file_path}")
    except bencodepy.DecodingError:
        print(
            f"Error: Could not decode torrent file at {file_path}. Invalid bencode format."
        )
    except KeyError as e:
        print(f"Error: Missing key in torrent file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return tracker_url, info_hash


if __name__ == "__main__":
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"

    tracker_url, info_hash = parse_torrent(torrent_file)

    if tracker_url and info_hash:
        print("Parsed Tracker URL:", tracker_url)
        print("Parsed Info Hash:", info_hash.hex())
    else:
        print("Parsing the torrent file failed or some tasks are not yet implemented.")
