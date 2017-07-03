import sys
from audioSegmentation import speakerDiarization as sD
import psycopg2
from io import StringIO

filename = sys.argv[1]

def runSD(filename):
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

    # creates array of triples for segments table
    speaker_arr = [[int(file_id), segment_time, speaker_id] for segment_time, speaker_id in enumerate(arr)]
    print "Speaker array: ", speaker_arr

    f = open('speaker_arr.py', 'r')
    # f.write(unicode(str(speaker_arr)))
    v = f.read()

    # prints 
    # <_io.StringIO object at 0x7fda8d5e4e50>
    # [[10, 0, 3], [10, 1, 3], [10, 2, 3], [10, 3, 3], [10, 4, 3], [10, 5, 3], [10, 6, 3], [10, 7, 3], [10, 8, 3], [10, 9, 3], [10, 10, 0], [10, 11, 0], [10, 12, 0], [10, 13, 0], [10, 14, 0], [10, 15, 0], [10, 16, 0], [10, 17, 0], [10, 18, 0], [10, 19, 0], [10, 20, 1], [10, 21, 1], [10, 22, 1], [10, 23, 1], [10, 24, 1], [10, 25, 1], [10, 26, 1], [10, 27, 1], [10, 28, 2], [10, 29, 2], [10, 30, 2], [10, 31, 2], [10, 32, 2], [10, 33, 2], [10, 34, 2], [10, 35, 2], [10, 36, 2], [10, 37, 2], [10, 38, 2], [10, 39, 2], [10, 40, 4], [10, 41, 4]]  

# file_id', 'segment_time', 
    # try:
    #   cur.copy_from(v, 'Segments', columns=('speaker_id'), sep=",")
    #   cur.execute("select * from Segments;")
    #   print "Segments table:", cur.fetchall()
    #   # prints []

    import numpy
    a = numpy.asarray(speaker_arr)
    numpy.savetxt("speaker_arr.csv", a, delimiter="\t", fmt='%1.0f')

    o = open('speaker_arr.csv', 'r')
    print o

    try: 
      cur.copy_from(o, 'Segments', columns=('file_id', 'segment_time', 'speaker_id'), sep='\t')
      cur.execute("select * from Segments;")
      print cur.fetchall()
      print "\nSpeaker diariziation for", filename, "successfully inserted into database."
    except psycopg2.DatabaseError, e: 
      print e, "didn't copy"




    con.commit()

  except psycopg2.DatabaseError, e:

    print 'Error %s' % e
    sys.exit(1)
  
  finally:

    if con:
      con.close()

runSD(filename)