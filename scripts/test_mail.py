import socket
import ssl
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection(host='imap.gmail.com', port=993):
    connected = False
    for attempt in range(5):
        try:
            # Create IPv4 socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Wrap socket with SSL
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            logger.info(f"Connection succeeded on attempt {attempt + 1}")
            connected = True
            
            # Clean up
            ssl_sock.close()
            break
            
        except Exception as e:
            logger.error(f"Connection failed on attempt {attempt + 1}: {str(e)}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
    if not connected:
        logger.error("All connection attempts failed")
    else:
        logger.info("Test completed successfully")

if __name__ == "__main__":
    test_connection()