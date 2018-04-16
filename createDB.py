import sqlite3

conn = sqlite3.connect('SO-Python.db')
c = conn.cursor()
c.execute("""
CREATE TABLE SOPython
(
QUESTION_ID INT PRIMARY KEY NOT NULL ,
QUESTION_NAME TEXT NOT NULL ,
FAVORITE_COUNT INT NOT NULL,
QUESTION_VOTE INT NOT NULL ,
ANSWER_VOTE INT,
ANSWER_TEXT TEXT
)
""")
conn.commit()
print('Table created')
conn.close()
