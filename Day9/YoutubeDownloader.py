from pytube import YouTube 

SAVE_PATH = "./" 

link=input("Please paste Youtube URL to download:")

YouTube(link).streams.first().download()

print("Video Downloaded in the Current Working Directory!")
