import socket
import subprocess
import os
import sys
import webbrowser
import time
from pathlib import Path

def get_ip_address():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

def start_backend():
    """Start the backend server"""
    backend_dir = Path("backend")
    backend_script = backend_dir / "main.py"
    
    if not backend_script.exists():
        print(f"Error: Backend script not found at {backend_script}")
        sys.exit(1)
    
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, str(backend_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Check if the process is still running
    if backend_process.poll() is not None:
        stdout, stderr = backend_process.communicate()
        print("Error starting backend server:")
        print(stderr)
        sys.exit(1)
    
    return backend_process

def start_frontend():
    """Start the frontend development server"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
    
    print("Starting frontend server...")
    os.chdir(frontend_dir)
    
    # Use npm start to run the development server
    frontend_process = subprocess.Popen(
        ["npm", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for the server to start
    time.sleep(5)
    
    # Check if the process is still running
    if frontend_process.poll() is not None:
        stdout, stderr = frontend_process.communicate()
        print("Error starting frontend server:")
        print(stderr)
        sys.exit(1)
    
    return frontend_process

def main():
    """Main function to start the application"""
    print("Starting PDF Redaction Tool...")
    
    # Get the local IP address
    ip_address = get_ip_address()
    
    # Start the backend server
    backend_process = start_backend()
    
    # Start the frontend server
    frontend_process = start_frontend()
    
    # Display connection information
    print("\n" + "="*50)
    print("PDF Redaction Tool is running!")
    print("="*50)
    print(f"Backend API: http://{ip_address}:8001")
    print(f"Frontend (local): http://localhost:3000")
    print(f"Frontend (network): http://{ip_address}:3000")
    print("\nTo access from other computers on the network:")
    print(f"1. Open a web browser on the other computer")
    print(f"2. Navigate to: http://{ip_address}:3000")
    print("\nPress Ctrl+C to stop the servers")
    print("="*50 + "\n")
    
    # Open the local frontend in the default browser
    webbrowser.open("http://localhost:3000")
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
