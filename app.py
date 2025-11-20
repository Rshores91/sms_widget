from flask import Flask, request, render_template, redirect, url_for
from twilio.rest import Client
# Import necessary modules from Flask and Twilio
from email_validator import validate_email, EmailNotValidError
# Import necessary modules from Flask and email_validator

app = Flask(__name__) # creates flask app instance
app.secret_key = 'your_secret_key' # sets a secret key for the app
# This key is used for session management and CSRF protection

# # Dashboard page to enter and send SMS                                          -----------FINISH THIS PART -------------------
# @app.route('/dashboard') # defines the route for the dashboard page
# def sms_dashboard():
#     if request.method == 'POST': # checks if the request method is POST
#         to_number = request.form.get('phone') # retrieves the phone number from the form
#         message_body = request.form.get('message') # retrieves the message body from the form

#         # Twilio setup
#         account_sid = os.getenv('TWILIO_ACCOUNT_SID') # retrieves the Twilio account SID from environment variables
#         auth_token = os.getenv('TWILIO_AUTH_TOKEN') # retrieves the Twilio auth token from environment variables
#         from_number = os.getenv('TWILIO_PHONE_NUMBER')
#         # retrieves the Twilio phone number from environment variables

#         try: 
#             client = Client(account_sid, auth_token)
#             message = client.messages.create(
#                 body=message_body, # sets the message body
#                 from_=from_number, # sets the sender's phone number
#                 to=to_number # sets the recipient's phone number
#             )
#             flash(f'Message sent to {to_number}!', 'success')
#         except Exception as e:
#             flash(f'Error: {str(e)}', 'danger')

#         return redirect(url_for('sms_dashboard')) # redirects to the dashboard page
    
#     return render_template('dashboard.html') # renders the dashboard template

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
 
    # # validation

    # errors = []
    # try:
    #     valid = validate_email(email)  # validates the email format
    #     email = valid.email

    # if not name or len(name) < 2:
    #     errors.append('Name must be at least 2 characters long.')

    

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