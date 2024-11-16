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
import os
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


def parse_crontab(crontab: str) -> List[Tuple[int, int, str]]:
    """
    Parses a crontab string and extracts schedule entries.

    Args:
        crontab (str): The crontab content as a string.

    Returns:
        list of tuples: List containing (minute, hour, command).
    """
    import re

    crontab_line_regex = re.compile(r"^(\d{1,2})\s+(\d{1,2})\s+.*?\s+.*?\s+.*?\s+(.+)$")
    schedule = []

    for line in crontab.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):  # Ignore comments or empty lines
            continue

        match = crontab_line_regex.match(line)
        if match:
            minute = int(match.group(1))
            hour = int(match.group(2))
            command = match.group(3).strip()
            schedule.append((minute, hour, command))

    return schedule


def generate_intervals(
        interval: int,
        scope: str,
        reference_date: datetime = None
) -> List[Tuple[datetime, datetime]]:
    """
    Generates time intervals based on the interval and scope.

    Args:
        interval (int): Interval size in minutes.
        scope (str): Time scope, e.g., "day" or "12:00-18:00".
        reference_date (datetime, optional): Reference date.

    Returns:
        list of tuples: List of (start_time, end_time) intervals.
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


def collect_jobs(schedule: List[Tuple[int, int, str]], intervals: List[Tuple[datetime, datetime]]) -> List[
    Tuple[str, List[str]]]:
    """
    Collects jobs for each interval.

    Args:
        schedule (list): Parsed crontab schedule as (minute, hour, command).
        intervals (list): List of (start_time, end_time) intervals.

    Returns:
        list of tuples: List of (interval_label, jobs).
    """
    jobs_by_interval = []

    for start, end in intervals:
        interval_jobs = []
        for minute, hour, command in schedule:
            job_time = datetime.combine(start.date(), datetime.min.time()).replace(hour=hour, minute=minute)
            if start <= job_time < end:
                interval_jobs.append(command)
        interval_label = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        jobs_by_interval.append((interval_label, interval_jobs))

    return jobs_by_interval


def plot_job_intervals(job_intervals: List[Tuple[str, List[str]]], title: str):
    """
    Plots the number of jobs per interval.

    Args:
        job_intervals (list of tuples): List of (interval_label, jobs).
        title (str): Title of the graph.
    """
    interval_labels = [interval for interval, _ in job_intervals]
    job_counts = [len(jobs) for _, jobs in job_intervals]

    plt.figure(figsize=(12, 6))
    plt.bar(interval_labels, job_counts, color="skyblue")
    plt.xlabel("Time Intervals")
    plt.ylabel("Number of Jobs")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


# Example Usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create a graph and schedule from crontab.')
    parser.add_argument("--crontab-file", "-c",
                        default=f"{this_dir}/crontab.csv",
                        help=f'file with crontab entries, defaults to "{this_dir}/crontab.csv"')
    parser.add_argument("--interval", "-i",
                        default=1,
                        help=f"interval size in minutes, defaults to {1}")
    parser.add_argument("--scope", "-s",
                        default="day",
                        help=f"scope of the schedule, day/week/month/12:00-15:00/..., defaults to day")
    parser.add_argument("--reference-date", "-r",
                        default=None,
                        help=f"reference date in format 'YYYY-mm-dd', defaults to {datetime.now().date()}")

    args = parser.parse_args()

    crontab_content = read_file(args.crontab_file)
    interval = int(args.interval)
    scope = args.scope
    reference_date = datetime.now()
    if args.reference_date is not None:
        reference_date = datetime.strptime(args.reference_date,"%Y-%m-%d")

    # Parse the crontab
    schedule = parse_crontab(crontab_content)

    # Generate time intervals
    intervals = generate_intervals(interval, scope, reference_date=reference_date)

    # Collect jobs in intervals
    job_intervals = collect_jobs(schedule=schedule, intervals=intervals)

    # Plot the intervals
    plot_job_intervals(job_intervals, title=f"Jobs per {interval}-Minute Interval ({scope})")

    # Print job intervals
    for interval_label, jobs in job_intervals:
        print(f"{interval_label}: {len(jobs)} jobs")
