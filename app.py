import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os
from tqdm import tqdm
from pathlib import Path
import sys

"""
Vídeo a Texto (MP4_A_TXT)
autor: instak1ll
Utilizado para convertir el audio de vídeos a texto
"""

def comprobar_dependencias():
    """Comprueba las dependencias"""
    try:
        import speech_recognition as sr
        from moviepy.editor import VideoFileClip
        from tqdm import tqdm
    except ImportError as e:
        print(f"Error: No tienes las dependencias instaladas.")
        print("Por favor, ejecuta el siguiente comando en la terminal para instalar las dependencias:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def extraer_audio_de_video(ruta_video, ruta_audio):
    """Extrae la pista de audio de un archivo de vídeo."""
    video = VideoFileClip(ruta_video)
    audio = video.audio
    audio.write_audiofile(ruta_audio)
    video.close()

def transcribir_audio(ruta_audio, ruta_salida, idioma='es-ES'):
    """Transcribe un archivo de audio a texto."""
    reconocedor = sr.Recognizer()
    segmentos_texto = []

    with sr.AudioFile(ruta_audio) as fuente:
        duracion = fuente.DURATION

        for i in tqdm(range(0, int(duracion), 30)):
            audio = reconocedor.record(fuente, duration=min(30, duracion-i))
            try:
                texto = reconocedor.recognize_google(audio, language=idioma)
                if texto.strip():
                    segmentos_texto.append(texto.strip())
            except sr.UnknownValueError:
                print(f"No se pudo reconocer el audio de {i}s a {min(i+30, duracion)}s")
            except sr.RequestError as e:
                print(f"Error en la petición a la API de Google: {e}")

    with open(ruta_salida, 'w', encoding='utf-8') as archivo:
        archivo.write('\n'.join(segmentos_texto))

def procesar_video_a_texto(ruta_video, ruta_salida, idioma='es-ES'):
    """Procesa un vídeo y lo convierte a texto."""
    audio_temporal = "audio_temporal.wav"

    try:
        print("Extrayendo audio...")
        extraer_audio_de_video(ruta_video, audio_temporal)

        print("Realizando reconocimiento de voz...")
        transcribir_audio(audio_temporal, ruta_salida, idioma)

    finally:
        if os.path.exists(audio_temporal):
            os.remove(audio_temporal)

def asegurar_directorio(directorio):
    """Crea el directorio si no existe."""
    Path(directorio).mkdir(parents=True, exist_ok=True)

def obtener_ruta_salida(archivo_entrada, directorio_salida):
    """Genera la ruta del archivo de salida."""
    nombre_archivo = Path(archivo_entrada).stem
    return os.path.join(directorio_salida, f"{nombre_archivo}.txt")

def procesar_todos_los_videos(directorio_entrada, directorio_salida, idioma='es-ES'):
    """Procesa todos los archivos MP4 en el directorio de entrada."""
    asegurar_directorio(directorio_salida)

    archivos_mp4 = [f for f in os.listdir(directorio_entrada) if f.lower().endswith('.mp4')]

    if not archivos_mp4:
        print("¡No se encontraron archivos MP4!")
        return

    print(f"Se encontraron {len(archivos_mp4)} archivos MP4")

    for archivo_video in archivos_mp4:
        ruta_video = os.path.join(directorio_entrada, archivo_video)
        ruta_salida = obtener_ruta_salida(archivo_video, directorio_salida)

        print(f"\nProcesando archivo: {archivo_video}")
        procesar_video_a_texto(ruta_video, ruta_salida, idioma)

if __name__ == "__main__":
    comprobar_dependencias()

    directorio_base = os.path.dirname(os.path.abspath(__file__))
    directorio_entrada = os.path.join(directorio_base, "input")
    directorio_salida = os.path.join(directorio_base, "output")

    idioma = input("Introduce el código de idioma (por defecto es-ES): ") or "es-ES"

    if os.path.exists(directorio_entrada):
        procesar_todos_los_videos(directorio_entrada, directorio_salida, idioma)
        print("\n¡Todos los archivos han sido procesados!")
    else:
        print(f"¡El directorio de entrada {directorio_entrada} no existe!")