import time 
import sys

async def progress(current, total):
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
        sys.stdout.write(f"\rProgress: {percentage:.1f}% | Speed: {speed_mbps:.2f} MB/s")
    else:
        # Update percentage only initially
        sys.stdout.write(f"\rProgress: {percentage:.1f}%")
    
    sys.stdout.flush()  # Ensure the output is written immediately

    # Return None, so the download can continue
    return None

