

def concatenate_movie(files,target_file):
    from moviepy.editor import VideoFileClip , concatenate_videoclips
    import os

    target_dir = os.path.dirname(target_file)
    if os.path.isdir(target_dir):
        pass
    else:
        os.makedirs(target_dir)

    clips = [VideoFileClip(f) for f in files]

    if os.path.isdir(target_dir):
        pass
    else:
        os.makedirs(target_dir)

    if os.path.isfile(target_file):
        print(f"{target_file} already exist.")
    else:
        result = concatenate_videoclips(clips)
        result.write_videofile(target_file)
        print(f"{target_file} created.")


if __name__=="__main__":
    import glob

    files = glob.glob("*.mp4")
    files = sorted(files)

    concatenate_movie(files[0:2],"./movie_conc/here_is_the_file/m.mp4")