import sqlite3
conn = sqlite3.connect('apple.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM pages LIMIT 2')
pages = cursor.fetchall()


for page in pages:
    page_name, page_content = page
    page_content = page_content.split('\n')
    print( page_name, page_content)

conn.close()
