# Typing Technique Analyzer Using Computer Vision

This projects goal is to make learning typing technique easier and more efficient through the use of Computer Vision.

## Prerequisites
- Python 3.8 or higher
- Webcam positioned above the keyboard looking down

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/brian6466/FYP.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run PyQt App
    ```bash
    python main.py
    ```

## Tutorial
When first running the application you will be brought to the confirm screen, in this screen you select how you want to generate your key locations. Pressing YOLO will generate YOLO using the current keymap json layout. Pressing YOLO Mapping will allow you to you to change keymap to a new mapping. Manual mapping will skip YOLO and manually map your key locations. Pressing Continue will move the the typing test screen.

If YOLO doesnt work on your keyboard, you can use manual mapping instead.

On the typing test screen make sure you are focused on the typing test screen and not the finger tracking screen as thats where we read the key inputs.
