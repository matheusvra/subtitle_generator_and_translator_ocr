# Subtitle Generator and Translator OCR

## Objective

This repository provides a tool for generating and translating subtitles using Optical Character Recognition (OCR) and voice recognition. It is designed to extract text from video frames or audio, generate subtitles, and translate them into different languages. The tool is ideal for content creators, educators, and anyone who needs to make video content accessible to a global audience.

## Features

- Extract text from video frames using OCR.
- Extract text from audio using voice recognition.
- Generate subtitles in the original language.
- Translate subtitles into multiple languages.
- Easy-to-use command-line interface.

## Installation

Follow these steps to set up the project:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/subtitle_generator_and_translator_ocr.git
    cd subtitle_generator_and_translator_ocr
    ```

    2. **Set Up a Virtual Environment Using Poetry with Python 3.11**:
        Ensure Python 3.11 is installed on your system. Then, create a virtual environment using Poetry:
        ```bash
        poetry env use python3.11
        ```
    ```

3. **Install Dependencies Using Poetry**:
    Ensure you have Poetry installed. Then, run:
    ```bash
    poetry install
    ```

4. **Download Required Models**:
    If the project uses specific OCR, voice recognition, or translation models, download them as instructed in the documentation.

## Usage Example

1. **Extract Subtitles from a Video**:
    ```bash
    python main.py --video input_video.mp4 --output subtitles.srt
    ```

2. **Extract Subtitles from Audio**:
    ```bash
    python main.py --audio input_audio.mp3 --output subtitles.srt
    ```

3. **Translate Subtitles**:
    ```bash
    python main.py --translate subtitles.srt --language es --output translated_subtitles.srt
    ```

4. **Combine Steps**:
    Extract and translate subtitles in one command:
    ```bash
    python main.py --video input_video.mp4 --language es --output translated_subtitles.srt
    ```

## Tutorial

Here’s a step-by-step guide to using the tool:

1. Place your video or audio file in the project directory.
2. Run the command to extract subtitles from the video or audio.
3. Use the translation feature to convert the subtitles into your desired language.
4. The output file will be saved in the specified location.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.