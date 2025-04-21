import os
import cv2
import pytesseract
import srt
import datetime
import subprocess
import argparse
from loguru import logger

# Voice recognition
from faster_whisper import WhisperModel

# Local translation
import argostranslate.translate

from subtitle_generator_and_translator_ocr.install_translation_model import (
    install_translation_model_if_needed,
)

import subtitle_generator_and_translator_ocr


def extract_text_from_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    cropped = gray[int(h * 0.80) : int(h * 0.97), int(w * 0.1) : int(w * 0.9)]
    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(cropped, lang="eng", config=custom_config)
    return text.strip()


def is_valid_sub(text):
    return len(text) > 4 and any(c.isalpha() for c in text)


def generate_subtitles_ocr(video_path, frame_interval):
    cap = cv2.VideoCapture(video_path)
    ms_between_frames = frame_interval
    subs = []
    last_text = ""
    sub_start = None
    sub_id = 1
    current_time = 0

    while True:
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time)
        ret, frame = cap.read()
        if not ret:
            break
        text = extract_text_from_frame(frame)
        logger.debug(f"[{current_time} ms] OCR: '{text}'")

        if is_valid_sub(text) and text != last_text:
            if last_text and sub_start is not None:
                sub = srt.Subtitle(
                    index=sub_id,
                    start=datetime.timedelta(milliseconds=sub_start),
                    end=datetime.timedelta(milliseconds=current_time),
                    content=last_text,
                )
                subs.append(sub)
                sub_id += 1
            sub_start = current_time
            last_text = text
        current_time += ms_between_frames

    if is_valid_sub(last_text) and sub_start is not None:
        sub = srt.Subtitle(
            index=sub_id,
            start=datetime.timedelta(milliseconds=sub_start),
            end=datetime.timedelta(milliseconds=current_time),
            content=last_text,
        )
        subs.append(sub)

    cap.release()
    return subs


def generate_subtitles_voice(video_path):
    logger.info("Using voice recognition (Whisper)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(video_path, beam_size=5)

    subs = []
    for i, segment in enumerate(segments):
        sub = srt.Subtitle(
            index=i + 1,
            start=datetime.timedelta(seconds=segment.start),
            end=datetime.timedelta(seconds=segment.end),
            content=segment.text.strip(),
        )
        subs.append(sub)

    return subs


def translate_subtitles(
    subtitles, from_lang="en", to_lang="pt", manual_verification=False
):
    install_translation_model_if_needed()
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang_obj = next(lang for lang in installed_languages if lang.code == from_lang)
    to_lang_obj = next(lang for lang in installed_languages if lang.code == to_lang)
    translation = from_lang_obj.get_translation(to_lang_obj)

    translated_subs = []
    for sub in subtitles:
        translated_text = translation.translate(sub.content)

        if manual_verification:
            print(f"\nOriginal: {sub.content}")
            print(f"Traduzido: {translated_text}")
            user_input = input(
                "Editar tradução? (enter = manter / texto novo): "
            ).strip()
            if user_input:
                translated_text = user_input

        translated_subs.append(
            srt.Subtitle(
                index=sub.index, start=sub.start, end=sub.end, content=translated_text
            )
        )
    return translated_subs


def verify_subtitles_final(subtitles):
    print("\n📝 Verificando legendas finais:")
    for i, sub in enumerate(subtitles):
        print(f"\n[{i+1}] {sub.start} --> {sub.end}")
        print(sub.content)
        choice = input("Confirmar? (enter = sim / n = cancelar): ").strip().lower()
        if choice == "n":
            print("Cancelado pelo usuário.")
            return False
    return True


def write_srt(subtitles, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))


def burn_subtitles(video_path, srt_path, output_path, force_overwrite=False):
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"subtitles={srt_path}",
        "-c:a",
        "copy",
    ]
    if force_overwrite:
        command.append("-y")
    command.append(output_path)
    subprocess.run(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Legenda e tradução OCR")
    parser.add_argument(
        "--manual-verification",
        action="store_true",
        default=True,
        help="Habilita edição manual das traduções",
    )
    parser.add_argument(
        "--verify-subtitles",
        action="store_true",
        default=True,
        help="Mostra as legendas traduzidas para confirmação antes de embutir no vídeo",
    )
    parser.add_argument(
        "--video-path",
        type=str,
        default=os.path.join(
            "/".join(os.path.dirname(subtitle_generator_and_translator_ocr.__file__).split("/")[:-1]),
            "video.mp4",
        ),
        help="Caminho para o arquivo de vídeo",
    )

    parser.add_argument(
        "--output-srt",
        type=str,
        default=os.path.join(
            "/".join(os.path.dirname(subtitle_generator_and_translator_ocr.__file__).split("/")[:-1]),
            "subtitles.srt",
        ),
        help="Caminho para salvar o arquivo SRT gerado",
    )
    parser.add_argument(
        "--output-video",
        type=str,
        default=os.path.join(
            "/".join(os.path.dirname(subtitle_generator_and_translator_ocr.__file__).split("/")[:-1]),
            "output_with_subs.mp4",
        ),
        help="Caminho para salvar o vídeo com legendas embutidas",
    )
    parser.add_argument(
        "--frame-interval",
        type=int,
        default=500,
        help="Intervalo de quadros (em ms) para OCR",
    )
    parser.add_argument(
        "--use-voice",
        action="store_true",
        default=True,
        help="Usar reconhecimento de voz em vez de OCR para gerar legendas",
    )
    parser.add_argument(
        "--translate-to-ptbr",
        action="store_true",
        default=True,
        help="Traduzir legendas para português brasileiro",
    )

    args = parser.parse_args()

    logger.info("Flags setup:")
    logger.info(f"Manual verification: {args.manual_verification}")
    logger.info(f"Verify subtitles: {args.verify_subtitles}")
    logger.info(f"Video path: {args.video_path}")
    logger.info(f"Output SRT path: {args.output_srt}")
    logger.info(f"Output video path: {args.output_video}")
    logger.info(f"Frame interval: {args.frame_interval}")
    logger.info(f"Use voice recognition: {args.use_voice}")
    logger.info(f"Translate to pt: {args.translate_to_ptbr}")

    logger.info("Generating subtitles...")

    if args.use_voice:
        subtitles = generate_subtitles_voice(args.video_path)
    else:
        subtitles = generate_subtitles_ocr(args.video_path, args.frame_interval)

    if args.translate_to_ptbr:
        logger.info("Translating subtitles to pt...")
        subtitles = translate_subtitles(
            subtitles,
            from_lang="en",
            to_lang="pt",
            manual_verification=args.manual_verification,
        )

    if args.verify_subtitles:
        if not verify_subtitles_final(subtitles):
            logger.info("❌ Legendas não confirmadas. Saindo.")
            exit()

    write_srt(subtitles, args.output_srt)
    logger.info(f"Subtitles saved to {args.output_srt}")

    logger.info("Embedding subtitles into video...")
    burn_subtitles(
        args.video_path, args.output_srt, args.output_video, force_overwrite=True
    )
    logger.info(f"Video with subtitles saved to {args.output_video}")
