from flask import Flask, request, jsonify
from outlook_mcp_server import tool_registry
from mcp.server.fastmcp import Context

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    tool = data.get("tool")
    args = data.get("args", {})

    if not tool:
        return jsonify({"error": "'tool' is required."}), 400

    if tool not in tool_registry:
        return jsonify({"error": f"Tool '{tool}' not found."}), 404

    if not isinstance(args, dict):
        return jsonify({"error": "'args' must be a dictionary."}), 400

    try:
        result = tool_registry[tool](**args)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000)
