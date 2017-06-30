import sys
import psycopg2

con = None

try:
		# move these params into config file 
		con = psycopg2.connect(
        dbname='d13pa0qbkldmjt',
        user='rdfbcmaswxjcko',
        password='0a3874c4cf059d20bfc7abcd6768f33bdd8669cdd884239543dd29db405c9001',
        host='ec2-50-19-83-146.compute-1.amazonaws.com',
        port=5432
    )

		cur = con.cursor()

		cur.execute("DROP TABLE IF EXISTS Audio_files CASCADE")
		cur.execute("CREATE TABLE Audio_files(File_id BIGSERIAL PRIMARY KEY, Name TEXT, Number_of_speakers INT, Duration DECIMAL)")

		cur.execute("DROP TABLE IF EXISTS Segments CASCADE")
		cur.execute("CREATE TABLE Segments(Segment_id BIGSERIAL PRIMARY KEY, File_id INT REFERENCES Audio_files(File_id), Segment_time INT, Speaker_id INT)")

		con.commit()

except psycopg2.DatabaseError, e:

	print 'Error %s' % e
	sys.exit(1)

finally:

	if con:
		con.close()

