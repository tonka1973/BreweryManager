# Implementation Plan - Recipe Costing & Product Pricing

## Goal
Implement a system to calculate the cost of production (Recipe Cost) and set a base Retail Price for products, which allows for margin calculation and default pricing in Sales.

## User Review Required
> [!IMPORTANT]
> Cost calculations will depend on the `cost_per_unit` in Inventory being accurate and the Units matching (or satisfying basic conversion rules).

## Proposed Changes

### 1. Database Schema Updates
- **Table `recipes`**: Add `labor_cost`, `energy_cost`, `misc_cost` (all REAL, default 0.0).
- **Table `products`**: Add `cost_price` (REAL), `retail_price` (REAL).

### 2. [src/gui/recipes.py](file:///c:/Users/darre/Desktop/brewman/BreweryManager/src/gui/recipes.py)
- **`RecipeDialog`**:
    - Add fields for "Labor Cost", "Energy Cost", "Misc Cost".
    - Add a "Calculate Inventory Cost" button or real-time calculation.
    - Logic: Iterate ingredients -> Find Inventory Item -> Convert Units -> Multiply Cost.
    - Display "Total Estimated Cost" and "Cost Per Litre".
- **`RecipesModule`**:
    - Update schema on init.
    - Show `Cost/L` in treeview? (Optional, maybe just in details).

### 3. [src/gui/products.py](file:///c:/Users/darre/Desktop/brewman/BreweryManager/src/gui/products.py)
- **`AddProductDialog`**:
    - Add `Retail Price` field (Required).
    - Add `Cost Price` field (Auto-filled if linked to a Recipe/Gyle, otherwise manual).
- **`ProductsModule`**:
    - Update schema on init.
    - Show `Retail Price` in treeview.

### 4. [src/gui/sales_screen.py](file:///c:/Users/darre/Desktop/brewman/BreweryManager/src/gui/sales_screen.py)
- **`SaleDialog.on_product_selected`**:
    - Fetch and set `price_entry` using the product's `retail_price`.

## Verification Plan
### Automated Tests
- None (UI heavy).

### Manual Verification
1.  **Inventory**: Ensure some ingredients have costs.
2.  **Recipe**:
    - Create/Edit Recipe.
    - Add Labor/Energy costs.
    - Verify "Total Cost" sums correctly.
3.  **Product**:
    - Add Product.
    - Set Retail Price.
4.  **Sales**:
    - Create Sale.
    - Select Product.
    - Verify Price defaults to Retail Price.
