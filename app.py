import sys
import os
from audioSegmentation import speakerDiarization as sD
import psycopg2
import numpy
from io import StringIO

filename = sys.argv[1]

def runSD(splitFile):
  speakerDiarization = sD(filename, 0, mtSize=2.0, mtStep=0.1, stWin=0.05, LDAdim=35, PLOT=False)
  insertIntoDB(filename, speakerDiarization[0])

def insertIntoDB(filename, arr):
  # turns numpy array into python array, and sets diarization to speaker/second
  arr = arr.astype(int).tolist()[::10]
  duration = len(arr)
  number_of_speakers = len(set(arr))

  print "\nFile:", filename
  print "Number of speakers:", number_of_speakers
  print "Duration:", duration, "seconds"

  con = None

  try:

    #store these
    con = psycopg2.connect(
        dbname='d13pa0qbkldmjt',
        user='rdfbcmaswxjcko',
        password='0a3874c4cf059d20bfc7abcd6768f33bdd8669cdd884239543dd29db405c9001',
        host='ec2-50-19-83-146.compute-1.amazonaws.com',
        port=5432
    )
    
    cur = con.cursor()

    cur.execute("INSERT INTO Audio_files(Name, Number_of_speakers, Duration) VALUES (%s, %s, %s) RETURNING File_id",\
      (filename, number_of_speakers, duration))

    # fetches File_id from insert
    file_id = cur.fetchone()[0]
    print "File id: ", file_id

    # creates array of rows for segments table
    speaker_arr = [[int(file_id), segment_time, speaker_id] for segment_time, speaker_id in enumerate(arr)]
    print "Speaker array: ", speaker_arr

    # writes speaker_arr to .csv as buffer
    a = numpy.asarray(speaker_arr)
    numpy.savetxt("speaker_arr.csv", a, delimiter="\t", fmt='%1.0f')
    rows = open('speaker_arr.csv', 'r')

    # bulk insert from .csv
    cur.copy_from(rows, 'Segments', columns=('file_id', 'segment_time', 'speaker_id'), sep='\t')
    # uncomment to view segments insert array
    # cur.execute("select * from Segments;")
    # print cur.fetchall()

    con.commit()
    print "\nSpeaker diariziation for", filename, "successfully inserted into database."

  except psycopg2.DatabaseError, e:

    print 'Error %s' % e
    sys.exit(1)
  
  finally:

    if con:
      con.close()

runSD(filename)