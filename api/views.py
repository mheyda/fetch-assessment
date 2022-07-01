from django.shortcuts import render
from django import forms
from datetime import datetime
import time
from django.http import HttpResponse, HttpResponseRedirect
import json


data = {
    "transactions": [
        { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" },
        { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
        { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
        { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
        { "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
    ],
    "balances": {
        "DANNON": 1100, 
        "UNILEVER": 200, 
        "MILLER COORS": 10000
    }
}

payers = {}


# Forms
class add_transaction(forms.Form):
    payer = forms.CharField(label="Payer", widget=forms.TextInput())
    points = forms.DecimalField(label="Number of Points", decimal_places = 0, max_digits = 6, widget=forms.TextInput())
add_transaction_form = add_transaction()

class spend_points(forms.Form):
    points = forms.DecimalField(label="Number of Points", decimal_places = 0, max_digits = 6, widget=forms.TextInput())
spend_points_form = spend_points()


def index(request):
    return render(request, "index.html", {
        "add_transaction_form": add_transaction_form,
        "spend_points_form": spend_points_form,
        "transactions": data["transactions"],
        "balances": data["balances"],
    })


def transactions(request):

    if request.method == "POST":
        # Extract transaction inputs
        payer = request.POST["payer"]
        points = int(request.POST["points"])

        # Get date and time of transaction
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Push transaction to storage and sort by timestamp
        data["transactions"].append({"payer": payer, "points": points, "timestamp": timestamp, "spent": False})
        data["transactions"].sort(key=lambda trans:time.mktime(time.strptime(trans['timestamp'], '%Y-%m-%dT%H:%M:%SZ')))

        # Push payer to balances if they don't already exist
        if not payer in data["balances"]:
            data["balances"][payer] = points
        # Otherwise adjust balances accordingly
        else:
            data["balances"][payer] = data["balances"][payer] + points      

    return HttpResponseRedirect("/")


def points(request):

    # Spend points
    if request.method == "POST":
        points_to_spend = int(request.POST["points"])
        transaction_index = 0
        points_spent = {}
        original_balances = data["balances"].copy()

        while points_to_spend > 0:
            current_payer = data["transactions"][transaction_index]["payer"]

            # Make sure the current payer's balance is large enough to handle current transaction
            if data["balances"][current_payer] > data["transactions"][transaction_index]["points"]:
                # If there's enough from the current transaction
                if data["transactions"][transaction_index]["points"] > points_to_spend:
                    if current_payer in points_spent:
                        points_spent[current_payer] = points_spent[current_payer] - points_to_spend
                    else:
                        points_spent[current_payer] = -points_to_spend
                    data["balances"][current_payer] = data["balances"][current_payer] - points_to_spend
                    points_to_spend = 0

                # If more transactions are needed
                else:
                    if current_payer in points_spent:
                        points_spent[current_payer] = points_spent[current_payer] - data["transactions"][transaction_index]["points"]
                    else:
                        points_spent[current_payer] = -data["transactions"][transaction_index]["points"]
                    data["balances"][current_payer] = data["balances"][current_payer] - data["transactions"][transaction_index]["points"]
                    points_to_spend = points_to_spend - data["transactions"][transaction_index]["points"]
                    
            # If transaction is more than current payer's balance
            else:
                # If current payer has more points than need to be spent, finish
                if data["balances"][current_payer] > points_to_spend:
                    if current_payer in points_spent:
                        points_spent[current_payer] = points_spent[current_payer] - points_to_spend
                    else:
                        points_spent[current_payer] = -points_to_spend
                    data["balances"][current_payer] = data["balances"][current_payer] - points_to_spend
                    points_to_spend = 0
                # Empty current payer's balance and continue
                else:                    
                    if current_payer in points_spent:
                        points_spent[current_payer] = points_spent[current_payer] - data["balances"][current_payer]
                    else:
                        points_spent[current_payer] = -data["balances"][current_payer]
                    points_to_spend = points_to_spend - data["balances"][current_payer]
                    data["balances"][current_payer] = 0
            
            transaction_index = transaction_index + 1

        output = []
        for key, value in data["balances"].items():
            output.append({ "payer": key, "points": value - original_balances[key] })

        return HttpResponse(json.dumps(output))



def balances(request):
    if request.method == "GET":
        return HttpResponse(json.dumps(data["balances"]))