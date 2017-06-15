import sys
from audioSegmentation import speakerDiarization as sD
import psycopg2

filename = sys.argv[1]

def runSD(filename):
  speakerDiarization = sD(filename, 0, mtSize=2.0, mtStep=0.1, stWin=0.05, LDAdim=35, PLOT=False)
  return speakerDiarization[0]

def formatSDarr(arr):
  rounded_arr = arr.astype(int)
  int_arr = []
  for i in rounded_arr:
    j = int(i)
    int_arr.append(j)
  speaker_arr = int_arr[::10]
  duration = len(int_arr) / 10
  number_of_speakers = len(set(speaker_arr))
  insertIntoDB(filename, number_of_speakers, duration, speaker_arr)

def insertIntoDB(filename, number_of_speakers, duration, speaker_arr):

  con = None

  try:
      # move these params into config file 
      con = psycopg2.connect("dbname='speechtag' user='josh' host='localhost' password='lighthouse123'")  
      cur = con.cursor()

      cur.execute("INSERT INTO Audio_files(Name, Number_of_speakers, Duration) VALUES (%s, %s, %s) RETURNING File_id",\
        (filename, number_of_speakers, duration))
      speaker_id = cur.fetchone()[0]

      for index, item in enumerate(speaker_arr, 1):
        cur.execute("INSERT INTO Segments(Segment_time, File_id, Speaker_id) VALUES (%s, %s, %s)",\
        (index, speaker_id, item))

      con.commit()

  except psycopg2.DatabaseError, e:

    print 'Error %s' % e
    sys.exit(1)
  
  finally:

    if con:
      con.close()

formatSDarr(runSD(filename))  