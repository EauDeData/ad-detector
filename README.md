# Tool for Ads Detection

## How to


1. Once conda is installed create an environment with the required python version.

> conda create -n ads python==3.9.12
> conda activate ads

2. Switch to the working directory

> cd [PROJECT DIRECTORY]

3. Install Python dependencies

> pip install -r requirements.txt

4. Install tesseract. If you are using windows use the provided <a href = 'https://tesseract-ocr.github.io/tessdoc/Installation.html'> link </a>.

> WARNING: Ensure SPANISH tesseract-ocr is installed.

5. Provide to the config file the necessary paths.

> A file with all the PDF's absolute routes will be required. Generate it and provide it to the config file.

6. Set 'offline' to true in the config file. 

> WARNING: Set it to false after installation.

7. Launch the main file. It will take ~2h to preload all the data. But it won't be required anymore after this first execution.

> After setting up everything just set to 'false' the 'offline' option in the config file.


