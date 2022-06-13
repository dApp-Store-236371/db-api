from http import HTTPStatus
import os
from flask import Flask, Response, send_from_directory
import json
from threading import Thread
import psycopg2
from urllib.parse import urlparse
from asgiref.wsgi import WsgiToAsgi


IS_HOSTED = True

##DB CONNECTION



def get_db_connection():
    result = urlparse("postgres://nofufthy:we3Erf889-HjVtanL4MF7mS0UsRvGf1T@dumbo.db.elephantsql.com/nofufthy")
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    db_connection = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname,
        port = port
    )
    return db_connection

    
def db_fetch(db_connection, sql: str):
    print("DB FETCH: " + sql)
    try:
        with db_connection.cursor() as cur:
            
            cur.execute(sql)
            db_connection.commit() 
            
            res = tuple(cur.fetchall())
            return res

    except (Exception, psycopg2.DatabaseError) as error:
        print("SQL db_fetch Error: ", error)
        return Tuple()

def get_filtered_app_ids(db_connection, offset, length, textFilter, categoryFilter, ratingFilter):

    sql = f"""SELECT id 
            FROM public.apps 
            WHERE 
                (name ILIKE '%{textFilter}%')
                AND
                category ILIKE '%{categoryFilter}%' 
                AND 
                rating >= {ratingFilter} 
            ORDER BY id ASC
            OFFSET {offset} 
            LIMIT {length};   
        """
    raw_res = db_fetch(db_connection, sql)
    print("raw res: ", raw_res)
    ids = [res[0] for res in raw_res]
    
    print("ids: ", ids)
    return ids




# ###### SERVER ###############
# statics_dir = os.path.abspath('mysite/build') if IS_HOSTED else os.path.abspath('./build')

app_wsgi = Flask(__name__)
app = WsgiToAsgi(app_wsgi)
# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve(path):
#     print("static_folder = ", app.static_folder)
#     if path != "" and os.path.exists(app.static_folder + '/' + path):
#         return send_from_directory(app.static_folder, path)
#     elif path == '':
#         return send_from_directory(app.static_folder, 'index.html')
#     else:
#         return Response(status=HTTPStatus.NOT_FOUND, response="The page does not exist. Error 404.")

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/apps/filtered/<offset>/<length>/<rating_filter>/<category_filter>", methods=['GET'], defaults={'text_filter': ""})
@app.route("/apps/filtered/<offset>/<length>/<rating_filter>/<category_filter>/", methods=['GET'], defaults={'text_filter': ""})
@app.route("/apps/filtered/<offset>/<length>/<rating_filter>/<category_filter>/<text_filter>", methods=['GET'])
def get_apps_filtered(offset, length, text_filter, rating_filter, category_filter):
    
    rating_filter = float(rating_filter)
        
    if(category_filter == "ALL"):
        category_filter = ""

    # if text_filter is None or text_filter == "__ALL__":
    
    print("text_filter = ", text_filter, type(text_filter))
    print("rating_filter = ", rating_filter, type(rating_filter))
    print("category_filter = ", category_filter)
    
    ids = []
    with get_db_connection() as conn:
        ids = get_filtered_app_ids(conn, offset, length, text_filter, category_filter, rating_filter)
        
    
    
    return Response(status=HTTPStatus.OK, response=json.dumps(ids),  mimetype='application/json')



if __name__ == "__main__":
    app.run(debug=True)
