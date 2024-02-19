from flask import Flask, request, jsonify
import json
import boto3

app = Flask(__name__)
sqs_client = boto3.client("sqs")

@app.route("/", methods=["POST"])
def handle_webhook():
    try:
        payload = json.loads(request.data)
        if "title" not in payload or "priority" not in payload or "description" not in payload:
            return jsonify({"error": "Missing required fields"}), 400
        
        title = payload["title"].strip()
        description = payload["description"].strip()
        priority = int(payload["priority"])

        queue_name_map = {
            1: "high-priority-queue",
            2: "medium-priority-queue",
            3: "low-priority-queue"
        }

        queue_name = queue_name_map.get(priority)
        if not queue_name:
            return jsonify({"error": "Invalid priority"}), 400

        enqueue_message({"title": title, "description": description}, queue_name)
        return jsonify({"message": "Your ticket has been sent"}), 200
    except ValueError:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as exc:
        return jsonify({"error": f"Unhandled error: {str(exc)}"}), 500

def enqueue_message(message, queue_name):
    json_message = json.dumps(message)
    try:
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
    except sqs_client.exceptions.QueueDoesNotExist:
        queue_url = sqs_client.create_queue(QueueName=queue_name)["QueueUrl"]
    
    sqs_client.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=json_message
    )

if __name__ == "__main__":
    app.run(debug=True) 
