# Weekend starts at Saturday 00:00

days_map = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
}

# One-line input like: "saturday 23:59"
s = input("Enter day and time (e.g., 'friday 18:30'): ").strip().lower()

# Parse day and time (fallback to asking time if only day is given)
if " " in s:
    day_str, time_str = s.split(maxsplit=1)
    day_str = day_str.lower()   # 👈 important
else:
    day_str = s.lower()
    time_str = input("Enter the time in 24-hr format (HH:MM): ").strip()


# Validate day
if day_str not in days_map:
    print("Invalid day.")
    raise SystemExit

# Validate time
try:
    h, m = map(int, time_str.split(":"))
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError
except ValueError:
    print("Invalid time. Use HH:MM in 24-hour format.")
    raise SystemExit

# Minutes since start of (arbitrary) week
curr_min = days_map[day_str] * 24 * 60 + h * 60 + m
weekend_start = 5 * 24 * 60  # Saturday 00:00

if curr_min < weekend_start:
    delta = weekend_start - curr_min
    hours, minutes = divmod(delta, 60)
    print(f"Weekend begins in {hours} hours and {minutes} minutes.")
elif curr_min == weekend_start:
    print("Weekend begins now!")
else:
    delta = curr_min - weekend_start
    hours, minutes = divmod(delta, 60)
    print(f"It's the weekend since {hours} hours and {minutes} minutes.")
