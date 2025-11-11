# pip install flasgger
from flasgger import Swagger
from flask import Flask, request, jsonify

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/submit-info', methods=['POST'])
def submit_info():
    """
    Register new peer
    ---
    tags:
      - Tracker
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            ip:
              type: string
              example: "192.168.10.151"
            port:
              type: integer
              example: 9001
            protocol:
              type: string
              example: "tcp"
    responses:
      201:
        description: Peer registered
    """
    data = request.get_json()
    return jsonify(data), 201

if __name__ == '__main__':
    app.run(port=8000)
