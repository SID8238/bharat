import os
import sys
import subprocess

# Add the current directory to sys.path so 'bharat' package can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("🚀 Starting SentinelOps Predictive Monitoring Dashboard...")
print(f"📂 Project Root: {current_dir}")

try:
    from bharat.app import app
    print("✅ Backend modules loaded successfully.")
    
    # Run the Flask app
    # We use a wrapper to ensure the environment is correct
    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000, debug=True)
        
except ImportError as e:
    print(f"❌ Error loading modules: {e}")
    print("\nAttempting to run as module...")
    subprocess.run([sys.executable, "-m", "bharat.app"])
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
