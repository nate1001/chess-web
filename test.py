from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import func, select

db_uri = 'postgres:///chess'
engine = create_engine(db_uri)
# Create a MetaData instance
metadata = MetaData()
#print (metadata.tables)
# reflect db schema to MetaData
metadata.reflect(bind=engine)
for key in (metadata.tables):
	print (key)
raise

position = Table("v_position", metadata, autoload_with=engine)
conn = engine.connect()
print (func.random_search())
res = conn.execute(select([func.random_search()]))
for row in res:
    print(row)
    print(row.site)
