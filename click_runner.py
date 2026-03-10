"""
Connectivity Clicker Runner - Runs the clicker multiple times on a schedule
"""
import argparse
import time
from datetime import datetime, timedelta
import subprocess
import sys


def run_clicker_loop(interval_minutes=4, duration_minutes=60):
    """
    Runs the clicker script repeatedly at specified intervals for a given duration.

    Args:
        interval_minutes (int): Minutes between each click (default: 4)
        duration_minutes (int): Total duration to run in minutes (default: 60)

    Returns:
        int: Number of successful clicks
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    interval_seconds = interval_minutes * 60

    click_count = 0
    success_count = 0

    print(f"Starting clicker runner")
    print(f"Interval: {interval_minutes} minutes")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    while datetime.now() < end_time:
        click_count += 1
        current_time = datetime.now()

        print(f"\n[{current_time.strftime('%H:%M:%S')}] Click #{click_count}")
        print("-" * 60)

        try:
            # Run the click_summary.py script in headless mode
            result = subprocess.run(
                [sys.executable, "click_summary.py", "--headless"],
                capture_output=False,
                text=True,
                timeout=interval_seconds - 10  # Leave buffer before next run
            )

            if result.returncode == 0:
                success_count += 1
                print(f"✓ Click #{click_count} successful")
            else:
                print(f"✗ Click #{click_count} failed with return code {result.returncode}")

        except subprocess.TimeoutExpired:
            print(f"✗ Click #{click_count} timed out")
        except Exception as e:
            print(f"✗ Click #{click_count} error: {e}")

        # Calculate time until next run
        next_run_time = current_time + timedelta(seconds=interval_seconds)

        # Check if we have time for another run
        if next_run_time >= end_time:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Next run would be after end time, stopping.")
            break

        # Wait until next run
        sleep_seconds = (next_run_time - datetime.now()).total_seconds()
        if sleep_seconds > 0:
            print(f"\nWaiting {sleep_seconds:.0f} seconds until next run at {next_run_time.strftime('%H:%M:%S')}...")
            time.sleep(sleep_seconds)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total clicks attempted: {click_count}")
    print(f"Successful clicks: {success_count}")
    print(f"Failed clicks: {click_count - success_count}")
    print(f"Success rate: {(success_count/click_count*100):.1f}%" if click_count > 0 else "N/A")
    print(f"Duration: {(datetime.now() - start_time).total_seconds()/60:.1f} minutes")

    return success_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the connectivity clicker on a recurring schedule'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=4,
        help='Minutes between each click (default: 4)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Total duration to run in minutes (default: 60)'
    )

    args = parser.parse_args()

    success_count = run_clicker_loop(
        interval_minutes=args.interval,
        duration_minutes=args.duration
    )

    # Exit with success if at least one click succeeded
    exit(0 if success_count > 0 else 1)
