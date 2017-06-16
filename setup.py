import sys
import psycopg2
import os
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

con = None

try:
		# move these params into config file 
		# con = psycopg2.connect("dbname='speechtag' user='josh' host='localhost' password='lighthouse123'")  
		con = psycopg2.connect(
		    database=url.path[1:],
		    user=url.username,
		    password=url.password,
		    host=url.hostname,
		    port=url.port
		)
		cur = con.cursor()

		cur.execute("DROP TABLE IF EXISTS Audio_files CASCADE")
		cur.execute("CREATE TABLE Audio_files(File_id BIGSERIAL PRIMARY KEY, Name TEXT, Number_of_speakers INT, Duration DECIMAL)")

		cur.execute("DROP TABLE IF EXISTS Segments CASCADE")
		cur.execute("CREATE TABLE Segments(Segment_id BIGSERIAL PRIMARY KEY, Segment_time INT, File_id INT REFERENCES Audio_files(File_id), Speaker_id INT)")

		con.commit()

except psycopg2.DatabaseError, e:

	print 'Error %s' % e
	sys.exit(1)

finally:

	if con:
		con.close()

