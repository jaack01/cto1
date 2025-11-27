# Order Management System

A comprehensive desktop application for managing orders with customer notifications, built with Python and Tkinter.

## Features

- **Order Management**: Create, edit, delete, and track orders with customer information
- **Status Tracking**: Manage order lifecycle (Pending → Ready → Completed)
- **Email Notifications**: Automatic email notifications when orders are marked as ready (SMTP)
- **SMS Notifications**: SMS notification stubs for future integration with SMS gateways
- **Input Validation**: Comprehensive form validation for data integrity
- **Modern GUI**: Clean interface with ttk themes and intuitive navigation
- **Filtering & Search**: Filter orders by status for easy management
- **Statistics Dashboard**: Real-time statistics on orders and revenue
- **Database Persistence**: SQLite database for reliable data storage

## Screenshots

The application features:
- Main dashboard with order list and statistics
- Create/Edit order dialogs with validation
- Settings panel for configuring notifications
- Help and About dialogs
- Status-based color coding (Pending: Orange, Ready: Green, Completed: Blue)

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- SQLite3 (included with Python)

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd order-management-system
```

### 2. Install Dependencies

The application uses only Python standard library modules, so no additional packages are required for basic functionality.

For a clean installation:

```bash
python3 -m pip install --upgrade pip
```

### 3. Run the Application

```bash
python3 app.py
```

## Application Icon

A placeholder application icon is included at `assets/app.ico`. The Tkinter window
loads this file at runtime, and all PyInstaller builds embed it as the executable icon.
Replace this file with your own `.ico` before distributing the application, keeping the
same path so build scripts and GitHub Actions continue to work as expected.

## Configuration

### Email Notifications (SMTP)

To enable email notifications:

1. Open the application
2. Go to **File > Settings**
3. Configure SMTP settings:
   - **SMTP Server**: Your SMTP server (e.g., `smtp.gmail.com`)
   - **SMTP Port**: Port number (e.g., `587` for TLS)
   - **SMTP Username**: Your email address
   - **SMTP Password**: Your email password or app-specific password
   - **From Email**: The sender email address

#### Gmail Configuration Example:

For Gmail users, you'll need to:
1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password
3. Use these settings:
   - Server: `smtp.gmail.com`
   - Port: `587`
   - Username: Your Gmail address
   - Password: Your app-specific password

### SMS Notifications

SMS notifications are currently implemented as stubs. To integrate with an actual SMS service:

1. Choose an SMS gateway provider (e.g., Twilio, AWS SNS, Vonage)
2. Obtain API credentials
3. Enable SMS in **File > Settings**
4. Enter your API key
5. Modify `notifications.py` to integrate with your chosen provider

Example integration services:
- **Twilio**: Popular SMS API with good documentation
- **AWS SNS**: Amazon's notification service
- **Vonage (formerly Nexmo)**: SMS and voice API
- **MessageBird**: Global SMS platform

## Usage Guide

### Creating an Order

1. Click **"New Order"** button or use **File > New Order**
2. Fill in the required fields:
   - Customer Name (required)
   - Customer Email (required, validated)
   - Customer Phone (optional, validated if provided)
   - Item Description (required)
   - Quantity (required, must be positive integer)
   - Price per Item (required, must be non-negative)
3. Click **"Save"** to create the order

### Managing Orders

#### Editing an Order
- Select an order from the list
- Click **"Edit Order"** or double-click the order
- Modify the details and click **"Save"**

#### Marking Order as Ready
- Select a pending order
- Click **"Mark Ready"**
- Confirm the action
- Email and SMS notifications will be sent automatically (if configured)

#### Marking Order as Completed
- Select a ready order
- Click **"Mark Completed"**
- The order will be marked as completed

#### Deleting an Order
- Select an order
- Click **"Delete Order"**
- Confirm the deletion (this action cannot be undone)

### Filtering Orders

Use the **Filter** dropdown to view:
- **All**: All orders
- **Pending**: Orders awaiting fulfillment
- **Ready**: Orders ready for pickup
- **Completed**: Completed orders

### Keyboard Shortcuts

- **Double-click**: Edit selected order
- **F5**: Refresh order list

### Statistics

The top-right corner displays real-time statistics:
- Total number of orders
- Count by status (Pending, Ready, Completed)
- Total revenue

## Project Structure

```
order-management-system/
├── assets/
│   └── app.ico           # Placeholder application icon
├── .github/
│   └── workflows/
│       └── build.yml     # GitHub Actions workflow for builds
├── app.py                # Main application and GUI
├── app.spec              # PyInstaller build specification
├── build.bat             # Windows batch build script
├── build.ps1             # Windows PowerShell build script
├── build.sh              # Linux/macOS build script
├── database.py           # Database operations and models
├── validation.py         # Input validation utilities
├── notifications.py      # Email and SMS notification services
├── README.md             # This file
├── requirements.txt      # Python dependencies (if any)
└── .gitignore            # Git ignore file
```

## Module Documentation

### app.py
Main application file containing the GUI implementation using Tkinter and ttk. Includes:
- `OrderManagementApp`: Main application class
- Menu system and toolbar
- Order creation/editing dialogs
- Settings dialog for notifications
- Help and About dialogs

### database.py
Database layer using SQLite for data persistence. Includes:
- `Database`: Main database class with CRUD operations
- Order creation, retrieval, updating, and deletion
- Statistics calculation
- Context manager for safe database operations

### validation.py
Shared validation utilities used across all forms. Includes:
- Email validation (regex-based)
- Phone number validation (multiple formats)
- Required field validation
- Number validation (positive, non-negative)
- Order form validation
- Dialog message helpers (error, warning, info, success, confirm)

### notifications.py
Notification services for customer communication. Includes:
- `NotificationConfig`: Configuration class for notification settings
- `EmailNotificationService`: Email sending via SMTP
- `SMSNotificationService`: SMS stub implementation
- `NotificationManager`: Unified interface for all notifications

## Data Model

### Order Schema

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    item_description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    ready_at TEXT
)
```

### Order Status Flow

1. **Pending**: Initial state when order is created
2. **Ready**: Order is prepared and customer is notified
3. **Completed**: Order has been picked up/delivered

## Error Handling

The application includes comprehensive error handling:
- Input validation with user-friendly error messages
- Database error handling with rollback
- Notification failure logging
- Confirmation dialogs for destructive actions

## Security Considerations

⚠️ **Important Security Notes:**

1. **Email Credentials**: 
   - Credentials are stored in memory only (not persisted)
   - For production use, consider using environment variables or encrypted configuration files
   - Use app-specific passwords instead of main account passwords

2. **Database**:
   - The SQLite database file is stored locally
   - No encryption is applied by default
   - Consider encrypting sensitive data for production use

3. **Input Validation**:
   - All user inputs are validated before database operations
   - SQL injection protection via parameterized queries
   - Email and phone format validation

## Troubleshooting

### Email Notifications Not Working

1. **Check SMTP credentials**: Verify server, port, username, and password
2. **App-specific passwords**: Gmail and some providers require app-specific passwords
3. **Firewall**: Ensure port 587 (or your SMTP port) is not blocked
4. **Check logs**: The application logs notification attempts
5. **Test with a simple email client**: Verify credentials work outside the app

### Database Errors

1. **File permissions**: Ensure write permissions in the application directory
2. **Corrupted database**: Delete `orders.db` to create a fresh database (data will be lost)
3. **Locked database**: Close other instances of the application

### GUI Issues

1. **Theme problems**: The app automatically selects available themes
2. **Display scaling**: Adjust your OS display settings if text appears too small/large
3. **Tkinter not installed**: Install tkinter for your Python distribution

## Building Standalone Executables

The application includes PyInstaller configuration to build standalone executables.

### Prerequisites

```bash
pip install pyinstaller
```

### Building on Windows

Run one of the following:

```cmd
build.bat
```

Or with PowerShell:

```powershell
.\build.ps1
```

### Building on Linux/macOS

```bash
chmod +x build.sh
./build.sh
```

### Customizing the Icon

The application uses `assets/app.ico` as its icon:
- Replace the placeholder icon with your own before building
- The icon file must be in `.ico` format for Windows executables
- Linux and macOS builds also embed the icon
- Keep the file path as `assets/app.ico` to avoid changing build configs

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that:
- Builds executables for Windows, Linux, and macOS on every push
- Creates release artifacts when you push a version tag (e.g., `v1.0.0`)
- Uses the same icon configuration for all platforms

To create a release with executables:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Development

### Running Tests

#### Python backend

The legacy Tkinter application does not yet include automated Python tests. To add coverage:

```bash
# Install pytest
pip install pytest

# Create test files
# tests/test_validation.py
# tests/test_database.py
# tests/test_notifications.py

# Run tests
pytest tests/
```

#### React/Zustand dashboard sample

A lightweight React testing harness is included for the web dashboard and Zustand store that back the Tauri shell. It uses Vitest with React Testing Library and runs entirely in a JSDOM environment.

```bash
# Install Node dependencies (first run only)
npm install

# Execute the component and store tests in CI-friendly mode
npm test
```

The sample suite demonstrates:
- Rendering dashboard statistics from mocked order data
- Validating and submitting the order form via the Zustand store
- Exercising store actions with mocked fetch/create implementations

### Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Future Enhancements

Potential improvements:
- Export orders to CSV/PDF
- Advanced search and filtering
- Multi-user support with authentication
- Order history and audit log
- Barcode/QR code generation for orders
- Integration with payment gateways
- Dashboard with charts and analytics
- Mobile app integration via REST API
- Print receipts/invoices

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or suggestions:
1. Check the **Help** menu in the application
2. Review this README thoroughly
3. Check application logs for error messages
4. Open an issue in the repository

## Changelog

### Version 1.0.0 (Initial Release)
- Order creation, editing, and deletion
- Status management (Pending, Ready, Completed)
- Email notifications via SMTP
- SMS notification stubs
- Input validation across all forms
- Modern GUI with ttk themes
- Statistics dashboard
- SQLite database persistence
- Help and About dialogs
- Comprehensive documentation

---

**Built with ❤️ using Python and Tkinter**
