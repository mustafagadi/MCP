# Import necessary libraries
from flask import Flask, request, jsonify   # Flask core and request handling
from outlook_mcp_server import tool_registry  # Your custom tool registry with tools like list_recent_emails, etc.
from mcp.server.fastmcp import Context        # Optional: Context object if needed by tools
import traceback                              # For error traceback printing

# Initialize Flask app
app = Flask(__name__)

# Define the /ask endpoint to handle all tool-based requests
@app.route("/ask", methods=["POST"])
def ask():
    # Get JSON data from the incoming request
    data = request.get_json(force=True)
    tool = data.get("tool")           # The tool name (e.g., "search_emails")
    args = data.get("args", {})       # The arguments to pass to the tool function

    # Log the incoming request
    print("-- Incoming Request --")
    print("Tool:", tool)
    print("Args:", args)
    print("Tool Type:", type(tool))
    print("Args Type:", type(args))

    # Check if tool name is provided
    if not tool:
        return jsonify({"error": "'tool' is required."}), 400

    # Check if the tool exists in the tool registry
    if tool not in tool_registry:
        return jsonify({"error": f"Tool '{tool}' not found."}), 404

    # Ensure args is a dictionary (or try to parse it if it's a JSON string)
    if not isinstance(args, dict):
        try:
            import json
            args = json.loads(args)   # Convert JSON string to dict if needed
        except Exception:
            return jsonify({"error": "'args' must be a dictionary or JSON string."}), 400

    # Try executing the tool function
    try:
        # Call the tool with keyword arguments unpacked from the args dictionary
        result = tool_registry[tool](**args)

        # Return the result in a JSON response
        return jsonify({"result": result}), 200
    except Exception as e:
        # Print full traceback to console for debugging
        print("Error occurred while executing tool:")
        traceback.print_exc()

        # Return an error message with details
        return jsonify({
            "error": "Execution failed",
            "details": str(e)
        }), 500

# Define a simple health check route for GET /
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Python MCP Server is running"}), 200

# Handle 404 Not Found for invalid routes
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Wrong route"}), 404

# Start the server on port 8000
if __name__ == "__main__":
    app.run(port=8000)
