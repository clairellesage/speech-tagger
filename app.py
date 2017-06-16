import sys
from audioSegmentation import speakerDiarization as sD
import psycopg2
import os
try:
    from urllib.parse import urlparse2
except ImportError:
    from urlparse2 import urlparse2
import murl

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

  print "\nFile:", filename
  print "Number of speakers:", number_of_speakers
  print "Duration:", duration, "seconds"
  print "Speaker array =", speaker_arr

  con = None

  try:

    # urlparse2.uses_netloc.append("postgres")
    # url = urlparse2.urlparse(os.environ["postgres://rdfbcmaswxjcko:0a3874c4cf059d20bfc7abcd6768f33bdd8669cdd884239543dd29db405c9001@ec2-50-19-83-146.compute-1.amazonaws.com:5432/d13pa0qbkldmjt"])
#     url = murl.Url('postgres://rdfbcmaswxjcko:0a3874c4cf059d20bfc7abcd6768f33bdd8669cdd884239543dd29db405c9001@ec2-50-19-83-146.compute-1.amazonaws.com:5432/d13pa0qbkldmjt')
#     print url

# postgres://user:pass@host.com:5432/path?k=v#f

    con = psycopg2.connect(
        dbname='postgres',
        user='rdfbcmaswxjcko',
        password='0a3874c4cf059d20bfc7abcd6768f33bdd8669cdd884239543dd29db405c9001',
        host='ec2-50-19-83-146.compute-1.amazonaws.com',
        port=5432
    )

    # con = psycopg2.connect("dbname='speechtag' user='josh' host='localhost' password='lighthouse123'")  
    cur = con.cursor()

    cur.execute("INSERT INTO Audio_files(Name, Number_of_speakers, Duration) VALUES (%s, %s, %s) RETURNING File_id",\
      (filename, number_of_speakers, duration))
    speaker_id = cur.fetchone()[0]

    for index, item in enumerate(speaker_arr, 1):
      cur.execute("INSERT INTO Segments(Segment_time, File_id, Speaker_id) VALUES (%s, %s, %s)",\
      (index, speaker_id, item))

    con.commit()
    print "\nSpeaker diariziation for", filename, "successfully inserted into database."

  except psycopg2.DatabaseError, e:

    print 'Error %s' % e
    sys.exit(1)
  
  finally:

    if con:
      con.close()

formatSDarr(runSD(filename))  