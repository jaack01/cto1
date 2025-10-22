"""
Validation utility functions for input validation across forms.
"""
import re

try:
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    messagebox = None


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not email.strip():
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_phone(phone):
    """
    Validate phone number format (accepts various formats).
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone or not phone.strip():
        return False
    
    phone_clean = re.sub(r'[\s\-\(\)\.]', '', phone)
    pattern = r'^\+?[1-9]\d{9,14}$'
    return re.match(pattern, phone_clean) is not None


def validate_required(value, field_name="Field"):
    """
    Validate that a required field is not empty.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not value or not str(value).strip():
        show_error(f"{field_name} is required")
        return False
    return True


def validate_positive_number(value, field_name="Field"):
    """
    Validate that a value is a positive number.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num = float(value)
        if num <= 0:
            show_error(f"{field_name} must be a positive number")
            return False
        return True
    except (ValueError, TypeError):
        show_error(f"{field_name} must be a valid number")
        return False


def validate_non_negative_number(value, field_name="Field"):
    """
    Validate that a value is a non-negative number.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num = float(value)
        if num < 0:
            show_error(f"{field_name} must be a non-negative number")
            return False
        return True
    except (ValueError, TypeError):
        show_error(f"{field_name} must be a valid number")
        return False


def validate_order_form(customer_name, customer_email, customer_phone, item_description, quantity, price):
    """
    Validate order form inputs.
    
    Args:
        customer_name: Customer name
        customer_email: Customer email
        customer_phone: Customer phone
        item_description: Item description
        quantity: Order quantity
        price: Item price
        
    Returns:
        bool: True if all validations pass, False otherwise
    """
    if not validate_required(customer_name, "Customer name"):
        return False
    
    if not validate_required(customer_email, "Customer email"):
        return False
    
    if not validate_email(customer_email):
        show_error("Invalid email address format")
        return False
    
    if customer_phone and not validate_phone(customer_phone):
        show_error("Invalid phone number format")
        return False
    
    if not validate_required(item_description, "Item description"):
        return False
    
    if not validate_required(quantity, "Quantity"):
        return False
    
    if not validate_positive_number(quantity, "Quantity"):
        return False
    
    try:
        qty = int(quantity)
        if qty != float(quantity):
            show_error("Quantity must be a whole number")
            return False
    except ValueError:
        show_error("Quantity must be a whole number")
        return False
    
    if not validate_required(price, "Price"):
        return False
    
    if not validate_non_negative_number(price, "Price"):
        return False
    
    return True


def show_error(message, title="Validation Error"):
    """
    Display an error dialog.
    
    Args:
        message: Error message to display
        title: Dialog title (default: "Validation Error")
    """
    if TKINTER_AVAILABLE and messagebox:
        messagebox.showerror(title, message)
    else:
        print(f"{title}: {message}")


def show_warning(message, title="Warning"):
    """
    Display a warning dialog.
    
    Args:
        message: Warning message to display
        title: Dialog title (default: "Warning")
    """
    if TKINTER_AVAILABLE and messagebox:
        messagebox.showwarning(title, message)
    else:
        print(f"{title}: {message}")


def show_info(message, title="Information"):
    """
    Display an information dialog.
    
    Args:
        message: Information message to display
        title: Dialog title (default: "Information")
    """
    if TKINTER_AVAILABLE and messagebox:
        messagebox.showinfo(title, message)
    else:
        print(f"{title}: {message}")


def show_success(message, title="Success"):
    """
    Display a success dialog.
    
    Args:
        message: Success message to display
        title: Dialog title (default: "Success")
    """
    if TKINTER_AVAILABLE and messagebox:
        messagebox.showinfo(title, message)
    else:
        print(f"{title}: {message}")


def confirm_action(message, title="Confirm"):
    """
    Display a confirmation dialog.
    
    Args:
        message: Confirmation message to display
        title: Dialog title (default: "Confirm")
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    if TKINTER_AVAILABLE and messagebox:
        return messagebox.askyesno(title, message)
    else:
        print(f"{title}: {message} (auto-confirmed)")
        return True
