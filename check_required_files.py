import os
import sys

# Define required files
def check_required_files():

    required_files = [
        'README.md',
        '.gitignore'
    ]

    # Track missing Files
    missing_files = []

    # Check for each requireed File
    for file in required_files: 
        if not os.path.exists(file):
            missing_files.append(file)

    # Report results
    if missing_files:
        print("ERROR: THe folowind required firls are missing:")
        for file in missing_files:
            print(f" - {file}")
        return False

    # Pass if Files are present
    return True



if __name__ == "__main__":

    if check_required_files():
        sys.exit(0)

    else:

        sys.exit(1)

