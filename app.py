import sys
from audioSegmentation import speakerDiarization as sD
import psycopg2
import os
import urlparse
import subprocess

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

    proc = subprocess.Popen('heroku config:get DATABASE_URL -a my-heroku-app', stdout=subprocess.PIPE, shell=True)
    db_url = proc.stdout.read().decode('utf-8').strip() + '?sslmode=require'

    conn = psycopg2.connect(db_url)

      # urlparse.uses_netloc.append("postgres")
      # url = urlparse.urlparse(os.environ["DATABASE_URL"])

      # con = psycopg2.connect(
      #     database=url.path[1:],
      #     user=url.username,
      #     password=url.password,
      #     host=url.hostname,
      #     port=url.port
      # )

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