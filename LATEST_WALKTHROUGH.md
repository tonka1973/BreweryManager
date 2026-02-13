# Verification Walkthrough - Current Orders Filter

## Changes Verified
- **Renamed Section**: "Recent Order Status" -> "Current Orders"
- **Updated Columns**: 
    - Invoice Number (Left Aligned, shows "Not Invoiced" if empty)
    - **Double-Click Order**: Double-clicking an order in the "Sales / Invoicing" list (or "Current Orders") opens the **Order Details** view.
    - From this view, you can:
        - **Create Invoice**: Instantly converts the order to an invoice.
        - **Make Payment**: (New) Record payment directly if the order is invoiced.
        - **Edit Order**: Opens the **Edit Order** dialog (New).
            - View all items in the order.
            - **Add Items**: Add more products to the existing order (or invoice).
            - **Remove Items**: Remove products from the order.
            - **Save**: Automatically updates stock and recalculates invoice totals.
- **Sales / Invoicing Module**: Merged the "Invoicing" tab into "Sales". You can now manage everything from one place.
    - **Toolbar**: Added a "Payment" button to quickly record payments for selected orders.
    - **View**: Mirrors the "Current Orders" view, showing all active orders across all customers.
- **Invoice Creation**: The old right-click menu has been removed in favor of this clearer workflow.
- **Bug Fixes**:
    - Fixed "Empty List" issue by bypassing the complex selection dialog for direct invoicing.
    - Fixed crash when initializing the old invoice dialog.
    - Added "Ordered Date" and "Delivery Date" columns to the customer dashboard.
- **Bug Fix**: Fixed an issue where some orders were hidden from the invoice creation list due to database anomalies. Removed status restrictions so ALL uninvoiced orders are visible.
- **Current Orders Columns**: Split "Date" into "Ordered Date" and "Delivery Date".
- **Scrollbar**: Added to "Current Orders" table for better navigation.
- **Filtering Logic**: Orders that are **Delivered**, **Invoiced**, AND **Paid** are hidden.

## Manual Verification Steps

1.  **Launch Application**
    - Run `python main.py`

2.  **Open Customer Dashboard**
    - Navigate to **Customers** tab.
    - Double-click a customer (e.g., "The Red Lion").

3.  **Check Section Title**
    - Confirm the bottom section on the "Overview" tab is titled **"Current Orders"**.

4.  **Test Filtering Scenarios**
    - **Scenario A: New Order**
        - Create a new sale for this customer.
        - **Result**: Should appear in "Current Orders" (Status: Reserved).
    - **Scenario B: Delivered Order**
        - Mark the order as Delivered.
        - **Result**: Should still appear (Status: Delivered, Payment: Unpaid/Pending).
    - **Scenario C: Invoiced Order**
        - Create an invoice for the order.
        - **Result**: Should still appear (Status: Delivered, Payment: Unpaid).
    - **Scenario D: Paid Order (The Filter Test)**
        - Mark the invoice as **Paid**.
        - Refresh the customer view (close and reopen or switch tabs).
        - **Result**: The order should **DISAPPEAR** from the "Current Orders" list.

5.  **Performance Check**
    - Ensure the customer dashboard opens quickly even with many historical orders (due to the new optimization).

## Recipe Costing & Product Pricing
We have implemented a comprehensive system for tracking production costs and setting retail prices.

### Key Changes
- **Database Schema**: Added `labor_cost`, `energy_cost`, `misc_cost` to `recipes` table and `retail_price`, `cost_price` to `products` table.
- **Recipe Costing**:
    - Updates to `RecipeDialog` to allow input of fixed costs (Labor, Energy, Misc).
    - Added "Calculate Cost" button that sums fixed costs and ingredient costs (pulled from Inventory).
    - Displays "Total Batch Cost" and "Cost Per Litre".
- **Product Pricing**:
    - Updates to `AddProductDialog` to include `Retail Price` and `Cost Price`.
    - These fields are saved to the database.
- **Sales Integration**:
    - `SaleDialog` now automatically populates the "Unit Price" field with the product's `Retail Price` when selected.

### Verification
1.  **Check Costing**:
    - Open a Recipe.
    - Enter Labor/Energy costs.
    - Click "Calculate Cost".
    - Save and Re-open to ensure values persist.
2.  **Check Pricing**:
    - Add a new Product.
    - Enter a Retail Price (e.g., 65.00).
    - Save.
3.  **Check Sales**:
    - Open "New Sale".
    - Select the new product.
    - Verify "Unit Price" automatically sets to 65.00.

## Order Logic & Grouping
We have updated the "Sales" and "Current Orders" lists to group multiple items into single "Order" rows.

### Key Changes
- **Grouped View**: Instead of listing every individual item line, the system now groups items by **Customer + Date** (or **Invoice ID**).
- **Edit Order**: Double-clicking a grouped row opens the **Edit Order** dialog showing ALL items in that order.
- **Adding Items**: When you add an item to an existing order, it is now correctly grouped with the original order in the list view.

### Verification
1.  **Open an Order**: Double-click an existing order.
2.  **Add Item**: Add a new product (e.g., "Pale Ale").
3.  **Save**: Click Save.
5.  **Verify Order Details**: Double-click an order from the Customer Dashboard. Confirm that the "Order Details" popup lists **ALL** items in that order, not just one.
