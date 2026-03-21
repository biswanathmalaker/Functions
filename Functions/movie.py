def movie(files,movie_path,fps):
    """
    files --> are list of image paths in sequence.\n
    movie_path --> is the path where movie is to created.\n eg. '/home/biswanath/new1.mp4'\n
    fps --> is frames per second.
    """
    import cv2

    file_array = files
    img_array = []
    for filename in file_array:
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)



    out = cv2.VideoWriter(movie_path,cv2.VideoWriter_fourcc(*'DIVX'),fps, size)
    
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

import os, ffmpeg
import subprocess
import glob


def create_movie_from_images(image_files, output_file, frame_rate=30):
    """
    Creates a movie from a list of image files using ffmpeg.

    image_files = glob.glob("./frames/hmi/*.jpeg")
    image_files = sorted(image_files)
    create_movie_from_images(image_files, 'hmi_ffmpeg.mp4')

    Args:
        image_files (list of str): List of paths to image files, sorted in the desired order.
        output_file (str): The path to the output movie file.
        frame_rate (int, optional): The frame rate of the output movie. Defaults to 30.

    """
    if not image_files:
        raise ValueError("The image_files list is empty.")
    
    # Create a temporary text file listing all the image files
    with open('file_list.txt', 'w') as f:
        for image_file in image_files:
            f.write(f"file '{image_file}'\n")
    
    # Command to create a movie using ffmpeg
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'file_list.txt',
        '-vf', f'fps={frame_rate}',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    
    # Run the ffmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Movie created successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while creating the movie: {e}")



def compress_movie(input_file, output_file, target_size_mb):
    """
    Compresses a movie file to a target size using ffmpeg.
    compress_movie('AIA_171_ffmpeg.mp4', 'AIA_171_ffmpeg_compr.mp4', 15)
    Args:
        input_file (str): The path to the input movie file.
        output_file (str): The path to the output compressed movie file.
        target_size_mb (float): The desired size of the output file in megabytes.
    """
    # Calculate the target bitrate in bits per second (bps)
    target_size_bits = target_size_mb * 8 * 1024 * 1024  # Convert MB to bits
    video_duration = get_video_duration(input_file)
    
    if video_duration <= 0:
        raise ValueError("Invalid video duration.")
    
    # Calculate the video bitrate needed to achieve the target size
    target_bitrate = target_size_bits / video_duration

    # Run the ffmpeg command to compress the video
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-b:v', str(int(target_bitrate)),
        '-bufsize', str(int(target_bitrate)),
        '-maxrate', str(int(target_bitrate)),
        '-y',  # Overwrite output file if it exists
        output_file
    ]
    
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Movie compressed successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while compressing the movie: {e}")

def get_video_duration(input_file):
    """
    Gets the duration of a video file in seconds.

    Args:
        input_file (str): The path to the input movie file.

    Returns:
        float: The duration of the video in seconds.
    """
    ffmpeg_command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_file
    ]
    
    try:
        result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting the video duration: {e}")
        return -1



def get_video_info(input_file):
    """
    Prints the total file size, framerate (FPS), quality, and container/codec information of an MP4 file.
    get_video_info('hmi_ffmpeg_compr.mp4')

    Args:
        input_file (str): The path to the input movie file.
    """
    if not os.path.isfile(input_file):
        print("The input file does not exist.")
        return
    
    # Get file size
    file_size = os.path.getsize(input_file) / (1024 * 1024)  # Convert to MB
    
    # Get video information using ffprobe
    ffprobe_command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name,codec_type,bit_rate,avg_frame_rate,width,height',
        '-show_entries', 'format=size,format_name',
        '-of', 'json',
        input_file
    ]
    
    try:
        result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        info = result.stdout
        import json
        info_dict = json.loads(info)
        
        # Extracting required information
        codec_name = info_dict['streams'][0]['codec_name']
        avg_frame_rate = info_dict['streams'][0]['avg_frame_rate']
        width = info_dict['streams'][0]['width']
        height = info_dict['streams'][0]['height']
        format_name = info_dict['format']['format_name']
        bit_rate = int(info_dict['streams'][0]['bit_rate']) / 1000  # Convert to kbps
        
        # Calculate FPS
        num, denom = map(int, avg_frame_rate.split('/'))
        fps = num / denom
        
        # Print video information
        print(f"Total File Size: {file_size:.2f} MB")
        print(f"Framerate (FPS): {fps:.2f}")
        print(f"Resolution: {width}x{height}")
        print(f"Codec: {codec_name}")
        print(f"Container: {format_name}")
        print(f"Bitrate: {bit_rate:.2f} kbps")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting the video information: {e}")





if __name__ == "__main__":
    from glob import glob

    files = glob("./movie_generation/frames/171/*.jpeg")
    files = sorted(files)
    # print(files[0],files[1],files[-1])

    movie_path = "./movie_generation/results/movie.mp4"
    fps = 5
    movie(files = files,movie_path=movie_path,fps=fps)