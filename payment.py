#!/usr/bin/env python3
"""
🎓 Trainer Claims Calculator (Kenya Shillings)
Auto-calculates trainer pay based on student fees and collection rates.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict
from decimal import Decimal, ROUND_HALF_UP

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
CONFIG = {
    'HOURLY_RATE': 300,              # KSh per hour
    'CURRENCY': 'KSh',
    'DATA_FILE': 'trainer_calc_data.json',
    'LOCALE': 'en_KE'
}

# ═══════════════════════════════════════════════════════════════
# COLORS FOR TERMINAL OUTPUT
# ═══════════════════════════════════════════════════════════════
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_currency(amount: float) -> str:
    """Format amount as Kenyan Shillings with commas"""
    abs_amount = abs(amount)
    if abs_amount % 1 == 0:
        formatted = f"{abs_amount:,.0f}"
    else:
        formatted = f"{abs_amount:,.2f}"
    return f"{CONFIG['CURRENCY']} {formatted}"

def format_number(num: float) -> str:
    """Format number with commas"""
    return f"{num:,.2f}"

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().strftime("%H:%M:%S")

def print_separator(char: str = "═", length: int = 65):
    """Print a separator line"""
    print(f"{Colors.CYAN}{char * length}{Colors.RESET}")

def print_header():
    """Print calculator header"""
    clear_screen()
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}╔═══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}║{Colors.RESET}       {Colors.BOLD}🎓 TRAINER CLAIMS CALCULATOR{Colors.RESET} {Colors.YELLOW}(KES){Colors.RESET}              {Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}╚═══════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()

def print_status(message: str, status_type: str = "info"):
    """Print status message with color"""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED
    }
    icon = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✗"}
    print(f"{colors.get(status_type, Colors.RESET)}{icon.get(status_type, 'ℹ')} {message}{Colors.RESET}")

# ═══════════════════════════════════════════════════════════════
# DATA PERSISTENCE
# ═══════════════════════════════════════════════════════════════
def save_data(data: Dict) -> bool:
    """Save calculation data to JSON file"""
    try:
        data['saved_at'] = datetime.now().isoformat()
        with open(CONFIG['DATA_FILE'], 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print_status(f"Failed to save data: {e}", "error")
        return False

def load_data() -> Optional[Dict]:
    """Load calculation data from JSON file"""
    try:
        if os.path.exists(CONFIG['DATA_FILE']):
            with open(CONFIG['DATA_FILE'], 'r') as f:
                data = json.load(f)
                return data
    except Exception as e:
        print_status(f"Failed to load data: {e}", "error")
    return None

def delete_data() -> bool:
    """Delete saved data file"""
    try:
        if os.path.exists(CONFIG['DATA_FILE']):
            os.remove(CONFIG['DATA_FILE'])
            return True
    except Exception as e:
        print_status(f"Failed to delete data: {e}", "error")
    return False

# ═══════════════════════════════════════════════════════════════
# CALCULATION ENGINE
# ═══════════════════════════════════════════════════════════════
def calculate(students: int, fee_billed: float, balance: float, hours: float) -> Dict:
    """
    Perform all calculations and return results dictionary
    """
    # Ensure non-negative values
    students = max(0, int(students))
    fee_billed = max(0, float(fee_billed))
    balance = max(0, float(balance))
    hours = max(0, float(hours))
    
    # Core calculations
    total_fee_billed = students * fee_billed
    balance_warning = False
    
    # Warn if balance exceeds total billed
    if balance > total_fee_billed and total_fee_billed > 0:
        balance = total_fee_billed
        balance_warning = True
    
    total_paid_fees = max(0, total_fee_billed - balance)
    factor = total_paid_fees / total_fee_billed if total_fee_billed > 0 else 0
    gross_salary = hours * CONFIG['HOURLY_RATE']
    final_pay = factor * gross_salary
    
    return {
        'inputs': {
            'students': students,
            'fee_billed': fee_billed,
            'balance': balance,
            'hours': hours,
            'balance_warning': balance_warning
        },
        'results': {
            'total_fee_billed': total_fee_billed,
            'total_paid_fees': total_paid_fees,
            'collection_factor': factor,
            'collection_percentage': factor * 100,
            'gross_salary': gross_salary,
            'final_pay': final_pay
        },
        'calculated_at': get_timestamp()
    }

# ═══════════════════════════════════════════════════════════════
# USER INPUT HANDLING
# ═══════════════════════════════════════════════════════════════
def get_numeric_input(prompt: str, min_val: float = 0, step: float = 1, 
                      allow_empty: bool = False, currency: bool = False) -> Optional[float]:
    """
    Get numeric input from user with validation
    Returns None if allow_empty and user enters nothing
    """
    prefix = f"{CONFIG['CURRENCY']} " if currency else ""
    
    while True:
        try:
            user_input = input(f"{prompt} {prefix}").strip()
            
            # Allow empty input if specified
            if allow_empty and user_input == '':
                return None
            
            # Handle empty input
            if user_input == '':
                return 0
            
            # Remove currency symbols and commas
            cleaned = user_input.replace(CONFIG['CURRENCY'], '').replace(',', '').replace('KSh', '').strip()
            
            value = float(cleaned)
            
            # Validate minimum
            if value < min_val:
                print_status(f"Value must be at least {min_val}", "warning")
                continue
            
            # Round to step
            if step and step < 1:
                value = round(value / step) * step
            
            return value
            
        except ValueError:
            print_status("Please enter a valid number", "error")
        except KeyboardInterrupt:
            print("\n")
            print_status("Operation cancelled", "warning")
            return None

def display_results(calc_data: Dict):
    """Display calculation results in formatted table"""
    inputs = calc_data['inputs']
    results = calc_data['results']
    
    print()
    print_separator("─")
    print(f"{Colors.BOLD}📊 CALCULATION RESULTS{Colors.RESET} {Colors.CYAN}({calc_data['calculated_at']}){Colors.RESET}")
    print_separator("─")
    
    # Input Summary
    print(f"\n{Colors.UNDERLINE}Input Summary:{Colors.RESET}")
    print(f"  • Students:        {inputs['students']:,}")
    print(f"  • Fee per Student: {format_currency(inputs['fee_billed'])}")
    print(f"  • Unpaid Balance:  {format_currency(inputs['balance'])}")
    print(f"  • Claimed Hours:   {inputs['hours']:.1f}")
    
    if inputs['balance_warning']:
        print(f"\n  {Colors.YELLOW}⚠ WARNING: Balance was capped at total billed amount{Colors.RESET}")
    
    # Results
    print(f"\n{Colors.UNDERLINE}Financial Breakdown:{Colors.RESET}")
    print(f"  ┌─────────────────────────────────────────────────┐")
    print(f"  │ Total Fee Billed:    {format_currency(results['total_fee_billed']):>25} │")
    print(f"  │ Total Paid Fees:     {format_currency(results['total_paid_fees']):>25} │")
    print(f"  │ Collection Rate:     {results['collection_percentage']:>24.1f}% │")
    print(f"  │ Gross Salary:        {format_currency(results['gross_salary']):>25} │")
    print(f"  └─────────────────────────────────────────────────┘")
    
    # Final Pay (Highlighted)
    print()
    print(f"  {Colors.BOLD}{Colors.GREEN}╔═══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.GREEN}║{Colors.RESET}     {Colors.BOLD}🎯 FINAL TRAINER PAY:{Colors.RESET}  {Colors.BOLD}{Colors.GREEN}{format_currency(results['final_pay']):>25}{Colors.RESET} {Colors.GREEN}║{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.GREEN}╚═══════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()

def display_help():
    """Display help information"""
    print()
    print_separator("─")
    print(f"{Colors.BOLD}📖 HELP & COMMANDS{Colors.RESET}")
    print_separator("─")
    print(f"""
  {Colors.CYAN}INPUT TIPS:{Colors.RESET}
  • Press {Colors.YELLOW}Enter{Colors.RESET} to submit a value
  • Press {Colors.YELLOW}Ctrl+C{Colors.RESET} to cancel current input
  • Enter {Colors.YELLOW}'q'{Colors.RESET} or {Colors.YELLOW}'quit'{Colors.RESET} to exit anytime
  • Enter {Colors.YELLOW}'r'{RESET} or {Colors.YELLOW}'reset'{Colors.RESET} to clear all fields
  • Enter {Colors.YELLOW}'d'{Colors.RESET} or {Colors.YELLOW}'demo'{Colors.RESET} to load demo data
  • Enter {Colors.YELLOW}'s'{Colors.RESET} or {Colors.YELLOW}'save'{Colors.RESET} to save current data
  • Enter {Colors.YELLOW}'l'{Colors.RESET} or {Colors.YELLOW}'load'{Colors.RESET} to load saved data
  
  {Colors.CYAN}CALCULATION LOGIC:{Colors.RESET}
  • Trainer pay is proportional to fees collected
  • Higher collection rate = Higher payout
  • Balance cannot exceed total billed amount
  
  {Colors.CYAN}CONFIGURATION:{Colors.RESET}
  • Hourly Rate: {format_currency(CONFIG['HOURLY_RATE'])}
  • Currency: {CONFIG['CURRENCY']}
  • Data File: {CONFIG['DATA_FILE']}
""")
    print_separator("─")

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class TrainerCalculator:
    def __init__(self):
        self.data = {
            'students': 0,
            'fee_billed': 0,
            'balance': 0,
            'hours': 0
        }
        self.running = True
    
    def auto_calculate(self):
        """Auto-calculate when any field has value"""
        if any([self.data['students'], self.data['fee_billed'], self.data['hours']]):
            results = calculate(
                self.data['students'],
                self.data['fee_billed'],
                self.data['balance'],
                self.data['hours']
            )
            display_results(results)
            save_data(self.data)
    
    def get_input_with_label(self, field: str, label: str, help_text: str, 
                            currency: bool = False, step: float = 1) -> bool:
        """Get input for a field, return False if user wants to quit"""
        print(f"\n{Colors.BOLD}{label}{Colors.RESET}")
        print(f"  {Colors.CYAN}{help_text}{Colors.RESET}")
        
        value = get_numeric_input(
            f"  Enter {label.split(':')[0].lower()}",
            min_val=0,
            step=step,
            allow_empty=True,
            currency=currency
        )
        
        # Check for special commands
        if value is None:
            return False
        
        self.data[field] = value
        return True
    
    def load_demo_data(self):
        """Load realistic demo data for Kenya"""
        demo = {
            'students': 30,
            'fee_billed': 15000,
            'balance': 45000,
            'hours': 40
        }
        self.data.update(demo)
        print_status("Demo data loaded", "success")
        self.auto_calculate()
    
    def reset_data(self):
        """Reset all data to zero"""
        self.data = {
            'students': 0,
            'fee_billed': 0,
            'balance': 0,
            'hours': 0
        }
        delete_data()
        print_status("All data reset", "success")
    
    def run(self):
        """Main application loop"""
        print_header()
        print_status("Welcome to Trainer Claims Calculator", "success")
        
        # Try to load saved data
        saved = load_data()
        if saved:
            print_status(f"Data loaded from {saved.get('saved_at', 'previous session')}", "info")
            self.data.update({k: saved.get(k, 0) for k in self.data.keys()})
            self.auto_calculate()
        
        print()
        print(f"{Colors.YELLOW}💡 Tip: Enter 'help' for commands, 'demo' for sample data{Colors.RESET}")
        print()
        
        while self.running:
            try:
                # Field 1: Students
                if not self.get_input_with_label(
                    'students', 
                    "👥 NUMBER OF STUDENTS", 
                    "Total enrolled students in the training batch",
                    currency=False,
                    step=1
                ):
                    break
                self.auto_calculate()
                
                # Field 2: Fee Billed
                if not self.get_input_with_label(
                    'fee_billed', 
                    "💰 FEE BILLED PER STUDENT", 
                    "Amount charged to each student (Kenya Shillings)",
                    currency=True,
                    step=1
                ):
                    break
                self.auto_calculate()
                
                # Field 3: Balance
                if not self.get_input_with_label(
                    'balance', 
                    "⏳ CUMULATIVE BALANCE (UNPAID)", 
                    "Total outstanding amount from all students",
                    currency=True,
                    step=1
                ):
                    break
                self.auto_calculate()
                
                # Field 4: Hours
                if not self.get_input_with_label(
                    'hours', 
                    "⏱️ TRAINER CLAIMED HOURS", 
                    "Total teaching hours claimed by trainer",
                    currency=False,
                    step=0.5
                ):
                    break
                self.auto_calculate()
                
                # Loop complete - ask if user wants to continue
                print()
                print_separator("─")
                continue_choice = input(f"\n{Colors.BOLD}Calculate another? (y/n/s/r/d/h): {Colors.RESET}").strip().lower()
                
                if continue_choice in ['y', 'yes', '']:
                    self.reset_data()
                    print_header()
                    continue
                elif continue_choice in ['s', 'save']:
                    save_data(self.data)
                    print_status("Data saved successfully", "success")
                elif continue_choice in ['r', 'reset']:
                    self.reset_data()
                    print_header()
                    continue
                elif continue_choice in ['d', 'demo']:
                    self.load_demo_data()
                elif continue_choice in ['h', 'help']:
                    display_help()
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
                    print_header()
                    continue
                else:
                    break
                    
            except KeyboardInterrupt:
                print("\n")
                print_status("Calculation interrupted", "warning")
                break
        
        # Exit
        print()
        print_separator("═")
        print(f"{Colors.GREEN}✓ Thank you for using Trainer Claims Calculator!{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Data auto-saved to: {CONFIG['DATA_FILE']}{Colors.RESET}")
        print_separator("═")
        print()

# ═══════════════════════════════════════════════════════════════
# QUICK CALCULATE MODE (Non-Interactive)
# ═══════════════════════════════════════════════════════════════
def quick_calculate(students: int, fee_billed: float, balance: float, hours: float):
    """One-line calculation without interactive prompts"""
    results = calculate(students, fee_billed, balance, hours)
    display_results(results)
    return results

# ═══════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════
def main():
    import sys
    
    # Check for command-line arguments (quick mode)
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print(f"""
{Colors.BOLD}🎓 TRAINER CLAIMS CALCULATOR{Colors.RESET}

{Colors.UNDERLINE}USAGE:{Colors.RESET}
  python trainer_calculator.py                    # Interactive mode
  python trainer_calculator.py 30 15000 45000 40  # Quick mode
  python trainer_calculator.py --help             # Show this help

{Colors.UNDERLINE}QUICK MODE ARGUMENTS:{Colors.RESET}
  1. Number of students (integer)
  2. Fee per student (KSh)
  3. Unpaid balance (KSh)
  4. Claimed hours (float)

{Colors.UNDERLINE}EXAMPLE:{Colors.RESET}
  python trainer_calculator.py 30 15000 45000 40
  
{Colors.UNDERLINE}CONFIGURATION:{Colors.RESET}
  Edit CONFIG dictionary in script to change:
  • HOURLY_RATE (default: 300 KSh/hour)
  • DATA_FILE (default: trainer_calc_data.json)
""")
            return
        elif len(sys.argv) == 5:
            try:
                students = int(sys.argv[1])
                fee_billed = float(sys.argv[2])
                balance = float(sys.argv[3])
                hours = float(sys.argv[4])
                print_header()
                quick_calculate(students, fee_billed, balance, hours)
                return
            except ValueError as e:
                print_status(f"Invalid arguments: {e}", "error")
                print("Use --help for usage information")
                return
    
    # Interactive mode
    calculator = TrainerCalculator()
    calculator.run()

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Colors.RED}✗ Unexpected error: {e}{Colors.RESET}\n")
        exit(1)