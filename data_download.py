# Standard imports
import asyncio

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers
from peer_handshake import perform_handshake


async def request_piece(reader, writer, piece_index):
    # Request block (16 KB) from piece index 0 at offset 0
    length_prefix = (13).to_bytes(4, byteorder="big")
    message_id = (6).to_bytes(1, byteorder="big")  # Request message ID
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

    # Read response (piece message)
    response_prefix = await reader.read(4)  # Message length prefix
    if not response_prefix:
        return None

    message_length = int.from_bytes(response_prefix, byteorder="big")
    piece_data = await reader.read(
        message_length - 9
    )  # Subtract header size (1 byte id, 4 byte index, 4 byte begin)

    if piece_data:
        print(f"Downloaded {len(piece_data)} bytes from piece {piece_index}")
    return piece_data


async def main():
    torrent_file = "ubuntu-24.04.2-desktop-amd64.iso.torrent"
    tracker_url, info_hash = parse_torrent(torrent_file)
    peer_list = get_peers(tracker_url, info_hash)

    if peer_list:
        reader, writer = await perform_handshake(
            peer_list[0][0], peer_list[0][1], info_hash
        )
        if reader and writer:
            piece = await request_piece(reader, writer, piece_index=0)
            if piece:
                print("Successfully downloaded a piece.")
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
