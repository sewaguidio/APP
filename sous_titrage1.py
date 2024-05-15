# -*- coding: utf-8 -*-
"""
!pip install --quiet ipython-autotime
# %load_ext autotime
!pip install moviepy
!pip install deep_translator
!pip install streamlit
!pip install numpy
"""
import tempfile
import os
import requests
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as  np
from deep_translator import GoogleTranslator
import streamlit as st


def extraire_audio(chemin_video):

    video = VideoFileClip(chemin_video)
    audio = video.audio
    sortie_audio = "sortie_audio.mp3"
    audio.write_audiofile(sortie_audio)
    return sortie_audio

def getDeepgramTranscription(file_path, deepgramapiKey, lang ):
    # Use this to get subtitles in English
    if lang == "fr" : 
        url = "https://api.deepgram.com/v1/listen?model=whisper-large&language=fr&punctuate=true&diarize=true&smart_format=true"
        
    else:
        url = "https://api.deepgram.com/v1/listen?model=whisper-large&language=en&punctuate=true&diarize=true&smart_format=true"

    # Use this to get subtitles in the same language as the audio/video
    #url = "https://api.deepgram.com/v1/listen?model=whisper-large&detect_language=true"

    headers = {
        "Authorization": 'Token ' + deepgramapiKey,
    }

    with open(file_path, 'rb') as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)

    output = response.json()
    return output





def translate_text(text, langue):
    # Initialiser le traducteur
    translator = GoogleTranslator(source='auto', target = langue)
    # Traduire le texte en ewe
    translation = translator.translate(text)
    return translation

def convert_to_srt(datas, output_filename, lang):
    def format_time(seconds):
        # Convert seconds to hours, minutes, seconds, milliseconds format
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds*1000):03d}"

    with open(output_filename, 'w',encoding="utf-8") as f:
      for para in range(len(datas)):
        data = datas[para]['sentences']
        for i, entry in enumerate(data, start=1):
            start_time = format_time(entry['start'])
            end_time = format_time(entry['end'])
            
            if lang == "ee" or lang == "yo":
                subtitle_text = translate_text(entry['text'], lang)
            else:
                subtitle_text = entry['text']
                
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{subtitle_text}\n\n")


# Liste des langues disponibles
langues = ["Français (fr)", "Anglais (en)", "Ewe (ee)", "Yoruba (yo)"]

# Interface Streamlit
st.title("Transcription et sous-titrage de vidéo")

# Charger la vidéo
video_file = st.file_uploader("Charger une vidéo", type=["mp4", "mov", "avi"])



if video_file is not None:
    # Saisie de la clé d'API Deepgram
    cle = st.text_input("Entrez votre clé ")

    # Sélection de la langue
    langue_selectionnee = st.selectbox("Sélectionnez la langue", langues)

    if cle and langue_selectionnee:
        # Extraction du code de langue
        lang = langue_selectionnee.split("(")[1].split(")")[0]

        # Enregistrement du fichier téléchargé dans un emplacement temporaire
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            temp_video.write(video_file.read())
            temp_video_path = temp_video.name

        # Bouton pour lancer la transcription
        if st.button("Transcrire"):
            # 1. Extraction de l'audio
            mp3url = extraire_audio(temp_video_path)

            # 2. Transcription de l'audio
            output1 = getDeepgramTranscription(mp3url, cle, lang)

            # 3. Extraction de partie de la transcription pour le sous-titrage
            subtitle_data1 = output1['results']['channels'][0]['alternatives'][0]['paragraphs']['paragraphs']

            # Extraction du nom de fichier
            filename = os.path.basename(mp3url)
            name, extension = os.path.splitext(filename)
            output_filename = name + ".srt"

            # Écriture d'un fichier de sous-titres (.srt) avec les timestamps mot par mot
            convert_to_srt(subtitle_data1, output_filename, lang)

            srtfilename = output_filename
            st.write(f"Sous-titres générés : {srtfilename}")

            target = os.path.basename(video_file.name)
            output_video = target.replace(".mp4", "_transcrit.mp4")

            # Cette opération prendra 2-3 minutes
            os.system(f"ffmpeg -i {target} -vf subtitles={srtfilename} {output_video}")

            # Affichage de la vidéo avec les sous-titres
            with open(video_file, "rb") as f:
                video_bytes = f.read()
            st.video(video_bytes)

    else:
        st.warning("Veuillez entrer une clé d'API Deepgram valide et sélectionner une langue.")
