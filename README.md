# Ground-Truth-App

<p align="center"> <img src="https://github.com/emilio-lovarela/Ground-Truth-App/blob/master/Instructions/Instructions1.JPG?raw=true" alt="screenshot" width="500"><img src="https://github.com/emilio-lovarela/Ground-Truth-App/blob/master/Instructions/Instructionsz12.jpg?raw=true" alt="screenshot" width="600"></p>

This is a Kivy app to facilitate the creation of image masks, labels, Ground-truth... to train Deep learning neural networks in the tasks of Classification, Object Detection, Semantic Segmentation and Instance Segmentation.

## Windows users
Windows users can download a ready-to-use executable at the following link. Clicking the link downloads a zip file that contains the executable. When you run the program, the instructions will appear on the screen as images.
[Click here to download](<https://www.dropbox.com/s/di6oxtp17qdkut3/GroundTruthApp.zip?dl=1>)

## Linux users (Windows users can also use it)

### 1. Install Python 3+

If you don't already have Python 3+ installed, grab it from <https://www.python.org/downloads/>.

### 2. Create a virtual env (optional)
This is optional, but highly recommended. In a [command prompt or Terminal window](https://tutorial.djangogirls.org/en/intro_to_command_line/#what-is-the-command-line), type the following, and press enter:

```shell
python -m virtualenv ~/the_name_you_want
```
Then to activate the virtual env you just have to run the following command:

In linux:
```shell
source ~/the_name_you_want/bin/activate
```
In Windows:
```shell
the_name_you_want\Scripts\activate
```

### 3. Clone This Repository

On <https://github.com/emilio-lovarela/Ground-Truth-App>, click the green "Clone or Download" button at the top right of the page. If you want to get started with this script more quickly, click the "Download ZIP" button, and extract the ZIP somewhere on your computer.

### 4. Install Dependencies

In a [command prompt or Terminal window](https://tutorial.djangogirls.org/en/intro_to_command_line/#what-is-the-command-line), [navigate to the directory](https://tutorial.djangogirls.org/en/intro_to_command_line/#change-current-directory) containing this repository's files. Then, type the following, and press enter:

```shell
pip install -r requirements.txt
```

### 5. Run the Script

In the same command prompt or Terminal window, type the following, and press enter:

```shell
python3 GroundTruthBuilder.py
```
In linux if when executing the program it gives you a warning you may have to use the following command in the cmd:

```shell
sudo apt-get install xclip
```