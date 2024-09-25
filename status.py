import time 
import sys

# Initialize global variables to track time and data
start_time = None
previous_time = None
previous_bytes = 0
total_bytes = 0

async def progress(current, total, file_name, task):
    global start_time, previous_time, previous_bytes, total_bytes

    # Initialize timers and bytes on the first call
    if start_time is None:
        start_time = time.time()
        previous_time = start_time

    # Calculate percentage
    percentage = current * 100 / total

    # Update total bytes downloaded
    total_bytes = current

    # Get current time
    current_time = time.time()

    # Calculate elapsed time
    elapsed_time = current_time - start_time

    # Calculate speed
    if elapsed_time > 0:
        speed = (current - previous_bytes) / (current_time - previous_time)  # bytes per second
        previous_time = current_time
        previous_bytes = current

        # Convert speed to MB/s
        speed_mbps = speed / (1024 * 1024)  # Convert to MB/s

        # Update progress in the same line
        sys.stdout.write(f"\rProgress: {percentage:.1f}% {file_name}| {task} Speed: {speed_mbps:.2f} MB/s")
    else:
        # Update percentage only initially
        sys.stdout.write(f"\rProgress: {percentage:.1f}%")
    
    sys.stdout.flush()  # Ensure the output is written immediately

    # Return None, so the download can continue
    return None

async def finish_download():
    global start_time, total_bytes

    # Calculate average speed after the download is complete
    elapsed_time = time.time() - start_time  # Total elapsed time
    if elapsed_time > 0:
        average_speed_mbps = total_bytes / elapsed_time / (1024 * 1024)  # Convert to MB/s
        print(f"\nDownload completed! Average Speed: {average_speed_mbps:.2f} MB/s")
    else:
        print("\nDownload completed! Unable to calculate average speed.")

async def finish_upload():
    global start_time, total_bytes

    # Calculate average speed after the download is complete
    elapsed_time = time.time() - start_time  # Total elapsed time
    if elapsed_time > 0:
        average_speed_mbps = total_bytes / elapsed_time / (1024 * 1024)  # Convert to MB/s
        print(f"\nUpload completed! Average Speed: {average_speed_mbps:.2f} MB/s")
    else:
        print("\nUpload completed! Unable to calculate average speed.")

# Reset variables when starting a new download
async def reset_progress():
    global start_time, previous_time, previous_bytes
    start_time = None
    previous_time = None
    previous_bytes = 0
