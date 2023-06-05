from pytube import YouTube
import os
#learned about pathlib from this page: https://docs.python.org/3/library/pathlib.html
import pathlib

#i took the code for how to get the current file's directory from here:
# https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
MUSIC_DIR = pathlib.Path(__file__).parent.resolve()
TEMP_DIR = MUSIC_DIR / "_temp_"

def is_downloaded() -> bool:
    """
    Checks if all the music files are already downloaded.
    """
    #open the source list 
    with open(str(MUSIC_DIR / "sources.txt")) as sources_handle:
        #get the text of the source file
        sources = sources_handle.read()
        #convert it into a list of file names
        names = [source.split(":")[0].strip() for source in sources.split("\n")]
        #check if all music files exist via a list comprehension, then comparing the length of the list and of the ideal file names
        files_all_exist = len([f for name in names if (f:=(MUSIC_DIR / name).is_file())])==len(names)
        return files_all_exist


def download():
    """
    Downloads all the music files from their youtube sources
    """
    #open the source list
    with open(str(MUSIC_DIR / "sources.txt")) as sources_handle:
        #get the text of the source file 
        sources = sources_handle.read()
        
        #for all the sources
        for source in sources.split("\n"):
            #get the desired name of the mp3
            mp3_name = source.split(":")[0].strip()
            #get the desired name of the mp4 from the name of the mp3
            mp4_name = mp3_name.split(".")[0]+".mp4"
            #get the link to the youtube video for download
            your_knight_and_that_legendary_sword_he_carries_our_last_line_of_defense = source.split("-")[-1].strip()
            
            #get the video, and the audio only stream
            video = YouTube(your_knight_and_that_legendary_sword_he_carries_our_last_line_of_defense)
            audio_stream = video.streams.get_audio_only()

            #download the audio stream to the mp4 name
            audio_stream.download(output_path=str(TEMP_DIR), filename=mp4_name)
            #I took the ffmpeg command to convert an mp4 file to mp3 from here:
            # https://superuser.com/questions/332347/how-can-i-convert-mp4-video-to-mp3-audio-with-ffmpeg
            #i also took the arguments for how to make the output less verbose from here:
            # https://superuser.com/questions/326629/how-can-i-make-ffmpeg-be-quieter-less-verbose
            os.system(f"ffmpeg -hide_banner -loglevel error -i {str(TEMP_DIR / mp4_name)} -b:a 192K -vn {str(MUSIC_DIR / mp3_name)}")
            #remove the temp file
            os.remove(str(TEMP_DIR / mp4_name))
            print("Successfully downloaded "+mp3_name)

        #remove the temporary dir
        os.rmdir(TEMP_DIR)