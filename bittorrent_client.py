# Standard imports
import asyncio

# Local imports
from torrent_parser import parse_torrent
from tracker_request import get_peers
from peer_handshake import perform_handshake
from data_download import request_piece


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
                print("Successfully downloaded a piece using the integrated client.")
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
