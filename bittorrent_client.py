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
        "ubuntu-24.04.2-desktop-amd64.iso.torrent"  # Replace with your torrent file
    )
    tracker_url: Optional[str] = None
    info_hash: Optional[bytes] = None
    peer_list: list[tuple[str, int]] = []

    # Task 6.1: Parse the torrent file
    tracker_url, info_hash = parse_torrent(torrent_file)

    if tracker_url and info_hash:
        print(f"Tracker URL: {tracker_url}")
        print(f"Info Hash: {info_hash.hex()}")

        # Task 6.2: Get peers from the tracker
        peer_list = get_peers(tracker_url, info_hash)
        if peer_list:
            print(f"Found {len(peer_list)} peers.")
            random.shuffle(peer_list)
            peers_to_try = (
                len(peer_list)
                if MAX_PEER_CONNECTIONS == -1
                else min(MAX_PEER_CONNECTIONS, len(peer_list))
            )
            downloaded_piece: Optional[bytes] = None

            # Task 6.3: Iterate through peers and attempt handshake/download
            for i in range(peers_to_try):
                peer_ip, peer_port = peer_list[i]
                reader: Optional[asyncio.StreamReader] = None
                writer: Optional[asyncio.StreamWriter] = None

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
                        piece = await request_piece(reader, writer, piece_index=0)
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
