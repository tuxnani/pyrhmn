import moviepy.editor as mp
import os

def convert_mp4_to_mp3(mp4_file, mp3_file):
    """
    Converts an MP4 file to an MP3 file using moviepy.
    """
    try:
        # Load the video file
        video_clip = mp.VideoFileClip(mp4_file)
        
        # Extract the audio from the video clip
        audio_clip = video_clip.audio
        
        # Write the audio to an MP3 file
        # You can specify the bitrate for quality/size (e.g., '192k', '320k')
        audio_clip.write_audiofile(mp3_file, codec='mp3', bitrate='192k')
        
        # Close the clips to free up resources
        audio_clip.close()
        video_clip.close()
        
        print(f"Successfully converted {mp4_file} to {mp3_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Example Usage ---
# Define your input and output file paths
input_video = "input_mp4.mp4"  # Replace with your actual MP4 file path
output_audio = "output_audio.mp3" # Replace with desired output MP3 file path

# Ensure the input file exists for the example to run correctly
if os.path.exists(input_video):
    convert_mp4_to_mp3(input_video, output_audio)
else:
    print(f"Error: The file '{input_video}' was not found.")
