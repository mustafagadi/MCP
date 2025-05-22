from flask import Flask, request, jsonify
from outlook_mcp_server import tool_registry

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    tool = data.get("tool")
    args = data.get("args", {})
    try:
        result = tool_registry[tool](**args)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=8000)
