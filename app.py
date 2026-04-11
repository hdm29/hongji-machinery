import os
import sqlite3
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS machinery')
    cursor.execute('''
        CREATE TABLE machinery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            parent_cat TEXT,
            image_path TEXT
        )
    ''')

    static_dir = os.path.join(app.root_path, 'static')
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.lower().endswith(valid_extensions):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, static_dir)
                    
                    # Category is the folder name (e.g., Jaw Crusher)
                    category = os.path.basename(root)
                    # Parent is the folder above (e.g., crushers)
                    parent_path = os.path.dirname(root)
                    parent_cat = os.path.basename(parent_path) if parent_path != static_dir else "General"

                    display_name = os.path.splitext(file)[0].replace('_', ' ').replace('-', ' ').title()

                    cursor.execute(
                        'INSERT INTO machinery (name, category, parent_cat, image_path) VALUES (?, ?, ?, ?)',
                        (display_name, category, parent_cat, relative_path)
                    )
    
    conn.commit()
    conn.close()
    print("Scan complete. Database updated.")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Sort: Crushers first, then specific types
    cursor.execute('SELECT * FROM machinery ORDER BY parent_cat DESC, category ASC')
    items = cursor.fetchall()
    conn.close()
    return render_template('inventory.html', machinery=items)

@app.route('/download-catalog')
def download_catalog():
    # Make sure your file is renamed to 'catalog.pdf' in the static folder
    return send_from_directory('static', 'catalog.pdf', as_attachment=True)
@app.route('/contact')
def contact():
    return render_template('contact.html')
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
    @app.route('/inventory')
def inventory():
    from flask import request
    query = request.args.get('search')
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if query:
        # Search by name or category
        cursor.execute("SELECT * FROM machinery WHERE name LIKE ? OR category LIKE ?", 
                       ('%'+query+'%', '%'+query+'%'))
    else:
        cursor.execute('SELECT * FROM machinery ORDER BY parent_cat DESC, category ASC')
        
    items = cursor.fetchall()
    conn.close()
    return render_template('inventory.html', machinery=items)