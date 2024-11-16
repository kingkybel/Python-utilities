#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/crontab_to_schedule/crontab_to_schedule.py
# Description:  Make a schedule from a crontab
#
# Copyright (C) 2024 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-05-13
# @author: Dieter J Kybelksties

import argparse
import csv
import os
import re
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.logger import error, log_warning
from datetime import datetime, timedelta
from typing import List, Tuple
import matplotlib.pyplot as plt
from lib.file_utils import read_file



def parse_crontab(crontab_lines: list[str]) -> list[dict[str, str]]:
    """Parses crontab entries into a structured list."""
    entries = []
    cron_pattern = re.compile(
        r"^\s*"
        r"(\S+)\s+"  # minute
        r"(\S+)\s+"  # hour
        r"(\S+)\s+"  # day of month
        r"(\S+)\s+"  # month
        r"(\S+)\s+"  # day of week
        r"(.*)"      # command
    )

    for line in crontab_lines:
        line = line.strip()
        if not line or line.startswith("#"):  # Ignore comments and empty lines
            continue
        match = cron_pattern.match(line)
        if match:
            minute, hour, dom, month, dow, command = match.groups()
            entries.append({
                "minute": minute,
                "hour": hour,
                "day_of_month": dom,
                "month": month,
                "day_of_week": dow,
                "command": command.strip(),
            })
        else:
            log_warning(f"Unrecognized crontab entry: {line}")
    return entries


def expand_time_field(field: str, max_value: int) -> List[int]:
    """Expands a time field like '0,15' or '7-18' into a list of integers."""
    result = set()
    for part in field.split(","):
        if "-" in part:  # Range
            start, end = map(int, part.split("-"))
            result.update(range(start, end + 1))
        elif part == "*":  # Wildcard
            result.update(range(max_value))
        else:  # Single value
            result.add(int(part))
    return sorted(result)


def generate_intervals(
    interval: int,
    scope: str,
    reference_date: datetime = None
) -> List[Tuple[datetime, datetime]]:
    """
    Generates time intervals based on the interval and scope.
    """
    if reference_date is None:
        reference_date = datetime.now()

    intervals = []
    if scope == "day":
        start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = reference_date.replace(hour=23, minute=59, second=59, microsecond=0)
    elif "-" in scope:  # Time range
        start_str, end_str = scope.split("-")
        start = datetime.strptime(start_str, "%H:%M").replace(
            year=reference_date.year,
            month=reference_date.month,
            day=reference_date.day,
        )
        end = datetime.strptime(end_str, "%H:%M").replace(
            year=reference_date.year,
            month=reference_date.month,
            day=reference_date.day,
        )
    else:
        raise ValueError(f"Invalid scope format: {scope}")

    current = start
    while current <= end:
        next_time = current + timedelta(minutes=interval)
        intervals.append((current, min(next_time, end)))
        current = next_time

    return intervals


def collect_jobs(
    schedule: list[dict[str, str]],
    intervals: list[tuple[datetime, datetime]]
) -> List[Tuple[str, List[str]]]:
    """
    Collects jobs for each interval.
    """
    jobs_by_interval = []

    for start, end in intervals:
        interval_jobs = []
        for entry in schedule:
            minutes = expand_time_field(entry["minute"], 60)
            hours = expand_time_field(entry["hour"], 24)

            for hour in hours:
                for minute in minutes:
                    job_time = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if start <= job_time < end:
                        interval_jobs.append(entry["command"])
        interval_label = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        jobs_by_interval.append((interval_label, interval_jobs))

    return jobs_by_interval


def plot_job_intervals(job_intervals: List[Tuple[str, List[str]]], title: str):
    """
    Plots the number of jobs per interval.
    """
    interval_labels = [interval for interval, _ in job_intervals]
    job_counts = [len(jobs) for _, jobs in job_intervals]

    plt.figure(figsize=(12, 6))
    plt.bar(interval_labels, job_counts, color="skyblue")
    plt.xlabel("Time Intervals")
    plt.ylabel("Number of Jobs")
    plt.title(title)
    # Show every nth label to avoid clutter
    n = max(1, len(interval_labels) // 10)
    plt.xticks(range(0, len(interval_labels), n), interval_labels[::n], rotation=90)
    plt.tight_layout()
    plt.show()


def write_to_csv(file_path: str, rows: List[List[str]], headers: List[str]):
    """Writes rows to a CSV file with the given headers."""
    with open(file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerows(rows)


# Example Usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a graph and schedule from crontab.")
    parser.add_argument(
        "--crontab-file", "-c",
        default=f"{this_dir}/crontab.csv",
        help=f'File with crontab entries, defaults to "{this_dir}/crontab.csv"'
    )
    parser.add_argument("--interval", "-i", type=int, default=1, help="Interval size in minutes, defaults to 1")
    parser.add_argument("--scope", "-s", default="day", help="Scope of the schedule, e.g., day/12:00-18:00")
    parser.add_argument(
        "--reference-date", "-r",
        default=None,
        help=f"Reference date in format 'YYYY-mm-dd', defaults to {datetime.now().date()}"
    )
    parser.add_argument("--schedule-output", "-so", default="minute_schedule.csv", help="Output CSV for schedule.")
    parser.add_argument("--job-counts-output", "-jo", default="job_counts.csv", help="Output CSV for job counts.")

    args = parser.parse_args()

    try:
        crontab_content = read_file(args.crontab_file)
    except FileNotFoundError:
        error(f"Crontab file '{args.crontab_file}' not found.")
        sys.exit(1)

    interval = args.interval
    scope = args.scope
    reference_date = datetime.now()
    if args.reference_date is not None:
        reference_date = datetime.strptime(args.reference_date, "%Y-%m-%d")

    # Parse the crontab
    schedule = parse_crontab(crontab_content.splitlines())

    # Generate time intervals
    intervals = generate_intervals(interval, scope, reference_date=reference_date)

    # Collect jobs in intervals
    job_intervals = collect_jobs(schedule=schedule, intervals=intervals)

    # Write the schedule to a CSV
    schedule_rows = [[interval, ", ".join(jobs)] for interval, jobs in job_intervals]
    write_to_csv(args.schedule_output, schedule_rows, ["Interval", "Jobs"])

    # Write job counts to a separate CSV
    job_count_rows = [[interval, len(jobs)] for interval, jobs in job_intervals]
    write_to_csv(args.job_counts_output, job_count_rows, ["Interval", "Number of Jobs"])

    # Plot the intervals
    plot_job_intervals(job_intervals, title=f"Jobs per {interval}-Minute Interval ({scope})")
    #
    # # Print job intervals
    # for interval_label, jobs in job_intervals:
    #     print(f"{interval_label}: {len(jobs)} jobs")