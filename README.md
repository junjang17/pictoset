# Pictoset

## Overview
Pictoset is a Flask web app that creates Quizlet flashcard sets using images of word/definition pairs that the user uploads.
Pictoset uses Google's Optical Character Recognition engine, [Tesseract](https://github.com/tesseract-ocr/tesseract), to
analyze the uploaded image for text. The text is then formatted and sent to Quizlet's API to create a set for the user.

## Setting up Pictoset (Installation and Configuration)
In order to set up Pictoset, you will need to 
1. Install Pictoset files
2. Install Tesseract engine **(VERSION 3.05)**
3. Configure Tesseract 

### Installing Pictoset Files
Install the Pictoset files either through files that were submitted through CS50's submit50 or through [github](https://github.com/junjang17/pictoset).
The main files for Pictoset include:
1. Source code (Flask App)
2. Tesseract Language-Training Data 
3. virtual environment with pytesseract (Python wrapper for Tesseract)

### Installing Tesseract OCR Engine
Install the [Tesseract engine](https://github.com/tesseract-ocr/tesseract). Below are various methods (taken from 
tesseract's github readme linked above)

  * **Linux**
    * Tesseract is available directly from many Linux distributions. The package is generally called 'tesseract' or 
      'tesseract-ocr' - search your distribution's repositories to find it. 
    * Packages are also generally available for language training data (search the repositories,) but if not you will 
      need to download the appropriate training data (=< 3.02 or the latest from github.com), 
      unpack it, and copy the .traineddata file into the 'tessdata' directory, probably /usr/share/tesseract-ocr/tessdata 
      or /usr/share/tessdata.
    * If Tesseract is not available for your distribution, or you want to use a newer version than they offer, you can 
      compile your own. Note that older versions of Tesseract only supported processing .tiff files.

  * **macOS**
    * Using MacPorts
      * To install Tesseract run this command:
      
        `sudo port install tesseract`
    * Using Homebrew
      * To install Tesseract run this command:
      
        `brew install tesseract`
    * I highly recommend using the Homebrew method as it is simple. Also, you can skip set the PATH variable step

  * **Windows**
    * An unofficial installer for windows for Tesseract 3.05-dev and Tesseract 4.00-dev is available from Tesseract at 
      UB Mannheim. This includes the training tools.
    * An installer for the old version 3.02 is available for Windows from our download page. This includes the English 
      training data. If you want to use another language, download the appropriate training data, unpack it using 7-zip, 
      and copy the .traineddata file into the 'tessdata' directory, probably C:\Program Files\Tesseract-OCR\tessdata.
    * To access tesseract-OCR from any location you may have to add the directory where the tesseract-OCR binaries are 
      located to the Path variables, probably C:\Program Files\Tesseract-OCR.



### Configuring Tesseract OCR Engine
In order for Pictoset to work, Tesseract must have the required Language training data in the correct directory, and tesseract 
must set as a PATH variable such that the command line can run tesseract as *tesseract*. 
1. Locate the directory Tesseract was installed (if you used Homebrew, it should be in /usr/local/Cellar. Access /usr by opening Finder and pressing **command + shift + G**)
2. Open the Tesseract directory, open the folder named *share*, and open *tessdata*. In this folder, place the language-training data files (drag and drop)
that was downloaded from the **Pictoset Files** (found in the folder *tesseract-data*) 
    * **NOTE:** If you only plan to use Tesseract for English, you can skip this part.
3. Now, the directory that contains the Tesseract engine must be included in the PATH variables. 
   * On Mac, open terminal and run `export PATH=$PATH: <your directory path here>`
   
   If you used Homebrew, this step is already done, but make sure by checking that wherever Tesseract installed
   (should be /usr/local/bin) is included in PATH.
   * On Windows, 
        1. In Search, search for and then select: System (Control Panel)
        2. Click the Advanced system settings link.
        3. Click Environment Variables. In the section System Variables, find the PATH environment variable and select it. Click Edit. If the PATH environment variable does not exist, click New.
        4. In the Edit System Variable (or New System Variable) window, specify the value of the PATH environment variable. Click OK. Close all remaining windows by clicking OK.
        
Once Tesseract has been installed and configured, you are ready to run Pictoset.


## Running Pictoset
1. Open terminal and navigate into the Pictoset directory (you should now be in directory that contains **application.py** and various other files)
2. Activate the virtual environment using the command `source bin/activate`
3. Set the flask app using `export FLASK_APP=applicaton.py`
4. Run the server using `flask run`
5. Visit the specified url to access the app (Most likely **127.0.0.1:5000**)

## General Directions
The overall flow of Pictoset is as follows. Visit the **How To** page on the webapp for the directions as well.
1. **Log in** using Quizlet (click the button on the homepage)
2. Click **Create set** (either in Navbar or in the main body of page)
3. **Upload** an image
4. Crop out the **terms** you want
5. Crop out the **definitions** you want
6. Specify the **title, term language, and definition language**
7. Click **Create set**!

* Quick Tip: When selecting terms/definitions, do your best to avoid anything other than letters (such as bullet points, 
  dashes before the terms, etc.)


## Limitations 
Pictoset has a few limitations:
* Accuracy
    * Pictoset, because it is using Tesseract's Engine, can have varying accuracy when it comes to correctly recognizing and posting the terms/definitions to Quizlet
* Works on certain types of Images
    * In order to correctly differentiate the terms and definitions, the user must crop out the area of the picture that contains the terms and definitions. As such, 
    Pictoset works best when the terms and definitions are separated with a few spaces.
* Limited accuracy for different languages
    * As per Tesseract's github, **"Tesseract was originally designed to recognize English text only."** As such,
      this webapp works best with English, Spanish, French, and German. In particular, Tesseract is 
      least successful with Asian languages
