import time 
import sys

# Dictionary to track progress per file
progress_trackers = {}

async def progress(current, total, file_id, task):
    """Handles progress tracking for each file."""
    global progress_trackers

    # Initialize tracker if it doesn't exist for this file_id
    if file_id not in progress_trackers:
        progress_trackers[file_id] = {
            "start_time": time.time(),
            "previous_time": time.time(),
            "previous_bytes": 0,
            "total_bytes": total
        }

    tracker = progress_trackers[file_id]

    # Calculate percentage
    percentage = current * 100 / total

    # Update total bytes downloaded/uploaded
    tracker["total_bytes"] = current

    # Get current time
    current_time = time.time()

    # Calculate elapsed time
    elapsed_time = current_time - tracker["start_time"]

    # Calculate speed
    if elapsed_time > 0:
        speed = (current - tracker["previous_bytes"]) / (current_time - tracker["previous_time"])  # bytes per second
        tracker["previous_time"] = current_time
        tracker["previous_bytes"] = current

        # Convert speed to MB/s
        speed_mbps = speed / (1024 * 1024)  # Convert to MB/s

        # Update progress in the same line
        sys.stdout.write(f"\rProgress: {percentage:.1f}% {file_id}| {task} Speed: {speed_mbps:.2f} MB/s")
    else:
        # Update percentage only initially
        sys.stdout.write(f"\rProgress: {percentage:.1f}%")

    sys.stdout.flush()  # Ensure the output is written immediately

    # Return None to allow download/upload to continue
    return None

async def finish_task(file_id):
    """Handles the completion of a task and calculates average speed."""
    global progress_trackers

    # Ensure the tracker for this file_id exists
    if file_id not in progress_trackers:
        print(f"Task {file_id} does not exist in progress trackers.")
        return

    tracker = progress_trackers[file_id]
    
    # Calculate total elapsed time
    elapsed_time = time.time() - tracker["start_time"]

    # Calculate average speed if there's elapsed time
    if elapsed_time > 0:
        average_speed_mbps = tracker["total_bytes"] / elapsed_time / (1024 * 1024)  # Convert to MB/s
        print(f"\nTask completed! {file_id} Average Speed: {average_speed_mbps:.2f} MB/s")
    else:
        print(f"\nTask completed! {file_id} Unable to calculate average speed.")

    # Cleanup: Remove the tracker for this file after task completion
    del progress_trackers[file_id]

async def reset_progress(file_id):
    """Resets the progress for a specific file task."""
    global progress_trackers

    # Ensure the tracker for this file_id exists before resetting
    if file_id not in progress_trackers:
        # Initialize a new tracker for this file if not present
        progress_trackers[file_id] = {
            "start_time": time.time(),  # Reset start time
            "previous_time": time.time(),  # Reset previous time
            "previous_bytes": 0,  # Reset previous bytes
            "total_bytes": 0  # Optionally reset total bytes
        }
    else:
        # Reset values in the existing tracker
        progress_trackers[file_id]["start_time"] = time.time()
        progress_trackers[file_id]["previous_time"] = time.time()
        progress_trackers[file_id]["previous_bytes"] = 0
        progress_trackers[file_id]["total_bytes"] = 0  # Optionally reset total bytes

