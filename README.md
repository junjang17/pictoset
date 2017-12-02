1. Tesseract OCR
    **WHAT IS PYTESSERACT?**
        Tesseract(v3.05) is an Optical Character Recognition (OCR) engine that Google wrote. This engine allows for image to text
        recognition. In order to use Tesseract with different languages, you need to "train" the engine using various text
        files of a specific format that Google decided. Google trained the OCR for us, so we don't have to worry about the
        actual training process. However, we do need to install the training data that Google has put on the github for
        tesseract (https://github.com/tesseract-ocr/tessdata/blob/3.04.00/jpn.traineddata). You need to store the language
        data files in your tesseract "tessdata" folder, which is located in the directory you download tesseract.

    **PYTESSERACT**
        Now if we can imagine tesseract as the engine that's doing the heavy lifting, Pytesseract is simply a python
        wrapper that allows us to interact with Tesseract using python code. This is great for us because we need to use
        flask for the webapp. Pytesseract uses tesseract (which is used using command line), so it is important to have
        tesseract set in your PATH, or change the necessary line of code in your pytesseract.py file.

    **TEXTBLOB**
        Textblob is the package I'm thinking of using to detect langauge and differentiate b/t terms/definitions
        ex. For each word we get from img to text, check if word is of specified lang (probably the terms), then
        set those terms into a list of their own for easier manipulation (maybe even enumerate? or is that unnecessary)
            - Using textblob requires something called punkt, which can be downloaded using
                import nltk
                nltk.download("punkt")
            - If SSL error gets thrown out, go to your Applications/python3.6/Install Certificates.command, run Install Certificates.command
            - Try nltk.download("punkt") again

2. QUIZLET API
    **OAUTH PROTOCOL**
        Oauth is a method of allowing third party apps to use an API's services. The core concept of Quizlet's
        OAUTH takes 3 steps:
            1. User logs into Quizlet
            2. User allows you to access their accounts for only specific actions, also known as scopes, such as viewing
               user's flashcard sets, writing flashcard sets, etc. Then, API hands the webapp a "token"
            3. Webapp trades the token for an access code, and presents access code to API whenever using API's services
    **REQUESTS MODULE**
        The requests module for python greatly simplifies making HTTP requests. This is extremely helpful for setting up
        Oauth because Oauth involves posting to the quizlet API for access code. Also, this module is used to post
        requests to the API for the user's data (flashcard sets, etc.) 
