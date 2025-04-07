# PDF Redaction Tool

A web application for redacting sensitive information from PDF documents.

## Features

- Upload PDF files for processing
- Automatically detects and redacts sensitive information:
  - Personal names
  - Email addresses
  - Phone numbers
  - Social Security Numbers
  - Credit card numbers
  - Dates
  - Addresses
  - Company names
  - Financial information
  - IDs (passports, driver's licenses)
  - Network information (IP addresses)
- Displays redaction statistics
- Shows redacted text with highlighted redactions

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CID_Scanning
   ```

2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

## Running the Application

### Option 1: Using the Start Script (Recommended)

Run the application using the provided start script:

```
python start_app.py
```

This will:
- Start the backend server on port 8001
- Start the frontend development server on port 3000
- Display the IP addresses for accessing the application
- Open the application in your default browser

### Option 2: Manual Start

1. Start the backend server:
   ```
   cd backend
   python main.py
   ```

2. In a separate terminal, start the frontend server:
   ```
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Accessing from Other Computers

To access the application from other computers on the same network:

1. Make sure both the backend and frontend servers are running
2. Find your computer's IP address (displayed when using the start script)
3. On the other computer, open a web browser
4. Navigate to `http://<your-ip-address>:3000`

## Troubleshooting

- **Port conflicts**: If either port 8001 or 3000 is already in use, you can modify the port numbers in:
  - Backend: `backend/main.py`
  - Frontend: `frontend/src/config.js`

- **CORS issues**: If you encounter CORS errors, make sure the backend's CORS configuration includes the correct origins.

- **Network access**: Ensure your firewall allows connections to ports 8001 and 3000.

## License

[MIT License](LICENSE)
