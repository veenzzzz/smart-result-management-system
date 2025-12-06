import os
import sys
from datetime import datetime

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"*** {title.center(44)} ***")
    print("=" * 50)

def print_separator():
    """Print a separator line"""
    print("-" * 50)

def get_input(prompt, input_type=str, allow_empty=False):
    """Get validated input from user"""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            
            if not value and not allow_empty:
                print("ERROR: Input cannot be empty. Please try again.")
                continue
            
            if not value and allow_empty:
                return None
            
            if input_type == int:
                return int(value)
            elif input_type == float:
                return float(value)
            else:
                return value
                
        except ValueError:
            print(f"ERROR: Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\n\nWARNING: Operation cancelled by user.")
            return None

def confirm_action(message):
    """Ask for confirmation"""
    while True:
        response = input(f"{message} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("ERROR: Please enter 'y' or 'n'.")

def pause():
    """Pause and wait for user input"""
    input("\nPress Enter to continue...")

def format_date(date_str):
    """Format date string"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d-%m-%Y")
    except:
        return date_str

def get_current_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")