import os
import sqlite3
from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)

def init_db():
    """Initializes the database and scans the static folder for machinery images."""
    db_path = os.path.join(os.getcwd(), 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create the table immediately so the app never fails to find it
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machinery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            parent_cat TEXT,
            image_path TEXT
        )
    ''')
    
    # 2. Check if we have already scanned the images
    cursor.execute('SELECT COUNT(*) FROM machinery')
    count = cursor.fetchone()[0]
    
    # 3. If the table is empty, scan the static directory
    if count == 0:
        static_dir = os.path.join(app.root_path, 'static')
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    if file.lower().endswith(valid_extensions):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, static_dir)
                        
                        # Extract categories from folder names
                        category = os.path.basename(root)
                        parent_path = os.path.dirname(root)
                        parent_cat = os.path.basename(parent_path) if parent_path != static_dir else "General"
                        
                        # Format the display name (e.g., 'jaw_crusher.jpg' -> 'Jaw Crusher')
                        display_name = os.path.splitext(file)[0].replace('_', ' ').replace('-', ' ').title()
                        
                        cursor.execute(
                            'INSERT INTO machinery (name, category, parent_cat, image_path) VALUES (?, ?, ?, ?)',
                            (display_name, category, parent_cat, relative_path)
                        )
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    query = request.args.get('search')
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if query:
            cursor.execute("SELECT * FROM machinery WHERE name LIKE ? OR category LIKE ?", 
                           ('%'+query+'%', '%'+query+'%'))
        else:
            cursor.execute('SELECT * FROM machinery ORDER BY parent_cat DESC, category ASC')
        items = cursor.fetchall()
    except sqlite3.OperationalError:
        # Fallback if the table hasn't finished being created
        items = []
        
    conn.close()
    return render_template('inventory.html', machinery=items)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download-catalog')
def download_catalog():
    # Make sure catalog.pdf exists in your /static folder
    return send_from_directory('static', 'catalog.pdf', as_attachment=True)

# Run initialization BEFORE the app starts
init_db()

if __name__ == '__main__':
    # Use port 10000 for Render compatibility
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)