import os
import sys
import threading

# Add the current directory to sys.path so 'bharat' package can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("🚀 Starting SentinelOps Predictive Monitoring Dashboard...")
print(f"📂 Project Root: {current_dir}")

try:
    from bharat.app import app
    from bharat.services.scheduler_service import start_scheduler
    
    print("✅ Backend modules loaded successfully.")
    
    # Start the scheduler in a background thread
    # We use the app context to ensure the scheduler has access to the database
    def run_scheduler():
        print("🟢 Background Scheduler started from launcher")
        with app.app_context():
            start_scheduler()

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Run the Flask app
    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000, debug=False) # Turned off debug to avoid double start
        
except ImportError as e:
    print(f"❌ Error loading modules: {e}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
