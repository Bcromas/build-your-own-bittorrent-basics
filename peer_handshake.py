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
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None
    sock: Optional[socket.socket] = None

    try:
        print(f"Attempting handshake with {peer_ip}:{peer_port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(connect_timeout)
        await asyncio.get_event_loop().sock_connect(sock, (peer_ip, peer_port))
        reader, writer = await asyncio.open_connection(sock=sock)

        protocol_name = b"BitTorrent protocol"
        reserved_bytes = bytes(8)
        peer_id = b"-PYEXERCISE-" + "".join(
            random.choices("0123456789ABCDEF", k=12)
        ).encode("ascii")

        handshake_msg = (
            len(protocol_name).to_bytes(1, byteorder="big")
            + protocol_name
            + reserved_bytes
            + info_hash
            + peer_id
        )

        writer.write(handshake_msg)
        await writer.drain()

        response = await asyncio.wait_for(reader.read(68), timeout=handshake_timeout)

        if response and len(response) == 68 and response[28:48] == info_hash:
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
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"
    tracker_url, info_hash = parse_torrent(torrent_file)
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
