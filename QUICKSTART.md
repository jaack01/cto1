# Quick Start Guide

Get up and running with the Order Management System in 5 minutes!

## Installation

1. **Check Python version** (requires Python 3.7+):
   ```bash
   python3 --version
   ```

2. **Run the application**:
   ```bash
   python3 app.py
   ```

That's it! The application will create the database automatically on first run.

## First Steps

### 1. Create Your First Order

1. Click **"New Order"** button
2. Fill in:
   - Customer Name: `John Doe`
   - Customer Email: `john@example.com`
   - Customer Phone: `+1234567890` (optional)
   - Item Description: `Custom Widget`
   - Quantity: `2`
   - Price per Item: `49.99`
3. Click **"Save"**

### 2. Mark Order as Ready

1. Select the order you just created
2. Click **"Mark Ready"**
3. Confirm the action
4. Note: Email/SMS notifications require configuration (see below)

### 3. Configure Email Notifications (Optional)

1. Go to **File > Settings**
2. Enter your SMTP details:
   - **Gmail users**:
     - Server: `smtp.gmail.com`
     - Port: `587`
     - Username: Your Gmail address
     - Password: App-specific password ([How to create](https://support.google.com/accounts/answer/185833))
   - **Other providers**: Use your provider's SMTP settings
3. Click **"Save"**

Now when you mark orders as ready, customers will receive email notifications!

## Common Tasks

### View Orders by Status
Use the **Filter** dropdown:
- Select "pending" to see pending orders
- Select "ready" to see ready orders
- Select "completed" to see completed orders

### Edit an Order
- **Double-click** the order in the list, OR
- Select it and click **"Edit Order"**

### Complete an Order
1. Select a ready order
2. Click **"Mark Completed"**

### Delete an Order
1. Select the order
2. Click **"Delete Order"**
3. Confirm the deletion

## Tips

- 📊 **Statistics** are shown in the top-right corner
- 🎨 **Color coding**: Pending (orange), Ready (green), Completed (blue)
- ⌨️ **F5** refreshes the order list
- 📧 **Email notifications** are sent when marking orders as ready
- 💾 **Auto-save**: All changes are saved immediately to the database

## Need Help?

- Click **Help > Help** in the application menu
- Check the [full README](README.md) for detailed documentation
- Review [troubleshooting tips](README.md#troubleshooting)

## Next Steps

1. Configure email notifications for customer alerts
2. Explore the statistics dashboard
3. Try filtering orders by status
4. Customize the settings to fit your workflow

Happy order managing! 🎉
