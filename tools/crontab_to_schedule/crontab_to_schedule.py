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

from __future__ import annotations
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from os import PathLike

import matplotlib.pyplot as plt

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.logger import error, log_warning
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
        r"(.*)"  # command
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


def expand_time_field(field: str, max_value: int) -> list[int]:
    """
    Expands a time field like '0,15' or '7-18' into a list of integers.
    :param field:
    :param max_value:
    :return:
    """
    result = set()
    for part in field.split(","):
        if "-" in part:  # Range
            start, end = {int, part.split("-")}
            result.update(range(start, end + 1))
        elif part == "*":  # Wildcard
            result.update(range(max_value))
        else:  # Single value
            result.add(int(part))
    return sorted(result)


def generate_intervals(
        time_delta_mins: int,
        scope_restriction: str,
        date_to_check: datetime | str = None
) -> list[tuple[datetime, datetime]]:
    """
    Generates time intervals based on the interval and scope.
    :param time_delta_mins: size of the time interval in minutes.
    :param scope_restriction: day, <start-time>-<end-time>
    :param date_to_check: date to generate interval for.
    :return: intervals
    """
    if date_to_check is None:
        date_to_check = datetime.now()

    reval_intervals = []
    if scope_restriction == "day":
        start = date_to_check.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_to_check.replace(hour=23, minute=59, second=59, microsecond=0)
    elif "-" in scope_restriction:  # Time range
        start_str, end_str = scope_restriction.split("-")
        start = datetime.strptime(start_str, "%H:%M").replace(
            year=date_to_check.year,
            month=date_to_check.month,
            day=date_to_check.day,
        )
        end = datetime.strptime(end_str, "%H:%M").replace(
            year=date_to_check.year,
            month=date_to_check.month,
            day=date_to_check.day,
        )
    else:
        raise ValueError(f"Invalid scope_restriction format: {scope_restriction}")

    current = start
    while current <= end:
        next_time = current + timedelta(minutes=time_delta_mins)
        reval_intervals.append((current, min(next_time, end)))
        current = next_time

    return reval_intervals


def collect_jobs(
        schedule: list[dict[str, str]],
        intervals: list[tuple[datetime, datetime]]
) -> list[tuple[str, list[str]]]:
    """
    Collects jobs from schedule for each interval.
    :param schedule:
    :param intervals:
    :return:
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


def plot_job_intervals(job_intervals: list[tuple[str, list[str]]], title: str):
    """
    Plots the number of jobs per interval
    :param job_intervals:
    :param title:
    :return:
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


def write_to_csv(file_path: str, rows: list[list[str]], headers: list[str]):
    """
    Writes rows to a CSV file with the given headers..
    :param file_path:
    :param rows:
    :param headers:
    :return:
    """
    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerows(rows)


def write_to_json(job_intervals: list[tuple[str, str]], output_file: PathLike | str):
    """
    Writes job intervals to a JSON file in the specified format.
    :param job_intervals: List of (interval_label, jobs) tuples.
    :param output_file: Path to the output JSON file.
    :return:
    """
    # Create the JSON structure
    json_data = [
        {
            "time": interval,
            "numberOfJobs": len(jobs),
            "jobs": jobs
        }
        for interval, jobs in job_intervals
    ]

    # Sort the data by numberOfJobs in descending order
    json_data.sort(key=lambda entry: entry["numberOfJobs"], reverse=True)

    # Write to the JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)


# Example Usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a graph and schedule from crontab.")
    parser.add_argument(
        "--crontab-file", "-c",
        default="crontab.txt",
        help='File with crontab entries, defaults to "crontab.csv"'
    )
    parser.add_argument("--interval", "-i",
                        type=int,
                        default=1,
                        help="Interval size in minutes, defaults to 1")
    parser.add_argument("--scope", "-s",
                        default="day",
                        help="Scope of the schedule, e.g., day/12:00-18:00")
    parser.add_argument("--reference-date", "-r",
                        default=None,
                        help=f"Reference date in format 'YYYY-mm-dd', defaults to {datetime.now().date()}")
    parser.add_argument("--timeline-output", "-t",
                        default="timeline.csv",
                        help="Output timeline for jobs.")
    parser.add_argument("--job-counts-output", "-j",
                        default="job_counts.csv",
                        help="Output CSV for job counts.")
    parser.add_argument("--plot", "-p",
                        default=False,
                        action="store_true",
                        help="display a plot of number of jobs per time time_delta_mins.")

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
    intervals = generate_intervals(interval, scope_restriction=scope, date_to_check=reference_date)

    # Collect jobs in intervals
    job_intervals = collect_jobs(schedule=schedule, intervals=intervals)

    # Write the schedule to a CSV
    schedule_rows = [[interval] + jobs for interval, jobs in job_intervals]

    write_to_csv(args.schedule_output, schedule_rows, ["Interval", "Jobs"])

    # Write to a JSON file
    write_to_json(job_intervals=job_intervals, output_file=f"{this_dir}/job_schedule.json")

    # Write job counts to a separate CSV
    job_count_rows = [[interval, len(jobs)] for interval, jobs in job_intervals]
    write_to_csv(args.job_counts_output, job_count_rows, ["Interval", "Number of Jobs"])

    if args.plot:
        # Plot the intervals
        plot_job_intervals(job_intervals, title=f"Jobs per {interval}-Minute Interval ({scope})")
