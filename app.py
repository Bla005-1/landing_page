from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/builds/<path:filename>')
def builds(filename):
    return send_from_directory('static/builds', filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
