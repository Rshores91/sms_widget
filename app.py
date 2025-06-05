from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__) # creates flask app instance


@app.route('/') # defines the route for the home page
def home():
    return redirect(url_for('customer_form'))
# redirects the user to the customer form page

@app.route('/customer-form') # defines the route for the home page

def customer_form():
    return render_template('customer_form.html')
# renders the customer form template
# when the user accesses the '/customer-form' URL

@app.route('/submit', methods=['POST']) # defines the route for form submission
def submit():
    name = request.form['name'] # retrieves the name from the form
    email = request.form['email'] # retrieves the email from the form
    phone = request.form['phone'] # retrieves the phone number from the form
    birthday = request.form['birthday'] # retrieves the birthday from the form
    event = request.form['event'] # retrieves the event from the form
    optin = 'optin' in request.form
    # retrieves the opt-in status from the form
    # Here you can process the data as needed (e.g., save to a database)

    # save the data to a CSV file
    with open('data/customer_data.csv', 'a', encoding='utf-8') as f:
        import csv
        writer = csv.writer(f)
        writer.writerow([name, email, phone, birthday, event, optin])

    # writes the data to a CSV file
    return redirect(url_for('thank_you')) # redirects to thank you page
    
@app.route('/thank-you') # defines the route for the thank you page
def thank_you():
    return render_template('thank_you.html') # renders the thank you template

if __name__ == '__main__': # checks if the script is run directly
    # if __name__ == '__main__': is a common Python idiom
    # Use debug mode only in development
    import os
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode) # runs the app in debug mode if in development