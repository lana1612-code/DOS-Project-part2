from flask import Flask, jsonify, request
import sqlite3
import threading
import os

app = Flask(__name__)

thread_data = threading.local()

pathDB_1 = os.path.join(os.path.dirname(__file__), 'catalog2.db')
pathDB_2 = os.path.join(os.path.dirname(__file__), '../catalog-1/catalog1.db')

def catalog1_db_connection():
    if not hasattr(thread_data, 'catalog1_connection'):
        thread_data.catalog1_connection = sqlite3.connect(pathDB_1)
        thread_data.catalog1_connection.row_factory = sqlite3.Row  
    return thread_data.catalog1_connection

def catalog2_db_connection():
    if not hasattr(thread_data, 'catalog2_connection'):
        thread_data.catalog2_connection = sqlite3.connect(pathDB_2)
        thread_data.catalog2_connection.row_factory = sqlite3.Row  
    return thread_data.catalog2_connection

@app.teardown_appcontext
def release_db_connection(exception):
    if hasattr(thread_data, 'catalog2_connection'):
        thread_data.catalog2_connection.close()
    if hasattr(thread_data, 'catalog1_connection'):
        thread_data.catalog1_connection.close() 
          
@app.route('/', methods=['GET'])
def catalog2():  
    return """  
    <html>  
        <head>  
            <title>Catalog page</title>  
        </head>  
        <body style="background-color: black; color: white;">  
            <h1 style="text-align: center; margin: 400px 0;" >Welcome to Catalog Page</h1>  
        </body>  
    </html>  
    """
#! work: done
@app.route('/retrieve/item/<id>', methods=['GET'])
def get_book_by_id(id):
    if not id.isdigit():
        return jsonify({"error": "Book ID must be numeric"}), 400

    database = catalog2_db_connection()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM books WHERE id=?", (id,))
    book = cursor.fetchone()
    cursor.close()

    if book:
        return jsonify(dict(book)), 200
    else:
        return jsonify({"error": "Book not found"}), 404

#! work: done
@app.route('/retrieve/topic/<topic>', methods=['GET'])
def get_books_by_topic(topic):
    database = catalog2_db_connection()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM books WHERE topic=?", (topic,))
    books = cursor.fetchall()
    cursor.close()

    if books:
        return jsonify([dict(book) for book in books]), 200
    else:
        return jsonify({"error": "No books found for this topic"}), 404

#! work: done
@app.route('/modify/<int:id>', methods=['PUT'])
def modify_book(id):
   
    data = request.get_json()
    updated_price = data.get('price')
    updated_quantity = data.get('quantity')

    
    if updated_price is None and updated_quantity is None:
        return jsonify({"error": "No update data provided"}), 400

    database1 = catalog1_db_connection()
    database2 = catalog2_db_connection()

    cursor1 = database1.cursor()
    cursor2 = database2.cursor()

    if updated_price is not None:
        cursor1.execute("UPDATE books SET price=? WHERE id=?", (updated_price, id))
    if updated_quantity is not None:
        cursor1.execute("UPDATE books SET quantity=? WHERE id=?", (updated_quantity, id))

    if updated_price is not None:
        cursor2.execute("UPDATE books SET price=? WHERE id=?", (updated_price, id))
    if updated_quantity is not None:
        cursor2.execute("UPDATE books SET quantity=? WHERE id=?", (updated_quantity, id))

    database1.commit()
    cursor1.close()
    database2.commit()
    cursor2.close()
   
    cursor2 = database2.cursor()
    cursor2.execute("SELECT * FROM books WHERE id=?", (id,))
    book = cursor2.fetchone()
    cursor2.close()

    if book:
        return jsonify(dict(book)), 200
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=6002)