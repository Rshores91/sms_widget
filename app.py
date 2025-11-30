from flask import Flask, request, render_template, redirect, url_for, jsonify, flash, session
import requests
import os 
import urllib3

# Disable SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__) # creates flask app instance
app.secret_key = 'your_secret_key' # sets a secret key for the app
# This key is used for session management and CSRF protection

# Allow overriding the backend base URL via environment variable for flexibility
API_BASE = os.getenv('API_URL', 'https://localhost:7010')

# Fallback interests so managers can still target core music genres before data exists
DEFAULT_INTEREST_OPTIONS = [
    "EDM",
    "Hip-Hop",
    "Karaoke",
    "Live Band"
]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        api_url = f"{API_BASE.rstrip('/')}/api/auth/login"
        payload = {"Username": username, "Password": password}
        
        try:
            # verify=False is used to bypass SSL certificate validation for local testing
            response = requests.post(api_url, json=payload, timeout=10, verify=False)
            if response.status_code == 200:
                data = response.json()
                session['token'] = data.get('token')
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('sms_dashboard'))
            else:
                flash('Invalid credentials', 'danger')
        except requests.exceptions.RequestException as e:
            flash(f"Could not contact backend: {e}", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# Dashboard page to enter and send SMS
@app.route('/dashboard') # defines the route for the dashboard page
def sms_dashboard():
    if 'token' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    headers = {'Authorization': f"Bearer {session['token']}"}
    metrics = {}
    customers = []
    interest_options = []

    metrics_url = f"{API_BASE.rstrip('/')}/api/customers/metrics"
    customers_url = f"{API_BASE.rstrip('/')}/api/customers"
    interests_url = f"{API_BASE.rstrip('/')}/api/customers/interests"

    try:
        metrics_resp = requests.get(metrics_url, headers=headers, timeout=10, verify=False)
        if metrics_resp.status_code == 200:
            metrics = metrics_resp.json()
        else:
            flash('Could not load customer metrics from the backend.', 'danger')
    except requests.exceptions.RequestException as e:
        flash(f'Could not contact backend for metrics: {e}', 'danger')

    try:
        interests_resp = requests.get(interests_url, headers=headers, timeout=10, verify=False)
        if interests_resp.status_code == 200:
            interest_options = interests_resp.json()
        else:
            flash('Could not load customer interests from the backend.', 'danger')
    except requests.exceptions.RequestException as e:
        flash(f'Could not contact backend for interests: {e}', 'danger')

    if not interest_options and metrics:
        interest_options = sorted(metrics.get('interestBreakdown', {}).keys())

    if interest_options:
        interest_options = sorted(set(interest_options + DEFAULT_INTEREST_OPTIONS))
    else:
        interest_options = DEFAULT_INTEREST_OPTIONS

    try:
        customers_resp = requests.get(customers_url, headers=headers, timeout=10, verify=False)
        if customers_resp.status_code == 200:
            customers = customers_resp.json()
        else:
            flash('Could not load customer list from the backend.', 'danger')
    except requests.exceptions.RequestException as e:
        flash(f'Could not contact backend for customers: {e}', 'danger')

    return render_template(
        'sms_dashboard.html',
        metrics=metrics,
        customers=customers,
        interest_options=interest_options
    )

@app.route('/send-sms', methods=['POST'])
def send_sms():
    if 'token' not in session:
        return redirect(url_for('login'))
        
    to_number = request.form.get('phone')
    message_body = request.form.get('message')
    
    api_url = f"{API_BASE.rstrip('/')}/api/sms/send"
    headers = {'Authorization': f"Bearer {session['token']}"}
    payload = {"Recipient": to_number, "Message": message_body}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            flash(f'Message sent to {to_number}!', 'success')
        else:
            # Try to parse JSON error from backend
            try:
                error_data = response.json()
                error_message = error_data.get('error', response.text)
            except ValueError:
                error_message = response.text
            
            flash(f'Failed to send message: {error_message}', 'danger')
            print(f"Error sending SMS: {response.status_code} - {response.text}")
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        print(f"Exception sending SMS: {e}")

    return redirect(url_for('sms_dashboard'))

@app.route('/send-bulk-sms', methods=['POST'])
def send_bulk_sms():
    if 'token' not in session:
        return redirect(url_for('login'))
        
    tag = request.form.get('tag')
    template = request.form.get('template')
    
    api_url = f"{API_BASE.rstrip('/')}/api/sms/bulk"
    headers = {'Authorization': f"Bearer {session['token']}"}
    payload = {"RecipientTag": tag, "MessageTemplate": template}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            flash(f"Bulk SMS sent! Success: {data.get('successful')}, Failed: {data.get('failed')}", 'success')
        else:
            flash(f'Failed to send bulk messages: {response.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('sms_dashboard'))

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

    # Allow overriding the backend base URL via environment variable for flexibility
    # API_BASE is defined globally now
    api_url = f"{API_BASE.rstrip('/')}/api/customers"
    # alternate: https://marketing.brnhome.com/api/customers/
    payload = {
        "Name" : request.form['name'], # retrieves the name from the form
        "Email" : request.form['email'], # retrieves the email from the form
        "PhoneNumber" : request.form['phone'], # retrieves the phone number from the form
        "Birthday" : request.form['birthday'], # retrieves the birthday from the form
        "Interest" : request.form['event'], # retrieves the event from the form
        "AgreeToSms" : 'optin' in request.form
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10, verify=False)
    except requests.exceptions.RequestException as e:
        # Show the exception message to help debugging local connectivity issues
        flash(f"Could not contact backend: {e}", "danger")
        return redirect(url_for('customer_form'))

    # If backend returned 4xx/5xx, try to extract a friendly message and show it to the user
    if response.status_code >= 400:
        backend_text = response.text or ""
        backend_msg = None

        # If backend returned JSON, try to parse potential message fields
        try:
            data = response.json()
            # common shapes: { "message": "..."} or { "error": "..."} or ModelState dict
            backend_msg = data.get("message") or data.get("error") or data.get("detail")
            # If ModelState (dictionary), join the errors
            if backend_msg is None and isinstance(data, dict):
                parts = []
                for k, v in data.items():
                    if isinstance(v, list):
                        parts.extend(v)
                    elif isinstance(v, str):
                        parts.append(v)
                if parts:
                    backend_msg = "; ".join(parts)
        except Exception:
            # not JSON, fallback to raw text
            backend_msg = backend_text.strip()

        if not backend_msg:
            backend_msg = f"Server returned {response.status_code}"

        flash(backend_msg, "danger")
        return redirect(url_for('customer_form'))

    # success -> continue
    return redirect(url_for('thank_you'))

    # try:
    #     response = requests.post(api_url, json=payload)
    #     response.raise_for_status()
    # except requests.exceptions.RequestException as e:
    #     return jsonify({"error": str(e)}), 500

    # return redirect(url_for('thank_you')) # redirects to thank you page
    


@app.route('/thank-you') # defines the route for the thank you page
def thank_you():
    return render_template('thank_you.html') # renders the thank you template

if __name__ == '__main__': # checks if the script is run directly
    # if __name__ == '__main__': is a common Python idiom
    # Use debug mode only in development
    import os
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode) # runs the app in debug mode if in development