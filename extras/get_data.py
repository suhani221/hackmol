import sqlite3

# Connect to the database
conn = sqlite3.connect('orange.db')
c = conn.cursor()

# Execute the query
c.execute("SELECT Sentence,Page_Number, MAX(Font_Size) FROM orange GROUP BY Page_Number")

# Retrieve the results
results = c.fetchall()
print(type(results))
# Print the results
for row in results:
    print(row)

conn.close()