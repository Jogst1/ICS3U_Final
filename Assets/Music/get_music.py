from pytube import YouTube
import os
import pathlib

MUSIC_DIR = pathlib.Path(__file__).parent.resolve()
TEMP_DIR = MUSIC_DIR / "_temp_"

def is_downloaded() -> bool:
    with open(str(MUSIC_DIR / "sources.txt")) as sources_handle:
        sources = sources_handle.read()
        names = [source.split(":")[0].strip() for source in sources.split("\n")]
        files_all_exist = len([f for name in names if (f:=(MUSIC_DIR / name).is_file())])==len(names)
        return files_all_exist


def download():
    with open(str(MUSIC_DIR / "sources.txt")) as sources_handle:
        sources = sources_handle.read()
        
        for source in sources.split("\n"):
            mp3_name = source.split(":")[0].strip()
            mp4_name = mp3_name.split(".")[0]+".mp4"
            your_knight_and_that_legendary_sword_he_carries_our_last_line_of_defense = source.split("-")[-1].strip()
            
            video = YouTube(your_knight_and_that_legendary_sword_he_carries_our_last_line_of_defense)
            audio_stream = video.streams.get_audio_only()

            audio_stream.download(output_path=str(TEMP_DIR), filename=mp4_name)
            os.system(f"ffmpeg -hide_banner -loglevel error -i {str(TEMP_DIR / mp4_name)} -b:a 192K -vn {str(MUSIC_DIR / mp3_name)}")
            os.remove(str(TEMP_DIR / mp4_name))
            print("Successfully downloaded "+mp3_name)

        os.rmdir(TEMP_DIR)


print(is_downloaded())