from flask import Flask, request, jsonify
from outlook_mcp_server import tool_registry  # dictionary where your tools are registered
from mcp.server.fastmcp import Context
import traceback

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    tool = data.get("tool")
    args = data.get("args", {})

    print("-- Incoming Request --")
    print("Tool:", tool)
    print("Args:", args)
    print("Tool Type:", type(tool))
    print("Args Type:", type(args))

    # Check if the tool exists in the registry
    if tool not in tool_registry:
        return jsonify({"error": f"Tool '{tool}' not found."}), 404

    # Ensure args is a dictionary (or parse JSON string)
    if not isinstance(args, dict):
        try:
            import json
            args = json.loads(args)
        except Exception:
            return jsonify({"error": "'args' must be a dictionary or JSON string."}), 400

    try:
        # Call the tool function with arguments unpacked
        result = tool_registry[tool](**args)
        return jsonify({"result": result}), 200
    except Exception as e:
        print("Error occurred while executing tool:")
        traceback.print_exc()
        return jsonify({
            "error": "Execution failed",
            "details": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Python MCP Server is running"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Wrong route"}), 404

if __name__ == "__main__":
    app.run(port=8000)
