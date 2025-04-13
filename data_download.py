# Standard imports
import asyncio
import random
from typing import Optional

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers
from peer_handshake import perform_handshake


# Define default timeout values as constants
MAX_PEER_CONNECTIONS = 2  # Set to -1 to try all peers
PIECE_RESPONSE_PREFIX_TIMEOUT = 25
PIECE_DATA_TIMEOUT = 40


async def request_piece(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    piece_index: int,
    piece_prefix_timeout: float = PIECE_RESPONSE_PREFIX_TIMEOUT,
    piece_data_timeout: float = PIECE_DATA_TIMEOUT,
) -> Optional[bytes]:
    """
    Requests and downloads a specific piece of data from a connected peer.

    Sends a 'request' message to the peer for the given piece index and then
    attempts to read the corresponding piece data. Handles timeouts during the
    process.

    Args:
        reader: The asyncio StreamReader object for reading from the peer.
        writer: The asyncio StreamWriter object for writing to the peer.
        piece_index: The index of the piece to request (integer).
        piece_prefix_timeout: Timeout in seconds to wait for the initial 4-byte
                              length prefix of the response (float).
                              Defaults to PIECE_RESPONSE_PREFIX_TIMEOUT.
        piece_data_timeout: Timeout in seconds to wait for the complete piece
                            data after receiving the prefix (float).
                            Defaults to PIECE_DATA_TIMEOUT.

    Returns:
        The downloaded piece data as bytes if successful, otherwise None
        (e.g., due to timeout or connection issues).
    """
    try:
        print(
            f"Requesting piece {piece_index} from {reader.get_extra_info('peername')}"
        )
        length_prefix = (13).to_bytes(4, byteorder="big")
        message_id = (6).to_bytes(1, byteorder="big")
        offset = (0).to_bytes(4, byteorder="big")
        block_length = (16384).to_bytes(4, byteorder="big")

        request_msg = (
            length_prefix
            + message_id
            + piece_index.to_bytes(4, byteorder="big")
            + offset
            + block_length
        )

        writer.write(request_msg)
        await writer.drain()

        # Use piece_prefix_timeout
        try:
            response_prefix = await asyncio.wait_for(
                reader.read(4), timeout=piece_prefix_timeout
            )
        except asyncio.TimeoutError:
            print(
                f"Timeout waiting for piece data prefix from {reader.get_extra_info('peername')} after {piece_prefix_timeout} seconds"
            )
            return None

        if not response_prefix:
            print(
                f"Peer {reader.get_extra_info('peername')} closed connection prematurely"
            )
            return None

        message_length = int.from_bytes(response_prefix, byteorder="big")
        # Use piece_data_timeout
        try:
            piece_data = await asyncio.wait_for(
                reader.read(message_length - 9), timeout=piece_data_timeout
            )
        except asyncio.TimeoutError:
            print(
                f"Timeout waiting for full piece data from {reader.get_extra_info('peername')} after {piece_data_timeout} seconds"
            )
            return None

        if piece_data:
            print(
                f"Downloaded {len(piece_data)} bytes from piece {piece_index} from {reader.get_extra_info('peername')}"
            )
        return piece_data

    except asyncio.TimeoutError:
        print(
            f"Timeout waiting for piece data from {reader.get_extra_info('peername')}"
        )
        return None
    except Exception as e:
        print(f"Error requesting/downloading piece: {e}")
        return None


async def download_piece(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    piece_index: int,
) -> Optional[bytes]:
    """
    Attempts to download a specific piece from a peer, relying on request_piece.

    Args:
        reader: The asyncio StreamReader object for reading from the peer.
        writer: The asyncio StreamWriter object for writing to the peer.
        piece_index: The index of the piece to download.

    Returns:
        The downloaded piece data as bytes if successful, otherwise None.
    """
    return await request_piece(reader, writer, piece_index)


async def main():
    """
    Main function to orchestrate peer connection and piece download.
    """
    torrent_file = (
        "ubuntu-24.04.2-desktop-amd64.iso.torrent"  # Replace with your torrent file
    )
    tracker_url, info_hash = parse_torrent(torrent_file)
    peer_list = get_peers(tracker_url, info_hash)

    if not peer_list:
        print("No peers found.")
        return
    else:
        random.shuffle(peer_list)  # randomly shuffle list to try different peers

    peers_to_try = (
        len(peer_list)
        if MAX_PEER_CONNECTIONS == -1
        else min(MAX_PEER_CONNECTIONS, len(peer_list))
    )
    downloaded_piece: Optional[bytes] = None

    for i in range(peers_to_try):
        peer_ip, peer_port = peer_list[i]
        reader: Optional[asyncio.StreamReader] = None
        writer: Optional[asyncio.StreamWriter] = None

        try:
            print(
                f"Attempting handshake with {peer_ip}:{peer_port} (Peer {i+1}/{peers_to_try})"
            )
            handshake_result = await perform_handshake(peer_ip, peer_port, info_hash)
            if handshake_result:
                reader, writer = handshake_result
                print(f"Handshake successful with {peer_ip}:{peer_port}")
                piece = await download_piece(reader, writer, piece_index=0)
                if piece:
                    print(
                        f"Successfully downloaded piece 0 from {peer_ip}:{peer_port}."
                    )
                    downloaded_piece = piece
                    break  # Stop after successfully downloading a piece
                else:
                    print(f"Failed to download piece 0 from {peer_ip}:{peer_port}.")
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
                    print(f"Error closing writer for {peer_ip}:{peer_port}: {e}")

    if downloaded_piece:
        print("Successfully downloaded a piece from one of the peers.")
    elif peer_list:
        print("Failed to download a piece from any of the attempted peers.")


if __name__ == "__main__":
    asyncio.run(main())
