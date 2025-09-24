# Utility functions
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def format_response(data):
    """Format response data for consistent API output."""
    return {
        "status": "success",
        "data": data,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }
