from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Allow CORS for Flutter frontend

ATTENDANCE_URL = "https://sadakath.ac.in/attend/attendance2.aspx"

# Function to fetch and parse attendance data
def get_attendance(roll_number):
    session = requests.Session()
    response = session.get(ATTENDANCE_URL)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch attendance page"}, 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    hidden_inputs = {tag['name']: tag['value'] for tag in soup.find_all('input', type='hidden')}
    
    payload = {
        "txtregno": roll_number,
        "btngetattendance": "Get Attendance",
        **hidden_inputs  # Include hidden fields from the page
    }
    
    post_response = session.post(ATTENDANCE_URL, data=payload)
    
    if post_response.status_code != 200:
        return {"error": "Failed to fetch attendance details"}, 500
    
    soup = BeautifulSoup(post_response.text, 'html.parser')
    attendance_details = {}
    
    table = soup.find('table', {'class': 'table table-bordered'})
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skipping header
            cols = row.find_all('td')
            if len(cols) >= 4:
                subject = cols[0].text.strip()
                attended = cols[1].text.strip()
                total = cols[2].text.strip()
                percentage = cols[3].text.strip()
                attendance_details[subject] = {
                    "attended": attended,
                    "total": total,
                    "percentage": percentage
                }
    
    return {"attendance": attendance_details}

@app.route('/attendance', methods=['POST'])
def attendance():
    data = request.get_json()  # Get JSON request body
    reg_no = data.get('reg_no') if data else None  # Extract 'reg_no' from JSON

    if not reg_no:
        return jsonify({"error": "Missing roll number"}), 400  # Handle missing roll number

    try:
        url = 'https://sadakath.ac.in/attend/attendance2.aspx'
        viewstate, viewstate_generator, event_validation = fetch_hidden_fields(url)
        attendance_details = get_attendance_details(url, reg_no, viewstate, viewstate_generator, event_validation)

        return jsonify(attendance_details)  # Return JSON response

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle exceptions properly



# Vercel Handler
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
