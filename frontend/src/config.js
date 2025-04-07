// Configuration for the application
const config = {
  // Backend API URL - replace with your server's IP address when deploying
  // Example: "http://192.168.1.100:8001" for local network
  // Use window.location.hostname to dynamically get the current host
  apiUrl: `http://${window.location.hostname}:8001`
};

export default config;
