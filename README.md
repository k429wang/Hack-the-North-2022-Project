# TraveLens

Created Kai Wang, Keegan Liu, Joey Wang, and Freeman Huang, at Hack the North 2022

## Inspiration
Have you ever travelled to a country with a language you can't understand? Are you tired of always pulling out your phone to open a translation app? Want a fast and convenient way of translating a foreign language in real time? Then **TraveLens** is the perfect solution for you!

## What it does
Read any text and blink your eyes twice to capture a block of text. Then, listen as the text is **translated** and played out loud automagically!

## How we built it
- Python, AdHawk API, Google Cloud, OpenCV
1. The **AdHawk MindLink** is worn and calibrated
2. To trigger the translation, blink twice to get the **AdHawk API** to return the coordinates and a screenshot
3. Utilize the **Google Cloud Vision API**, which uses OCR to detect text in the image
4. The language is identified and the text is translated
5. The translated text is read out loud using **Google Cloud TTS**

## Challenges we ran into
Prior to HTN, no one on the team had ever used any of these APIs before, so there was quite the steep learning curve for every member of our team. 
Additionally, fine-tuning the eye tracking software to properly track the **coordinates** of our **gaze** proved to be quite difficult. We had to employ many different methods to track and record the coordinates, which involved a great deal of trial and error. 
Cropping the image also proved to be surprisingly difficult. We had to figure out how different 3D coordinate systems acted on a 2D image, and how these interactions could help us crop out intended blocks of text.
Finally, we utilized a variety of different APIs, to help with **language identification** and translation. To map all of the different features together, members of our team had to surf through mountains of documentation and YouTube tutorials!

## Accomplishments that we're proud of
Getting everything finished! This was, by far, the most ambitious project any of us had ever worked on before, so it felt great when we finally got it done in such a short period of time.

## What we learned
- How eye tracking hardware and software works, and how it can interact with Google Cloud, OpenCV, and other platforms
- How to effectively use **version control** and project boards to boost efficiency and productivity
- How to use different types of APIs to reduce the amount of workload on individual developers

## What's next for TraveLens
We have many future plans for this product that we didn't get around to implementing this weekend at HTN:
1. A minimalistic **GUI**, where the user can select a native language to translate to
2. Easily accessible **translation history**
3. Built in **earpieces**, to help prevent users from disturbing their surroundings with audio playback
