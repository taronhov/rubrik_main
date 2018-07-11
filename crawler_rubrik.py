import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError, RqlDriverError, ReqlOpFailedError

import json

"""  This is a data crawler/scraper script foo Rubrik.com website, using its JSON API capabilities and 
    and utilizing Python driver and ReQL query language of Rethink DB (r.http command for accessing external APIs)"""

def dbSetup():

    connection = r.connect( "localhost", 28015)
    try:
        # r.db_create("test").run(connection)
        r.db("test").table_create("rubrik").run(connection)
        r.table_create("stargazers").run(connection)
        print 'Database setup completed.'
    except RqlRuntimeError:
        print 'App database already exists.'
    finally:
        connection.close()

def main():
    dbSetup()
    connection = r.connect( "localhost", 28015)
    try:
        r.table("stargazers").insert(r.http('https://api.github.com/repos/rethinkdb/rethinkdb/stargazers')).run(connection)
        
        # r.table("rubrik").insert(r.http('https://www.rubrik.com/customers/', result_format='json')).run(connection)
        # r.table("google").insert(r.http('www.google.com')).run(connection)

        # cursor = r.table("stargazers").run(connection)
        # for document in cursor:
        #     print(document)
        aaa = r.http('https://api.github.com/repos/rethinkdb/rethinkdb/stargazers').count().run(connection)
        print (aaa)
        cursor = r.table("google").run(connection)
        for document in cursor:
            print(document)

    except ReqlOpFailedError:
        print 'Table already exists in database.'
    finally:
        connection.close()

    # print (aaa)




if __name__ == "__main__":
    main()


