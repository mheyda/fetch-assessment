from django.shortcuts import render
from django import forms
from datetime import datetime
import time
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.utils.safestring import mark_safe

transaction_data = []
balance_data = {}

# Forms
class add_transaction(forms.Form):
    payer = forms.CharField(label="Payer: ", widget=forms.TextInput())
    points = forms.DecimalField(label="Number of Points: ", decimal_places = 0, max_digits = 6, widget=forms.TextInput())
    timestamp = forms.CharField(label=mark_safe("Timestamp (optional, defaults to current time)<br />Format: yyyy-mm-ddThh:mm:ssZ<br />Example: 2020-11-02T14:00:00Z"), widget=forms.TextInput(), required=False)
add_transaction_form = add_transaction()

class spend_points(forms.Form):
    points = forms.DecimalField(label="Number of Points", decimal_places = 0, max_digits = 6, widget=forms.TextInput())
spend_points_form = spend_points()


# Home page
def index(request):
    return render(request, "index.html", {
        "add_transaction_form": add_transaction_form,
        "spend_points_form": spend_points_form,
        "transactions": transaction_data,
        "balances": balance_data,
    })

# Transactions route
def transactions(request):

    # User wants to post a transaction
    if request.method == "POST":

        # Extract transaction data from request
        payer = request.POST["payer"]
        points = int(request.POST["points"])
        if request.POST["timestamp"]:
            timestamp = request.POST["timestamp"]
        else:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Push transaction to storage and sort by timestamp
        transaction_data.append({"payer": payer, "points": points, "timestamp": timestamp})
        transaction_data.sort(key=lambda trans:time.mktime(time.strptime(trans['timestamp'], '%Y-%m-%dT%H:%M:%SZ')))

        # Push payer to balances if they don't already exist
        if not payer in balance_data:
            balance_data[payer] = points
        # Otherwise adjust balances accordingly
        else:
            balance_data[payer] = balance_data[payer] + points      

    return HttpResponseRedirect("/")


# Points route
def points(request):

    # User wants to spend points
    if request.method == "POST":
        points_to_spend = int(request.POST["points"]) # Extract number of points to spend from request
        transaction_index = 0 # Iterator to loop through transactions
        original_balances = balance_data.copy() # Copy original balances to calculate output later

        # Make sure the user has enough points
        if sum(balance_data.values()) > points_to_spend:
            
            # Loop through transactions starting with the oldest
            while points_to_spend > 0:

                # Save values for current comparison
                current_payer = transaction_data[transaction_index]["payer"]
                current_payer_balance = balance_data[current_payer]
                current_transaction_points = transaction_data[transaction_index]["points"]

                # Check if current payer's balance is more than what the current transaction requires
                if current_payer_balance > current_transaction_points:

                    # If there's enough from the current transaction
                    if current_transaction_points > points_to_spend:
                        current_payer_balance = current_payer_balance - points_to_spend
                        points_to_spend = 0

                    # If more transactions are needed
                    else:
                        current_payer_balance = current_payer_balance - current_transaction_points
                        points_to_spend = points_to_spend - current_transaction_points
                        
                # If transaction is more than current payer's balance
                else:
                    # If current payer has more points than need to be spent, finish
                    if current_payer_balance > points_to_spend:
                        current_payer_balance = current_payer_balance - points_to_spend
                        points_to_spend = 0
                    # Empty current payer's balance and continue
                    else:                    
                        points_to_spend = points_to_spend - current_payer_balance
                        current_payer_balance = 0

                # Update data that was passed by value and increment
                balance_data[current_payer] = current_payer_balance
                transaction_index = transaction_index + 1

            # Generate output based on what was spent by who
            output = []
            for key, value in balance_data.items():
                output.append({ "payer": key, "points": value - original_balances[key] })

            return HttpResponse(json.dumps(output))

        # User doesn't have enough points
        else:
            return HttpResponse("You don't have enough points!")


# Balances route
def balances(request):
    # User wants to view the balances from all payers
    if request.method == "GET":
        return HttpResponse(json.dumps(balance_data))


# Reset route
def reset(request):
    # User wants to clear transactions
    if request.method == "POST":
        transaction_data.clear()
        balance_data.clear()
    
    return HttpResponseRedirect("/")