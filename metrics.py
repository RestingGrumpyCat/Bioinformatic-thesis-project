import re
import sqlite3
import csv
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


conn = sqlite3.connect('/Users/j-abbit/PycharmProjects/Thesis/gisaidACK.db')
print("Opened database successfully")


conn.execute("CREATE TABLE IF NOT EXISTS temp1 AS SELECT Genome.PID, Genome.Accession, Genome.CollectionDate, Genome.SubmissionDate, Publication.publicationDate, Genome.Contributor FROM Genome, Publication WHERE Genome.Accession==Publication.Accession;")
cur = conn.cursor()

cur.execute('''WITH RECURSIVE split( Accession, CollectionDate, SubmissionDate,  publicationDate , C, rest) AS (
  SELECT Accession, CollectionDate, SubmissionDate, publicationDate,' ', Contributor || ',' FROM temp1
   UNION ALL
  SELECT Accession, CollectionDate, SubmissionDate, publicationDate,
         substr(rest, 0, instr(rest, ',')),
         substr(rest, instr(rest, ',')+1)
    FROM split
   WHERE rest <> '')
SELECT Accession, CollectionDate, SubmissionDate, publicationDate, C
FROM split
WHERE C <> ''
AND length(C) > 2
ORDER BY C;
''')


data = cur.fetchall()
Accession = []
CollectionDate = []
SubmissionDate = []
publicationDate = []
contributor = []

for row in data:
    Accession.append((row[0]))
    CollectionDate.append(datetime.strptime(row[1],'%Y-%m-%d'))
    SubmissionDate.append(datetime.strptime(row[2],'%Y-%m-%d'))
    publicationDate.append(datetime.strptime(row[3],'%Y-%m-%d'))
    contributor.append(row[4])

#diff1= SubmissionDate - CollectionDate
#diff2= publicationDate - SubmissionDate
diff1 = []
diff2 = []
for i in range(0, len(CollectionDate)):
    diff = SubmissionDate[i] - CollectionDate[i]
    diff1.append(diff.days)

for i in range(0, len(CollectionDate)):
    diff = publicationDate[i] - SubmissionDate[i]
    diff2.append(diff.days)


Seen = set()
Counts1 = dict()
Counts2 = dict()

individual1 = []
avg1 = []
individual2 = []
avg2 = []
averages1 = dict()
averages2 = dict()

for i in range(len(contributor)):
    current = contributor[i]
    if current in Seen:
        continue
    Seen.add(current)
    Counts1[current] = []
    Counts2[current] = []

    for j in range(i, len(contributor)):
        if contributor[j] == current:
            Counts1[current].append(diff1[j])
            Counts2[current].append(diff2[j])


for contributor in Counts1.keys():
    count = 0
    total = 0
    for time in Counts1[contributor]:
        total += time
        count += 1
    averages1[contributor] = total/count

for contributor in Counts2.keys():
    count = 0
    total = 0
    for time in Counts2[contributor]:
        total += time
        count += 1
    averages2[contributor] = total/count

for key in averages1:
    individual1.append(key)
    avg1.append(averages1[key])

for key in averages2:
    individual2.append(key)
    avg2.append(averages2[key])


print("The average time used to submit sample from collecting group by sequence contributor")
print(averages1)
print("The average time used to for submitted sequence to get published group by sequence contributor")
print(averages2)

plt.hist(diff1)
plt.show()
plt.hist(diff2)
plt.show()
plt.hist(avg1)
plt.show()
plt.hist(avg2)
plt.show()


conn.commit()
cur.close()

conn.close()


