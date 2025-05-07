# Standard imports
import asyncio
import random
from typing import Optional

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers
from peer_handshake import perform_handshake
from data_download import request_piece

# Constant to control the number of peers to attempt connection with
MAX_PEER_CONNECTIONS = 2  # Set to -1 to try all peers


async def main():
    """
    Main function to orchestrate the BitTorrent client workflow:
    parsing the torrent, getting peers, performing handshake, and downloading a piece
    from a limited number of peers.
    """
    torrent_file = (
        "example.torrent"  # Replace with the path to your .torrent file
    )
    tracker_url: Optional[str] = None # Initialize tracker_url as None
    info_hash: Optional[bytes] = None # Initialize info_hash as None
    peer_list: list[tuple[str, int]] = [] # Initialize peer_list as None

    # Task 5.1: Parse the torrent file
    # Use the 'parse_torrent' function to extract the tracker URL and info hash from the 'torrent_file'.
    # Assign the returned values to the 'tracker_url' and 'info_hash' variables.
    tracker_url, info_hash = None, None # YOUR CODE HERE
    if tracker_url is None or info_hash is None:
        raise NotImplementedError("Task 5.1: Parsing the torrent file is not implemented.")

    if tracker_url and info_hash:
        print(f"Tracker URL: {tracker_url}")
        print(f"Info Hash: {info_hash.hex()}")

        # Task 5.2: Get peers from the tracker
        # Use the 'get_peers' function with the 'tracker_url' and 'info_hash' to retrieve a list of peers.
        # Assign the returned list to the 'peer_list' variable.
        peer_list = None # YOUR CODE HERE
        if peer_list is None:
            raise NotImplementedError("Task 5.2: Getting peers from the tracker is not implemented.")
        if peer_list:
            print(f"Found {len(peer_list)} peers.")
            random.shuffle(peer_list)
            peers_to_try = (
                len(peer_list)
                if MAX_PEER_CONNECTIONS == -1
                else min(MAX_PEER_CONNECTIONS, len(peer_list))
            )
            downloaded_piece: Optional[bytes] = None # Initialize downloaded_piece as None

            # Task 5.3: Iterate through peers and attempt handshake/download
            for i in range(peers_to_try):
                peer_ip, peer_port = peer_list[i]
                reader: Optional[asyncio.StreamReader] = None # Initialize reader as None
                writer: Optional[asyncio.StreamWriter] = None # Initialize writer as None

                try:
                    print(
                        f"Attempting handshake with {peer_ip}:{peer_port} (Peer {i+1}/{peers_to_try})"
                    )
                    handshake_result = await perform_handshake(
                        peer_ip, peer_port, info_hash
                    )

                    if handshake_result:
                        reader, writer = handshake_result
                        print(f"Handshake successful with {peer_ip}:{peer_port}")

                        # Attempt to download the first piece (index 0) using the 'request_piece' function.
                        # Pass the 'reader', 'writer', and 'piece_index=0'.
                        # Assign the downloaded piece data (or None) to the 'piece' variable.
                        piece = None # YOUR CODE HERE
                        if piece:
                            print(
                                f"Successfully downloaded piece 0 from {peer_ip}:{peer_port}."
                            )
                            downloaded_piece = piece
                            break  # Stop after successfully downloading a piece
                        else:
                            print(
                                f"Failed to download piece 0 from {peer_ip}:{peer_port}."
                            )
                    else:
                        print(f"Handshake failed with {peer_ip}:{peer_port}.")

                except Exception as e:
                    print(f"Error communicating with {peer_ip}:{peer_port}: {e}")
                finally:
                    if writer and not writer.is_closed():
                        try:
                            writer.close()
                            await writer.wait_closed()
                        except Exception as e:
                            print(
                                f"Error closing writer for {peer_ip}:{peer_port}: {e}"
                            )

            if downloaded_piece:
                print("Successfully downloaded a piece from one of the peers.")
            elif peer_list:
                print("Failed to download a piece from any of the attempted peers.")
        else:
            print("No peers found by the tracker.")
    else:
        print("Failed to retrieve tracker URL or info hash.")


if __name__ == "__main__":
    asyncio.run(main())
