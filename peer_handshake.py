# Standard imports
import asyncio
import random
import socket

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers

# Define default timeout values as constants
DEFAULT_CONNECT_TIMEOUT = 15
DEFAULT_HANDSHAKE_RESPONSE_TIMEOUT = 20
DEFAULT_PIECE_RESPONSE_PREFIX_TIMEOUT = 25
DEFAULT_PIECE_DATA_TIMEOUT = 40


async def perform_handshake(
    peer_ip,
    peer_port,
    info_hash,
    connect_timeout=DEFAULT_CONNECT_TIMEOUT,
    handshake_timeout=DEFAULT_HANDSHAKE_RESPONSE_TIMEOUT,
):
    try:
        print(f"Attempting handshake with {peer_ip}:{peer_port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(connect_timeout)  # Set initial connection timeout

        # Wrap the socket connection in an asyncio task
        await asyncio.get_event_loop().sock_connect(sock, (peer_ip, peer_port))

        reader, writer = asyncio.open_connection(sock=sock)  # use the socket

        protocol_name = b"BitTorrent protocol"
        reserved_bytes = bytes(8)
        peer_id = b"-PYWORKSHOP-" + "".join(random.choices("0123456789ABCDEF", k=12))

        handshake_msg = (
            len(protocol_name).to_bytes(1, byteorder="big")
            + protocol_name
            + reserved_bytes
            + info_hash
            + peer_id
        )

        writer.write(handshake_msg)
        await writer.drain()

        # Use asyncio.wait_for for the handshake response with its own timeout
        try:
            response = await asyncio.wait_for(
                reader.read(68), timeout=handshake_timeout
            )
        except asyncio.TimeoutError:
            print(
                f"Handshake timeout: No response from {peer_ip}:{peer_port} after {handshake_timeout} seconds"
            )
            writer.close()
            await writer.wait_closed()
            return None, None

        if response and response[28:48] == info_hash:
            print(f"Handshake successful with {peer_ip}:{peer_port}")
            return reader, writer
        else:
            print(
                f"Handshake failed with {peer_ip}:{peer_port} - Info hash mismatch or invalid response."
            )
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
        if "writer" in locals() and writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Error closing writer: {e}")


async def request_piece(
    reader,
    writer,
    piece_index,
    piece_prefix_timeout=DEFAULT_PIECE_RESPONSE_PREFIX_TIMEOUT,
    piece_data_timeout=DEFAULT_PIECE_DATA_TIMEOUT,
):
    """Requests and downloads a piece of data from a peer."""
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

    except Exception as e:
        print(f"Error requesting/downloading piece: {e}")
        return None


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
            for attempt in range(3):
                try:
                    reader, writer = await perform_handshake(
                        peer_ip,
                        peer_port,
                        info_hash,
                        DEFAULT_CONNECT_TIMEOUT,
                        DEFAULT_HANDSHAKE_RESPONSE_TIMEOUT,
                    )
                    if reader and writer:
                        print(
                            f"Successfully connected to {peer_ip}:{peer_port} after {attempt + 1} attempts."
                        )
                        try:
                            piece = await request_piece(
                                reader,
                                writer,
                                piece_index=0,
                                piece_prefix_timeout=DEFAULT_PIECE_RESPONSE_PREFIX_TIMEOUT,
                                piece_data_timeout=DEFAULT_PIECE_DATA_TIMEOUT,
                            )
                            if piece:
                                print(
                                    "Successfully downloaded a piece using the integrated client."
                                )
                            else:
                                print(
                                    f"Failed to download piece from {peer_ip}:{peer_port}"
                                )
                        except Exception as e:
                            print(f"Error during piece request: {e}")
                        finally:
                            writer.close()
                            await writer.wait_closed()
                        return
                    else:
                        print(
                            f"Handshake failed with {peer_ip}:{peer_port}, attempt {attempt + 1}."
                        )
                        await asyncio.sleep(5 * (attempt + 1))
                except Exception as e:
                    print(
                        f"Error connecting to {peer_ip}:{peer_port}, attempt {attempt + 1}: {e}"
                    )
                    await asyncio.sleep(5 * (attempt + 1))
            print("Failed to connect to any peer after multiple attempts.")
    else:
        print("No peers found by tracker.")


if __name__ == "__main__":
    asyncio.run(main())
