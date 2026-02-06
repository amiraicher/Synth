import logging
import os
import tempfile
from datetime import datetime

def setup_logging():
    # Create a log file in the system temp directory
    temp_dir = tempfile.gettempdir()
    log_filename = f"synth_lite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(temp_dir, log_filename)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler() # Also print to console
        ]
    )
    
    logging.info(f"Logging initialized. Log file: {log_path}")
    return log_path
