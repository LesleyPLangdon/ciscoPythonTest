# ─────────────────────────────────────────────────────────────────────────────
# Day 1 Exercise: Your First Python Script
# Python for Network Automation
# ─────────────────────────────────────────────────────────────────────────────
#
# PART 1 - Hello World (do this with the class)
# ──────────────────────────────────────────────
# Type this line and run your script with: python day1_exercise.py

print("Hello, network world!")

# PART 2 - Variables (do this with the class)
# ────────────────────────────────────────────
# Variables store information. In networking you work with data like this
# all the time - device names, IPs, port counts.

device_name = "Router-1"
ip_address = "192.168.1.1"
interfaces = 24

# f-strings let you drop variables into text using curly braces { }
print(f"{device_name} is at {ip_address} and has {interfaces} ports")


# ─────────────────────────────────────────────────────────────────────────────
# PART 3 - Your turn! (pair activity)
# ─────────────────────────────────────────────────────────────────────────────
#
# Create variables for an imaginary network device YOU manage.
# Include: device name, IP address, location, number of interfaces.
# Then print a summary line using an f-string.
#
# Example output:
#   Device: Core-SW-1 | IP: 10.0.0.1 | Location: Server Room B | Ports: 48
#
# Delete the 'pass' below and write your code here:

# your device variables go here


# your print statement goes here


# ─────────────────────────────────────────────────────────────────────────────
# STRETCH - if you finish early
# ─────────────────────────────────────────────────────────────────────────────
#
# 1. Add a second device and print both.
# 2. Add a variable for uptime in days and include it in your output.
# 3. What does the type() function do? Try: print(type(ip_address))
#    Try it on each of your variables. What do you notice?
