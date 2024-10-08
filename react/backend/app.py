# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app, resources={r"/api/*":{"origins": "*"}})  # Enable CORS to allow React frontend to communicate with Flask

# @app.route('/api/data', methods=['POST'])
# def receive_data():
#     data = request.json  # Receive JSON data from the frontend
#     print(f"Received data: {data}")

#     # Process the data if needed
#     response = {"message": "Data received successfully", "received": data}
#     return jsonify(response)

# if __name__ == '__main__':
#     app.run(host = '0.0.0.0', port=5001, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins": "*"}})

# Route to handle user input data
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    print(f"Received user data: {data}")
    return jsonify({"message": "User data received successfully", "received": data})

# Route to handle data from external API
@app.route('/api/apidata', methods=['POST'])
def receive_api_data():
    api_data = request.json
    print(f"Received API data: {api_data}")
    return jsonify({"message": "API data received successfully", "received": api_data})

if __name__ == '__main__':
    app.run(port=5001, debug=True)