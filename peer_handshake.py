# Standard imports
import asyncio
import random
import socket
from typing import Optional, Tuple

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers

# Define default attempt/timeout values as constants
MAX_ATTEMPTS = 2
CONNECT_TIMEOUT = 15
HANDSHAKE_RESPONSE_TIMEOUT = 20


async def perform_handshake(
    peer_ip: str,
    peer_port: int,
    info_hash: bytes,
    connect_timeout: float = CONNECT_TIMEOUT,
    handshake_timeout: float = HANDSHAKE_RESPONSE_TIMEOUT,
) -> Optional[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
    """
    Performs the BitTorrent handshake with a peer.

    Establishes a TCP connection with the peer, sends the BitTorrent handshake
    message, and waits for the peer's handshake response. It verifies if the
    received info hash matches the expected one.

    Args:
        peer_ip: The IP address of the peer.
        peer_port: The port number of the peer.
        info_hash: The 20-byte info hash of the torrent.
        connect_timeout: Timeout in seconds for establishing the TCP connection.
                         Defaults to CONNECT_TIMEOUT.
        handshake_timeout: Timeout in seconds for receiving the peer's handshake
                           response. Defaults to HANDSHAKE_RESPONSE_TIMEOUT.

    Returns:
        A tuple containing the asyncio StreamReader and StreamWriter objects
        representing the established connection if the handshake is successful.
        Returns None if the connection fails, the handshake times out, or the
        info hashes do not match.
    """
    reader: Optional[asyncio.StreamReader] = None # Initialize reader as None
    writer: Optional[asyncio.StreamWriter] = None # Initialize writer as None
    sock: Optional[socket.socket] = None # Initialize sock as None

    try:
        print(f"Attempting handshake with {peer_ip}:{peer_port}")

        # --- Task 3.1: Create a TCP socket ---
        # Create a socket object using socket.socket() for IPv4 (AF_INET) and TCP (SOCK_STREAM).
        sock = None # YOUR CODE HERE
        if sock is None:
            raise NotImplementedError("Task 3.1: Creating the TCP socket is not implemented.")
        sock.settimeout(connect_timeout)
        print("Socket created.")

        # --- Task 3.2: Connect to the peer ---
        # Use asyncio.get_event_loop().sock_connect() to asynchronously connect the socket
        # to the peer's IP address and port.
        try:
            pass # YOUR CODE HERE
            print("Socket connected.")
        except OSError as e:
            print(f"Socket connect error: {e}")
            return None, None

        # --- Task 3.3: Open asyncio streams ---
        # Use asyncio.open_connection() with the socket to get asyncio StreamReader and StreamWriter.
        reader, writer = None, None # YOUR CODE HERE
        if reader is None or writer is None:
            raise NotImplementedError("Task 3.3: Opening asyncio connection is not fully implemented.")
        print("asyncio connection opened.")

        # --- Task 3.4: Construct the handshake message ---
        # The handshake message is 68 bytes long and has the following structure:
        # 1 byte: length of the protocol string (19 for "BitTorrent protocol")
        # 19 bytes: protocol string "BitTorrent protocol"
        # 8 bytes: reserved bytes (all zeros for basic clients)
        # 20 bytes: info hash of the torrent
        # 20 bytes: peer ID (generate a unique one starting with "-PYEXERCISE-")
        protocol_name = b"BitTorrent protocol"
        reserved_bytes = bytes(8)
        peer_id = None # YOUR CODE HERE
        if peer_id is None or len(peer_id) != 20:
            raise NotImplementedError("Task 3.4: Generating the peer ID is not fully implemented or incorrect length.")

        handshake_msg = (
            len(protocol_name).to_bytes(1, byteorder="big")
            + protocol_name
            + reserved_bytes
            + info_hash
            + peer_id
        )

        print(f"Sending handshake: {handshake_msg.hex()}")
        writer.write(handshake_msg)
        await writer.drain()

        # --- Task 3.5: Receive and verify the handshake response ---
        # Read 68 bytes from the peer using asyncio.wait_for() with the handshake_timeout.
        # Verify that the received response is 68 bytes long and that the info hash (bytes 28-47)
        # matches the 'info_hash' we sent.
        response = None # YOUR CODE HERE
        if response is None:
            raise NotImplementedError("Task 3.5: Receiving the handshake response is not implemented.")

        if len(response) == 68 and response[28:48] == info_hash:
            print(f"Handshake successful with {peer_ip}:{peer_port}")
            return reader, writer
        else:
            print(
                f"Handshake failed with {peer_ip}:{peer_port} - Info hash mismatch or invalid response."
            )
            if writer:
                writer.close()
                await writer.wait_closed()
            return None, None

    except ConnectionRefusedError:
        print(f"Connection refused by {peer_ip}:{peer_port}")
        return None, None
    except asyncio.TimeoutError:
        print(
            f"Connection timeout with {peer_ip}:{peer_port} after {connect_timeout} seconds"
        )
        return None, None
    except OSError as e:
        print(
            f"OSError connecting to {peer_ip}:{peer_port}: {e} (Error Number: {e.errno}, Socket Error: {e.strerror})"
        )
        return None, None
    except Exception as e:
        print(f"Error connecting to {peer_ip}:{peer_port}: {e}")
        return None, None
    finally:
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Error closing writer: {e}")


async def main():
    """
    Main function.
    """
    torrent_file = "example.torrent"  # Replace with the path to your .torrent file
    tracker_url, info_hash = parse_torrent(torrent_file)
    if tracker_url is None or info_hash is None:
        print("Error parsing torrent file. Cannot proceed with handshake.")
        return
    
    peer_list = get_peers(tracker_url, info_hash)

    if peer_list:
        random.shuffle(peer_list)
        for peer_ip, peer_port in peer_list:
            for _ in range(MAX_ATTEMPTS):
                try:
                    reader, writer = await perform_handshake(
                        peer_ip,
                        peer_port,
                        info_hash,
                        CONNECT_TIMEOUT,
                        HANDSHAKE_RESPONSE_TIMEOUT,
                    )
                    if reader and writer:
                        print("Handshake completed successfully.")
                        writer.close()
                        await writer.wait_closed()
                    else:
                        print("Handshake failed.")
                except ConnectionRefusedError:
                    print(f"Connection refused by {peer_ip}:{peer_port}")
                    return None


if __name__ == "__main__":
    asyncio.run(main())
