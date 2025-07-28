import os
import sys
import subprocess
import speech_recognition as sr
from tqdm import tqdm
from pathlib import Path

# Configure the PATH for FFmpeg
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "bin")
os.environ["PATH"] += os.pathsep + FFMPEG_PATH

def check_dependencies():
    """Checks for dependencies"""
    try:
        import speech_recognition as sr
        from tqdm import tqdm
    except ImportError as e:
        print(f"Error: Missing dependencies - {str(e)}")
        print("Please install dependencies with:")
        print("pip install SpeechRecognition==3.10.0 tqdm==4.66.2")
        sys.exit(1)
    
    # Verify FFmpeg
    ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
    if not os.path.isfile(ffmpeg_exe):
        print(f"Error: ffmpeg.exe not found in {FFMPEG_PATH}")
        print("Download FFmpeg from: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("and extract the 'bin' folder into the ffmpeg directory of your project")
        sys.exit(1)

def extract_audio_from_video(video_path, audio_path):
    """Extracts audio using FFmpeg directly"""
    ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
    command = [
        ffmpeg_exe,
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        '-y',
        audio_path
    ]
    
    try:
        print("Extracting audio with FFmpeg...")
        result = subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False

def transcribe_audio(audio_path, output_path, language='en-US'):
    """Transcribes audio to text"""
    recognizer = sr.Recognizer()
    text_segments = []
    
    try:
        with sr.AudioFile(audio_path) as source:
            duration = source.DURATION
            segment_size = 30  # seconds
            
            for i in tqdm(range(0, int(duration), segment_size)):
                end_time = min(i + segment_size, duration)
                chunk_duration = end_time - i
                
                audio = recognizer.record(source, duration=chunk_duration)
                
                try:
                    text = recognizer.recognize_google(audio, language=language)
                    text_segments.append(f"[{i}-{end_time}s] {text}")
                except sr.UnknownValueError:
                    text_segments.append(f"[{i}-{end_time}s] (Unintelligible)")
                except sr.RequestError as e:
                    text_segments.append(f"[{i}-{end_time}s] API Error: {str(e)}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_segments))
            
        return True
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return False

def process_video_to_text(video_path, output_path, language='en-US'):
    """Processes a complete video"""
    audio_temp = os.path.join(BASE_DIR, "audio_temp.wav")
    
    if not extract_audio_from_video(video_path, audio_temp):
        return False
    
    if not transcribe_audio(audio_temp, output_path, language):
        return False
    
    try:
        if os.path.exists(audio_temp):
            os.remove(audio_temp)
    except:
        pass
    
    return True

def ensure_directory(directory):
    """Creates directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_output_path(input_file, output_directory):
    """Generates output path"""
    name = Path(input_file).stem
    return os.path.join(output_directory, f"{name}.txt")

def process_all_videos(input_directory, output_directory, language='en-US'):
    """Processes all videos in a directory"""
    ensure_directory(output_directory)
    videos = [f for f in os.listdir(input_directory) if f.lower().endswith('.mp4')]
    
    if not videos:
        print("No MP4 files found")
        return
    
    print(f"Processing {len(videos)} videos...")
    
    for video in videos:
        input_path = os.path.join(input_directory, video)
        output_path = get_output_path(video, output_directory)
        
        print(f"\nStarting: {video}")
        if process_video_to_text(input_path, output_path, language):
            print(f"Completed: {os.path.basename(output_path)}")
        else:
            print(f"Error processing: {video}")

if __name__ == "__main__":
    check_dependencies()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "input")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    
    language = input("Language (e.g., es-ES, en-US): ") or "en-US"
    
    if os.path.exists(INPUT_DIR):
        process_all_videos(INPUT_DIR, OUTPUT_DIR, language)
        print("\nProcess completed!")
    else:
        print(f"Input directory does not exist: {INPUT_DIR}")
        os.makedirs(INPUT_DIR, exist_ok=True)
        print(f"Directory created. Place your MP4 videos in: {INPUT_DIR}")