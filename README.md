# Fetch Rewards Backend Assessment

Welcome! In this repository, you'll find a Python/Django project hosted on Heroku that accomplishes the tasks given in the <a href='https://fetch-hiring.s3.us-east-1.amazonaws.com/points.pdf' target='_blank' ref='noreferrer'>coding exercise requirements</a>.

## How to use
<ol>
  <li>Go to <a href='https://fetch-assessment.herokuapp.com/' target='_blank' ref='noreferrer'>https://fetch-assessment.herokuapp.com/</a></li>
  <li>Add transactions using the HTML form provided. This form sends a POST request to the server and adds transactions accordingly.</li>
  <li>Spend points using the HTML form provided. This form also sends a POST request to the server and spends points accordingly.</li>
  <li>If you'd like to reset the transactions and balances, click the reset button at the top.</li>
</ol>

## Files
Most of the code is boilerplate from setting up a Django project, but the files relevant to this exercise are detailed below.

<p>
  <strong>URL Routes</strong> - found in fetch_assessment/urls.py
</p>
<p>
<strong>Route Logic</strong> - found in api/views.py
  <br>
  The routes provided do the following:
  <ul>
    <li>Index: a simple home page to view all transactions and balances, as well as post a new transaction or spend points</li>
    <li>Transactions: allows users to post transactions. Automatically redirects to the home page</li>
    <li>Points: allows users to spend points. Returns a list of dictionaries with the amount of points spent from each payer</li>
    <li>Balances: allows users to view the balances of all previous payers. Returns a dictionary with the balance of each payer</li>
    <li>Reset: allows user to reset balances and transactions</li>
  </ul>
</p>
