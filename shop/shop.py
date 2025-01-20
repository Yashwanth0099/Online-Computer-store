import traceback
from flask import Blueprint, request, flash, render_template, redirect, url_for,session
from werkzeug.datastructures import MultiDict
from sql.db import DB
from flask_login import login_required, current_user
from auth.models import User
shop = Blueprint('shop', __name__, url_prefix='/',template_folder='templates')

@shop.route("/shop", methods=["GET","POST"])
def shop_list():
    name = request.args.get("name")
    category = request.args.get("category")
    order = request.args.get("order")
    limit = request.args.get("limit", 10)
    args=[]
    query = "SELECT pid, ptype, pname, pprice, description, pquantity, image FROM Product WHERE pquantity > 0"
    if name:
        query += " AND pname like %s"
        args.append(f"%{name}%")
    if category:
        query += " AND ptype = %s"
        args.append(f"{category}")
    if order in ["asc", "desc"]:
        query += f" ORDER BY unit_price {order}"
    if limit and int(limit) > 0 and int(limit) <= 100:
        query += " LIMIT %s"
        args.append(int(limit))
    rows = []

    offer_prices = {}
    customer_status = None  # Initialize customer_status

    try:
        # Fetch customer status
        customer_status_result = DB.selectAll("SELECT cid, status FROM Customer WHERE cid=%s", current_user.get_id())
        if customer_status_result.status and customer_status_result.rows:
            customer_status = customer_status_result.rows[0]["status"]

        print(customer_status) 

    except Exception as e:
        print("Error fetching customer status", e)
        flash("Error fetching customer status, please try again!", "danger")

    try:
        offer_result = DB.selectAll("SELECT pid, OfferPrice FROM offer_product")
        if offer_result.status and offer_result.rows:
            offer_prices = {row["pid"]: row["OfferPrice"] for row in offer_result.rows}
    except Exception as e:
        print("Error fetching offer prices", e)
        flash("Error fetching offer prices, please try again!", "danger")
    

    try:
        print(query)
        print(args)
        result = DB.selectAll(query, *args)
        if result.status:
            rows = result.rows
    except Exception as e:
        print("Error fetching items", e)
        flash("There was a problem loading items, please try again!", "danger")
    
    return render_template("shop.html", rows=rows, offer_prices=offer_prices, customer_status=customer_status)

# Deliverable 5: Product Details Page

@shop.route("/productdetail", methods=["GET", "POST"])
def productdetail():
    product_id = request.args.get("pid")
    print("pid", product_id)
    row = {}
    try:
        # Retrieve common product details
        product_result = DB.selectOne("""
            SELECT pid, ptype, pname, pprice, description, pquantity, image 
            FROM PRODUCT 
            WHERE pid = %s
        """, product_id)

        if product_result:
            row = product_result.row
            product_type = row.get('ptype')
            
            # Fetch additional details based on product type
            if product_type == 'Computer':
                category_result = DB.selectOne("""
                    SELECT CPUType 
                    FROM COMPUTER 
                    WHERE pid = %s
                """, product_id)
                if category_result:
                    category_row = category_result.row
                    cpu_type = category_row.get('CPUType')
                    row.update(category_row)
                    
            elif product_type == 'Laptop':
                category_result = DB.selectOne("""
                    SELECT BType, Weight 
                    FROM LAPTOP 
                    WHERE pid = %s
                """, product_id)
                if category_result:
                    category_row = category_result.row
                    row.update(category_row)

            elif product_type == 'Printer':
                category_result = DB.selectOne("""
                    SELECT PrinterType, Resolution 
                    FROM PRINTER 
                    WHERE pid = %s
                """, product_id)
                if category_result:
                    category_row = category_result.row
                    row.update(category_row)

        else:
            flash("Product not found", "danger")

    except Exception as e:
        print("Error getting details about the product", e)
        flash("Error fetching product details, please try again", "danger")

    return render_template("productdetail.html", rows=row)


@shop.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    product_id = request.form.get("pid")
    id = request.form.get("id", product_id)
    print("id", id)
    quantity = request.form.get("quantity", 1, type=int)
    user_id = current_user.get_id()

    if id and user_id:
        try:
            # Get the latest basket ID for the user
            basket_result = DB.selectOne("SELECT MAX(bid) as latest_bid FROM Basket WHERE cid = %s", user_id)
            latest_bid = basket_result.row["latest_bid"] if basket_result.status and basket_result.row else None

            # If there's no existing bid, create a new one
            if not latest_bid:
                create_basket_result = DB.insertOne("INSERT INTO Basket (cid) VALUES (%s)", user_id)
                if create_basket_result.status:
                    # Fetch the new bid ID
                    latest_bid_result = DB.selectOne("SELECT MAX(bid) as latest_bid FROM Basket WHERE cid = %s", user_id)
                    latest_bid = latest_bid_result.row["latest_bid"] if latest_bid_result.status and latest_bid_result.row else None
                else:
                    flash("Error creating a new cart, please try again", "danger")
            
            # Check if the product already exists in the user's latest basket
            appears_in_check = DB.selectOne("SELECT * FROM Appears_in WHERE bid = %s AND pid = %s", latest_bid, id)

            if quantity > 0:
                if appears_in_check.status and appears_in_check.row:
                    # Product exists in the latest basket, update quantity
                    result = DB.insertOne("""
                    UPDATE Appears_in SET
                    quantity = quantity + %(quantity)s
                    WHERE bid = %(latest_bid)s AND pid = %(id)s
                    """, {"id": id, "quantity": quantity, "latest_bid": latest_bid})
                    if result.status:
                        # Fetch product name for the flash message
                        product_name_result = DB.selectOne("SELECT pname FROM Product WHERE pid = %s", id)
                        product_name = product_name_result.row["pname"] if product_name_result.status and product_name_result.row else None
                        flash(f"Updated quantity for {product_name} in the cart to {quantity}", "success")
                else:
                    customer_status_result = DB.selectOne("SELECT Status FROM Customer WHERE cid = %s", current_user.get_id())
                    customer_status = customer_status_result.row["Status"] if customer_status_result.status and customer_status_result.row else None
                    offer_result = DB.selectOne("SELECT * FROM offer_product WHERE pid = %s", id)
                    flag = True if customer_status == 'Gold' or customer_status == 'Platinum' else False

                    if flag and offer_result.status and offer_result.row:
                        # Product exists in the offer_product table, use offerPrice
                        offer_price = offer_result.row["OfferPrice"]
                        query_params = {"id": id, "quantity": quantity, "latest_bid": latest_bid, "offer_price": offer_price}

                        result = DB.insertOne("""
                        INSERT INTO Appears_in (bid, pid, quantity, pricesold)
                        VALUES (%(latest_bid)s, %(id)s, %(quantity)s, %(offer_price)s)
                        """, query_params)
                    else:
                        # Product doesn't exist in the offer_product table, use pprice
                        query_params = {"id": id, "quantity": quantity, "latest_bid": latest_bid}

                        result = DB.insertOne("""
                        INSERT INTO Appears_in (bid, pid, quantity, pricesold)
                        VALUES (%(latest_bid)s, %(id)s, %(quantity)s, (SELECT pprice FROM Product WHERE pid = %(id)s))
                        """, query_params)

                    if result.status:
                        # Fetch product name for the flash message
                        product_name_result = DB.selectOne("SELECT pname FROM Product WHERE pid = %s", id)
                        product_name = product_name_result.row["pname"] if product_name_result.status and product_name_result.row else None
                        flash(f"Added {quantity} of {product_name} to the cart", "success")
            else:
                # Assuming delete
                if appears_in_check.status and appears_in_check.row:
                    # Product exists in the latest basket, delete the row
                    result = DB.delete("DELETE FROM Appears_in WHERE bid = %s AND pid = %s", latest_bid, id)
                    if result.status:
                        # Fetch product name for the flash message
                        product_name_result = DB.selectOne("SELECT pname FROM Product WHERE pid = %s", id)
                        product_name = product_name_result.row["pname"] if product_name_result.status and product_name_result.row else None
                        flash(f"Deleted {product_name} from the cart", "success")
                else:
                    flash(f"Product with ID {id} not found in the cart", "danger")

        except Exception as e:
            print("Error updating/deleting item from cart", e)
            flash("Error updating/deleting item from cart, please try again", "danger")

    rows = []
    credit_value=None
    try:
        # Fetch cart items for the user
        result = DB.selectAll("""
        SELECT a.bid, a.pid, pname, quantity, (quantity * a.pricesold) as subtotal 
        FROM Appears_in a 
        JOIN Product p on a.pid = p.pid 
        JOIN Basket b on b.bid = a.bid
        WHERE b.cid = %s AND b.bid=(SELECT MAX(bid) as latest_bid FROM Basket WHERE cid= %s)
        """, current_user.get_id(),current_user.get_id())

        if result and result.rows:
            rows = result.rows
        elif result:
            return render_template("clearcart.html")

        credit_result = DB.selectAll("SELECT cid, creditline FROM SILVER_AND_ABOVE WHERE cid=%s",current_user.get_id())
        if credit_result.status and credit_result.rows:
            credit_value = credit_result.rows[0]["creditline"]

    except Exception as e:
        print("Error getting cart", e)
        flash("Error fetching cart, please try again", "danger")

    return render_template("cart.html", rows=rows, credit_value=credit_value)


@shop.route("/update_cart", methods=["POST"])
def update_cart():
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity", type=int)

    try:
        # Fetch the product details including pname
        product_result = DB.selectOne("SELECT pname FROM Product WHERE pid = %s", product_id)

        if product_result.status and product_result.row:
            product_name = product_result.row["pname"]

            # Perform the necessary update logic in the database
            result = DB.update("""
                UPDATE Appears_in
                SET quantity = %(quantity)s
                WHERE pid = %(product_id)s AND bid = (SELECT MAX(bid) FROM Basket WHERE cid = %(user_id)s)
            """, {"quantity": quantity, "product_id": product_id, "user_id": current_user.get_id()})

            if result.status:
                flash(f"Updated quantity for {product_name} to {quantity}", "success")
            else:
                flash("Error updating quantity", "danger")
        else:
            flash(f"Product with ID {product_id} not found", "danger")

    except Exception as e:
        print("Error updating quantity:", e)
        flash("Error updating quantity", "danger")

    return redirect(url_for("shop.cart"))

@shop.route("/delete_from_cart", methods=["POST"])
def delete_from_cart():
    product_id = request.form.get("product_id")

    try:
        # Fetch the product name for display purposes
        product_result = DB.selectOne("SELECT pname FROM Product WHERE pid = %s", product_id)
        product_name = product_result.row["pname"] if product_result.status and product_result.row else "Unknown Product"

        # Perform the necessary delete logic in the database
        result = DB.delete("""
            DELETE FROM Appears_in
            WHERE pid = %(product_id)s AND bid = (SELECT MAX(bid) FROM Basket WHERE cid = %(user_id)s)
        """, {"product_id": product_id, "user_id": current_user.get_id()})

        if result.status:
            flash(f"Deleted {product_name} from the cart", "success")
        else:
            flash("Error deleting product from the cart", "danger")

    except Exception as e:
        print("Error deleting product from the cart:", e)
        flash("Error deleting product from the cart", "danger")

    return redirect(url_for("shop.cart"))

@shop.route("/clearcart", methods=["GET", "POST"])
def clear_cart():
    try:
        user_id = current_user.get_id()

        # Fetch the latest bid for the user
        bid_result = DB.selectOne("SELECT MAX(bid) as latest_bid FROM Basket WHERE cid = %s", user_id)
        latest_bid = bid_result.row["latest_bid"] if bid_result.status and bid_result.row else None

        if latest_bid:
            # Delete items from appears_in table for the latest bid
            result_appears_in = DB.delete("DELETE FROM Appears_in WHERE bid = %s", latest_bid)
            result_transaction_in = DB.delete("DELETE FROM Transaction WHERE bid = %s", latest_bid)

            if result_appears_in.status and result_transaction_in:
                # Now, delete the basket
                result_basket = DB.delete("DELETE FROM Basket WHERE bid = %s", latest_bid)

                if result_basket.status:
                    flash("Cart cleared successfully", "success")
                else:
                    flash("Error clearing cart, please try again", "danger")
            else:
                flash("Error clearing cart, please try again", "danger")
        else:
            flash("Cart is already empty", "warning")

    except Exception as e:
        print("Error clearing cart:", e)
        flash("Error clearing cart, please try again", "danger")

    return render_template("clearcart.html")

@shop.route("/proceed_to_checkout", methods=["GET", "POST"])
@login_required
def proceed_to_checkout():
    bid = request.args.get("bid")
    cart = []
    total = 0
    quantity = 0
    order = {}
    row = None  # Define 'row' with a default value of None

    try:
        result = DB.selectAll("""
        SELECT a.pid, p.pname, a.quantity, p.pquantity,p.pprice, a.pricesold
        FROM Appears_in a
        JOIN Product p ON a.pid = p.pid
        WHERE  a.bid=%s
        """,  bid)

        if result.status and result.rows:
            cart = result.rows

        # Verify cart
        has_error = False
        for item in cart:
            if item["quantity"] > item["pquantity"]:
                flash(f"Item {item['pname']} doesn't have enough stock left. Please update the quantity to {item['pquantity']} for a successful purchase.", "warning")
                has_error = True
            total += int(item["pricesold"] * item["quantity"])
            quantity += int(item["quantity"])

        if has_error:
            # Redirect to the cart if there are errors
            return redirect(url_for("shop.cart"))

    except Exception as e:
        print("Error fetching cart or verifying items", e)
        flash("Error fetching cart, please try again", "danger")
        traceback.print_exc()
        return redirect(url_for("shop.cart"))
    
    if request.method == "POST":
        has_error = False
        email = request.form.get("email")
        shipname = request.form.get("shipname")
        recepientname = request.form.get("recepientname")
        street = request.form.get("street")
        snumber = request.form.get("snumber")
        city = request.form.get("city")
        zipcode = request.form.get("zip")
        state = request.form.get("state")
        country = request.form.get("country")
        cc_number = request.form.get("cc_number")
        cc_security_number = request.form.get("cc_security_number")
        cc_owner_name = request.form.get("cc_owner_name")
        cc_type = request.form.get("cc_type")
        cc_billing_address = request.form.get("cc_billing_address")
        cc_exp_date = request.form.get("cc_exp_date")

        if  email == "" or shipname=="" or recepientname == "" or street == "" or snumber == "" or city == "" or state == "" or country == "" or zipcode == "":
            flash("Please fill in all the required fields for shipping information", "danger")
            return redirect(url_for('shop.proceed_to_checkout'))

        # Validation checks for payment information
        if cc_number== "" or cc_security_number=="" or cc_owner_name=="" or cc_type=="" or cc_billing_address=="" or cc_exp_date=="":
            flash("Payment Details is missing", "danger")
            return redirect(url_for('shop.proceed_to_checkout'))
        
        try:
            DB.getDB().autocommit = False  # start a transaction

            # Insert shipping address data
            shipping_address_id = -1
            if not has_error:
                result = DB.insertOne("""
                INSERT INTO Shipping_Address (CID, SAName, RecepientName, Street, SNumber, City, Zip, State, Country)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, current_user.get_id(), shipname, recepientname, street, snumber, city, zipcode, state, country)
                if not result.status:
                    flash("Error saving shipping address, please try again", "danger")
                    DB.getDB().rollback()
                    has_error = True
                else:
                    result_id = DB.selectOne("SELECT LAST_INSERT_ID() as last_id")
                    shipping_address_id = result_id.row['last_id']

            # Insert credit card data
            credit_card_id = -1
            if not has_error:
                result = DB.insertOne("""
                INSERT INTO Credit_Card (CCNumber, SecNumber, OwnerName, CCType, BilAddress, ExpDate, StoredCardCID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, cc_number, cc_security_number, cc_owner_name, cc_type, cc_billing_address, cc_exp_date, current_user.get_id())
                if not result.status:
                    flash("Error saving credit card information, please try again", "danger")
                    DB.getDB().rollback()
                    has_error = True
                else:
                    result_id = DB.selectOne("SELECT LAST_INSERT_ID() as last_id")
                    credit_card_id = result_id.row['last_id']

            # Create transaction data
            if not has_error:
                result = DB.insertOne("""
                INSERT INTO Transaction (BID, CCNumber, CID, SAName, TDate, TTag)
                VALUES (%s, %s, %s, %s, NOW(), 'Purchase')
                """, bid, cc_number, current_user.get_id(), shipname)
                if not result.status:
                    flash("Error recording transaction, please try again", "danger")
                    DB.getDB().rollback()
                    has_error = True

            if not has_error:
                result = DB.update("UPDATE Product set pquantity = pquantity - (select IFNULL(quantity, 0) FROM Appears_in WHERE Appears_in.pid = Product.pid and appears_in.bid = %(bid)s) WHERE pid in (SELECT pid from Appears_in where bid = %(bid)s)", {"bid":bid} )
                if not result.status:
                    flash("Error updating stock, please try again!", "danger")
                    has_error = True
                    DB.getDB().rollback()

            # Select transaction for the current basket ID
            if not has_error:
                result = DB.selectOne("""
                SELECT *
                FROM Transaction
                WHERE BID = %s and cid=%s
                """, bid, current_user.get_id())
                transaction_data = result.row if result and result.row else None

                if not has_error:
                    DB.getDB().commit()
                    flash("Purchase successful, keep shopping with us!", "success")
                    return redirect(url_for("shop.purchase", id=bid))
                else:
                    return redirect(url_for("shop.cart"))

        except Exception as e:
            print("Transaction exception", e)
            flash("Something went wrong, please try again!", "danger")
            traceback.print_exc()
            DB.getDB().rollback()

    try:
        result = DB.selectOne("""SELECT email FROM Customer WHERE cid = %s""", current_user.get_id())
        if result.status:
            row = result.row
    except Exception as e:
        flash("Data cannot be fetched, please try again", "danger")

    return render_template("proceed_to_checkout.html", row=row)


@shop.route("/purchase", methods=["GET", "POST"])
@login_required
def purchase():
    order_id = request.args.get("id")
    cart = []
    transaction_details = {}
    credit_value=None
    try:
        # Fetch transaction details
        transaction_result = DB.selectOne("""
            SELECT t.BID, t.CCNumber, t.SAName, t.TDate, COUNT(ai.pid) as product_count,
            SUM(ai.pricesold * ai.quantity) as total_price
            FROM Transaction t
            JOIN Appears_in ai ON t.BID = ai.bid
            JOIN Product p ON ai.pid = p.pid
            WHERE t.BID = %s
            GROUP BY t.BID, t.CCNumber, t.SAName, t.TDate;
        """, order_id)

        if transaction_result.status and transaction_result.row:
            transaction_details = transaction_result.row
            print("Transaction")
            print(transaction_details)


        # Fetch items in the order
        item_result = DB.selectAll("""
            SELECT ai.bid, p.pname as name, ai.quantity as quantity, ai.pricesold as unit_price,
                   (ai.quantity * ai.pricesold) as subtotal
            FROM Appears_in ai
            JOIN Product p ON ai.pid = p.pid
            WHERE ai.bid = %s
        """, order_id)

        if item_result.status and item_result.rows:
            cart = item_result.rows
            print("Cart")
            print(cart)

        credit_result = DB.selectAll("SELECT cid, creditline FROM SILVER_AND_ABOVE WHERE cid=%s",current_user.get_id())

        if credit_result.status and credit_result.rows:
            credit_value = credit_result.rows[0]["creditline"]

        create_basket_result = DB.insertOne("INSERT INTO Basket (cid) VALUES (%s)", current_user.get_id())

        if not create_basket_result.status:
            flash("Error creating a new cart, please try again", "danger")

    except Exception as e:
        flash("Something went wrong, please try again", "danger")
        print("Error:", e)
        traceback.print_exc()

    return render_template("order_summary.html", rows=cart, order=transaction_details, credit_value=credit_value)


@shop.route("/orders", methods=["GET"])
@login_required
def orders():
    rows = [] 
    credit_value=None
    try:   
        result = DB.selectAll("""
        SELECT
        a.bid,
        ROUND(SUM(a.pricesold * a.quantity), 2) as total_price,
        t.TDate as transaction_date
        FROM Appears_in a
        JOIN Transaction t ON a.bid = t.BID
        LEFT JOIN SILVER_AND_ABOVE sa ON t.CID = sa.CID
        WHERE t.CID = %s
        GROUP BY a.bid, t.TDate
        ORDER BY a.bid DESC
        LIMIT 10
        """, current_user.get_id())
        
        if result.status and result.rows:
            rows = result.rows

        credit_result = DB.selectAll("SELECT cid, creditline FROM SILVER_AND_ABOVE WHERE cid=%s",current_user.get_id())

        if credit_result.status and credit_result.rows:
            credit_value = credit_result.rows[0]["creditline"]
            

    except Exception as e:
        print("Error getting orders", e)
        flash("Error fetching orders, please try again!", "danger")
        traceback.print_exc()
    return render_template("orders.html", rows=rows, credit_value=credit_value)

@shop.route("/order", methods=["GET"])
@login_required
def order():
    rows = []
    total = 0
    ship = {}
    bid = request.args.get("id")
    credit_value=None
    
    if not bid:
        flash("Invalid order", "danger")
        return redirect(url_for("shop.orders"))

    try:
        # Fetch product details
        result = DB.selectAll("""
        SELECT
            p.pname,
            ai.pricesold,
            ai.quantity,
            ROUND((ai.pricesold * ai.quantity),2) as subtotal
        FROM Appears_in ai
        JOIN Product p ON ai.pid = p.pid
        WHERE ai.bid = %s
        """, bid)

        if result.status and result.rows:
            rows = result.rows

        # Fetch shipment and payment details
        ship_result = DB.selectOne("""
        SELECT
            t.SAName,
            t.TDate
        FROM Transaction t
        WHERE t.BID = %s
        """, bid)

        if ship_result.status and ship_result.row:
            ship = ship_result.row
            print(rows)
        
        

    except Exception as e:
        print("Error getting order", e)
        flash("Error fetching order, please try again", "danger")

    return render_template("order.html", rows=rows, total=total, ship=ship)



