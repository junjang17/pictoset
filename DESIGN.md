# Design Document

## Overview
This design document will discuss Pictoset in two parts:
1. The outside sources used (Tesseract engine, Pytesseract, Quizlet API)
2. Detailed workings of each step in Pictoset when a user creates a Quizlet set using Pictoset
  * Typical Flow: Login with Quizlet → Upload Image → Crop Terms → Crop Definitions → Create Set

### Outside Sources
1. **Tesseract** 
    * Tesseract(v3.05) is an Optical Character Recognition (OCR) engine that Google wrote. This engine allows for image to text
    recognition. In order to use Tesseract with different languages, you need to "train" the engine using various text
    files of a specific format that Google decided. Google trained the OCR for us, so we don't have to worry about the
    actual training process. However, we do need to install the training data that Google has put on the Github for
    [Tesseract](https://github.com/tesseract-ocr/tessdata/blob/3.04.00/jpn.traineddata). All the required data is included in the Pictoset tesseract-data folder. 
    You need to store the language data files in your Tesseract "tessdata" folder, which is located in the directory you download tesseract.

2. **PYTESSERACT**
    * Pytesseract is simply a python wrapper that allows us to interact with Tesseract using python code. This is great for a webapp 
    that uses Tesseract with a python backend through Flask. Pytesseract essentially uses Tesseract by calling Tesseract in the command line, 
    so it is important to have Tesseract set in your PATH.

3. **QUIZLET API**
    * OAUTH PROTOCOL
        * Oauth is a method of allowing third party apps to use an API's services. The core concept of Quizlet's
        OAUTH takes 3 steps:
            1. User logs into Quizlet
            2. User is prompted to allow you to access their accounts for only specific actions, also known as **scopes**, such as viewing
               user's flashcard sets, writing flashcard sets, etc. If user accepts, API hands the webapp a "code" that can be traded for an access token
            3. Webapp trades the code for an access token, and presents access token to API whenever using API's services (via the headers of the POST request made to API)
    * REQUESTS MODULE
        * The requests module for python greatly simplifies making HTTP requests. This is extremely helpful for setting up
        Oauth because Oauth involves making POST requests to the Quizlet API for the access code. Also, this module is used to POST
        requests to the API for the user's data (flashcard sets, etc.)
        
### Step-by-Step Breakdown of Pictoset
  * Logging in
    * As mentioned above, the user logs in with Quizlet using the OAUTH protocol. When the user clicks *Log In*, 
    the app makes a GET request to Quizlet's API passing in various parameters:
      1. **Client ID**- Developer's API ID
      2. **Scope**- Read, Write... the permissions that the user gives to the app to access their account with
      3. **State**- A random string that I pass in that the Quizlet API must return back. I make sure the returned string matches
           the string I sent in order to prevent Cross Site Request Forgery attacks
      4. **Redirect URI**- The route to redirect the user once the code has been received. I redirect the user to the
             */authorize* route of my web app where I handle getting the access token using the code received from Quizlet
    * When Quizlet receives these 4 parameters properly, it redirects the user to the specified route, and it returns
     a code and the state via GET parameters. The web app checks that the state matches the state it sent, and then takes the
     code and makes a POST request back to Quizlet API (to get access token) involving the following parameters:
      1. **Grant Type**- Set to "authorization_code" by default (to specify that we need a authorization token back)
      2. **code**- The code we received from Quizlet earlier
      3. **redirect_uri**- Route to redirect the user once logging in is complete()
      4. **client_id**- The Quizlet devloper's ID that Quizlet API gave me
    * Once POST request is done, user is redirected to home page, and the webapp receives and stores the access token in
      the app session. Login is now complete.

  * Creating a Quizlet Set
    * Creating a Quizlet set takes 4 steps: Uploading image, Cropping terms, Cropping definitions, and Finalizing
      1. Uploading Image
         * First, the user uploads an image to the server to make a Quizlet set out of. Upon user's login, the server
           creates a temporary directory that will store any images that the user uploads. This directory is deleted upon
           user's logout. 
         * The webapp makes sure the selected file is an image by checking the extension (must be .jpg, 
           .jpeg, or .png). The webapp also makes sure that an image file was uploaded. If both these conditions are met,
           the image is saved into the temporary directory and the file path of the image is stored in a session variable
           (for future routes to access).
      2. Cropping Terms
           * Once the image has been uploaded, the user can now select the areas of the image that contains the terms.
             This design decision is a solution for separating the terms and definitions within the user's image.  
           * The cropping image is performed using a library called [jcrop](http://deepliquid.com/content/Jcrop.html) that
             provides image cropping functionality to html. Jcrop doesn't *actually* do the cropping -- it only gives the coordinates
             of the image that the user selected. These coordinates are passed back into the webapp via POST where the webapp
             then uses Python Image Library to crop the image using the coordinates that the user selected in.
           * Once the user crops the terms, the cropped area is saved into the temporary directory as "terms.jpg" and the user is redirected to definition crop.     
           * Although cropping the terms separately helps increase accuracy, the trade-off is that only certain types of images work with the app (images
             where the terms and definitions are far apart enough that a rectangular crop can occur). 
           * After cropping the terms, the user is prompted to crop the definitions.
      3. Cropping Definitions
           * The process of cropping the definitions is exactly the same as cropping the terms. The only difference is that
             after cropping, the file is saved to the temporary directory as "definitions.jpg." 
           * After cropping definitions, the user is taken to finalize the set creation.
      4. Finalizing
           * The last steps include setting the flashcard set's title, term language, and definition language. In order to create
             a set, a POST request is made to Quizlet API with the following parameters:
               1. **Title**- Title that user specifies for set
               2. **Terms[]**- An array of all the terms to be added to the set
               3. **Definitions[]**- An array of all the definitions to be added to the set (terms/definitions array lengths must be equal)
               4. **Lang_Terms**- The language code specifying terms' language that the user passes in from the finalization webpage. 
               5. **Lang_Definitions**- The language code specifying definitions' language that the user passes in.
           * During this step is when the Tesseract image-to-text recognition happens. First, the webapp feeds Tesseract the terms.jpg.
           Tesseract returns one big string that contains all the words it recognized from the image. This big string is then
           split by "\n" (line breaks) and each word is saved into the terms array. This process occurs for the definitions.jpg image as well. 
           Sometimes, the linebreaks are not recognized so errors can happen during set creation because as mentioned above,
           Quizlet requires that term and definition array lengths are equal. 
           
           * Once these words are saved into their respective arrays, the webapp makes a POST request to Quizlet and the set
             is created for the user. Then, the temporary directory is emptied and the user is sent back to the homepage.
  * Log Out
    * When the user decides to log out, the webapp clears session (remove all image paths, the path to temporary directory, access
      token, etc.) and then deletes the temporary directory. The user is redirected to the homepage (where it displays the option
      to log in if there is no access token in session).
               
           
