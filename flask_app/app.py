from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/<path:filename>')
def get_data(filename):
    # return send_from_directory('data', filename)
    return send_from_directory('/app/data', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)