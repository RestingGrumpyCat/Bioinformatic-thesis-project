import csv
import json
import re
from time import sleep
import sqlite3
import fitz
from urllib.request import Request, urlopen


def text_prep(text):
    txt = text.replace(
        '''We gratefully acknowledge the following Authors from the Originating laboratories responsible for obtaining the specimens, as well as the\nSubmitting laboratories where the genome data were generated and shared via GISAID, on which this research is based.\nAll Submitters of data may be contacted directly via www.gisaid.org\nAuthors are sorted alphabetically.\n''',
        '')
    txt = txt.replace('Accession ID\nOriginating Laboratory\nSubmitting Laboratory\nAuthors\n', '')
    txt = txt.lstrip()
    return txt


def write_to_file(list, filename):
    file = open(f'/Users/j-abbit/Documents/Bioinformatics_Thesis/{filename}', 'w')
    for elem in list:
        for parts in elem:
            file.write(parts + "\n")

    file.close()


def group(seq, sep):
    g = []
    for el in seq:
        if el == sep:
            yield g
            g = []
            continue
        g.append(el)
    yield g


def fetch_postion(list, keyword):
    indices = [i for i, x in enumerate(list) if x == keyword]
    return indices


def parser(text):
    statSplittor = []
    unparsedIDs = []
    unparsedStats = []
    sep = []
    indices = []

    matched = re.findall(r'(.+?\n(?=EPI_ISL_\d+,*\s+))', text)
    for elem in matched:
        if not re.match(r'EPI_ISL_.*\s*', elem):
            statSplittor.append(elem)

    statSplittor = [e.rstrip() for e in statSplittor]
    statSplittor = list(dict.fromkeys(statSplittor))

    split = text.split('\n')

    for elem in split:
        if re.match(r'EPI_ISL_.*\s*', elem):
            unparsedIDs.append(elem)
        else:
            unparsedStats.append(elem)

    for elem in unparsedStats:
        if (len(elem) == 0):
            unparsedStats.remove((elem))

    for elem in unparsedIDs:
        if (len(elem) == 0):
            unparsedIDs.remove((elem))

    try:
        while True:
            unparsedStats.remove('see above')
    except ValueError:
        pass

    unparsedStats = list(filter(None, unparsedStats))

    for elem in statSplittor:
        i = fetch_postion(unparsedStats, elem)
        indices = indices + i

    indices.sort()

    while indices:
        i = indices.pop()
        unparsedStats.insert(i + 1, '\n')

    stats = list(group(unparsedStats, '\n'))

    for elem in unparsedIDs:
        # if not ended with ",", it is the last ID for this section
        if elem[-1] != ',':
            sep.append(elem)
    for elem in sep:
        unparsedIDs.insert(unparsedIDs.index(elem) + 1, '\n')

    # making a list of list by seperator '\n'
    IDs = list(group(unparsedIDs, '\n'))
    IDs = [x for x in IDs if x]
    stats = [x for x in stats if x]

    return IDs, stats


# return the index of last accession ID
def get_last_section(text):
    matched = re.findall(r'(.+?\n(?=EPI_ISL_\d+,*\s+))', text)
    keyword = ''
    for elem in matched:
        if not re.match(r'EPI_ISL_.*\s*', elem):
            keyword = elem
    index = text.rfind(keyword)

    return index


def get_first_section(text):
    matched = re.findall(r'(.+?\n(?=EPI_ISL_\d+,*\s+))', text)
    keyword = ''
    for elem in matched:
        if not re.match(r'EPI_ISL_.*\s*', elem):
            keyword = elem
            break
    index = text.find(keyword) + len(keyword)
    return index






removed = ''
doc = fitz.open('/Users/j-abbit/Documents/Bioinformatics_Thesis/first10K.pdf')
IDs = []
stats = []

pageNum = doc.page_count
counter = 0
brokenIDs = []
brokenStats = []

while counter < pageNum:
    page = doc[counter]
    text = page.get_text()
    text = text_prep(text)
    index = get_first_section(text)
    start = text[0: index:]

    if (counter != 0):
        char = removed + start
        ID = re.findall(r'EPI_ISL_.*\s*', char)
        brokenIDs.append(ID)
    lastIndex = get_last_section(text)
    removed = text[lastIndex::]
    text = text[index: lastIndex:]

    l1, l2 = parser(text)
    IDs = IDs + l1
    stats = stats + l2
    counter = counter + 1

strippedBrokenIDs = []
for elem in brokenIDs:
    temp = []
    for part in elem:
        temp.append(part.rstrip())
    strippedBrokenIDs.append(temp)
concatID = IDs + strippedBrokenIDs
finalIDs = []

for elem in concatID:
    temp = []
    str = ''
    string = str.join(elem)
    temp = re.findall(r'EPI_ISL_[0-9]{6}', string)
    finalIDs.append(temp)


orig_lab = []
subm_lab = []
authors = []
brokenStats = []

temp = []
col_dates=[]
sub_dates=[]
with open("/Users/j-abbit/Documents/Bioinformatics_Thesis/date.tsv") as infile:
    before = csv.reader(infile, delimiter="\t")

    for line in before:
        for i in range(0, len(finalIDs)):
            for j in range(0,len(finalIDs[i])):
                if line[0] == finalIDs[i][j]:
                    print(line[0])
                    temp.append(line[0])
                    col_dates.append(line[1])
                    sub_dates.append(line[2])

k = 0

for id in temp:
    seg1 = id[10:12]
    seg2 = id[12:14]
    jsonData = "https://www.epicov.org/acknowledgement/" + seg1 + "/" + seg2 + '/' + id + '.json'
    req = Request(jsonData, headers={'User-Agent': 'Mozilla/5.0'})
    sleep(1)
    data = urlopen(req).read().decode()
    data = json.loads(data)
    o_lab = data['covv_orig_lab']
    s_lab = data['covv_subm_lab']
    au = data['covv_authors']
    orig_lab.append(o_lab)
    subm_lab.append(s_lab)
    authors.append(au)
    k = k+1
    print(k)


conn = sqlite3.connect('gisaidACK.db')
print("Opened database successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS 'Genome'
         ('PID' INT PRIMARY KEY NOT NULL,
          'Accession' CHAR(50),
          'Orig_lab' CHAR(50),
          'Subm_lab' CHAR(50),
          'SubmissionDate' CHAR(50),
          'CollectionDate' CHAR(50),
          'Contributor' CHAR(50));''')
print("Table 'Genome' created successfully")
cur = conn.cursor()

for i in range(0, len(temp)):
    conn.execute("INSERT INTO Genome VALUES (?,?,?,?,?,?,?)",
                (i, temp[i], orig_lab[i], subm_lab[i], col_dates[i], sub_dates[i],authors[i]))

conn.commit()
cur.close()
print("Inserted.")

cur = conn.cursor()

conn.commit()
cur.close()

conn.close()
