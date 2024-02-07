"""
Helper for the update script to update the '==' to '>=' to force pip to update
"""

if __name__ == '__main__':
    # Read the file
    with open('update.txt', 'r') as f:
        lines = f.readlines()

    # Change the lines
    for li, line in enumerate(lines):
        lines[li] = line.replace('==', '>=')

    # Write the update lines to file
    with open('update.txt', 'w') as f:
        f.writelines(lines)
