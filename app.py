import sys
from audioSegmentation import speakerDiarization as sD
import psycopg2
from psycopg2.extensions import adapt, register_adapter, AsIs

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
  # print "Speaker array =", speaker_arr

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

    # con = psycopg2.connect("dbname='speechtag' user='josh' host='localhost' password='lighthouse123'")  
    cur = con.cursor()

    cur.execute("INSERT INTO Audio_files(Name, Number_of_speakers, Duration) VALUES (%s, %s, %s) RETURNING File_id",\
      (filename, number_of_speakers, duration))

    # fetches File_id from insert
    file_id = cur.fetchone()[0]
    print "File id: ", file_id

    # creates array of triples for segments table
    speaker_arr = [(int(file_id), segment_time, speaker_id) for segment_time, speaker_id in enumerate(arr)]
    print "Speaker array: ", speaker_arr

    class Point(object):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    def adapt_point(point):
        x = adapt(point.x).getquoted()
        y = adapt(point.y).getquoted()
        z = adapt(point.z).getquoted()
        return AsIs("'(%s, %s, %s)'" % (x, y, z))

    register_adapter(Point, adapt_point)

    my_point_list = [Point(p[0], p[1], p[2]) for p in speaker_arr]

    # insert = "insert into Segments values (%s, %s, %s)"
    # cur.executemany(insert, (speaker_arr),)

    # insert = """
    #     insert into Segments values (File_id, Segment_time, Speaker_id)
    #     select File_id, Segment_time, Speaker_id
    #     from unnest(%s) s(File_id int, Segment_time int, Speaker_id int)
    #     returning File_id
    # ;"""

    # cur.execute(insert, (speaker_arr,))


    insert = "insert into Segments values (%s, %s, %s)"
    cur.execute(insert, (speaker_arr),)
    
    # cur.execute("INSERT INTO Segments (p) VALUES (%s)",
    #              (Point(1.23, 4.56),))

    # args_str = ','.join(cur.mogrify("(%s,%s,%s)", (my_point_list),))
    # cur.execute("INSERT INTO Segments VALUES " + args_str)
    con.commit()

    print "\nSpeaker diariziation for", filename, "successfully inserted into database."

  except psycopg2.DatabaseError, e:

    print 'Error %s' % e
    sys.exit(1)
  
  finally:

    if con:
      con.close()

runSD(filename)


    # # Clearly slow to insert one row at a time
    # for row in speaker_arr:
    #     cur.execute('insert into Segments values (%s,%s)', row)
     
    # # Should be much faster, but isn't
    # cur.executemany('insert into data values (%s,%s,%s)', myData)
     
    # # This hack is much faster
    # dataText = ','.join(cur.mogrify('(%s,%s)', row) for row in speaker_arr)
    # cur.execute('insert into Segments values ' + dataText)


    # for index, item in enumerate(speaker_arr, 1):
    #   cur.execute("INSERT INTO Segments(Segment_time, File_id, Speaker_id) VALUES (%s, %s, %s)",\
    #   (index, speaker_id, item))
