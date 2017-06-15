## About
This prototype uses the pyAudioAnalysis library to perform speaker diarization through unsupervised segmentation on .wav files. Given any audio file, it can extract the number of speakers and who spoke when (down to the second) and save this into the database.

## Installation
 * Install dependencies:
 ```
pip install numpy matplotlib scipy sklearn hmmlearn simplejson eyed3 pydub psycopg2
```
 * Set up the database:
```
python setup.py
```

 * Run the program with your audio file :
```
python app.py {filename}
```