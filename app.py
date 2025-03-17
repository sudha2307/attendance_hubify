import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = "https://sadakath.ac.in/attend/attendance3.aspx"

def get_attendance(reg_no):
    session = requests.Session()
    
    # Step 1: Get Initial Page to Extract Hidden Fields
    response = session.get(BASE_URL)
    if response.status_code != 200:
        return {"error": "Failed to load attendance page"}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract hidden fields required for form submission
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
    
    # Step 2: Submit Form with Registration Number
    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventvalidation,
        "TxtRegno": reg_no,
        "Button1": "Submit",
    }

    post_response = session.post(BASE_URL, data=payload)
    if post_response.status_code != 200:
        return {"error": "Failed to fetch attendance details"}
    
    # Step 3: Parse the Response
    soup = BeautifulSoup(post_response.text, 'html.parser')

    # Extract Student Name and Admin Number
    admin_no = soup.find("span", {"id": "Label1"}).text.strip()
    student_name = soup.find("span", {"id": "Label2"}).text.strip()

    # Extract Attendance Data Table
    table = soup.find("table", {"id": "GridView1"})
    rows = table.find_all("tr")[1:]  # Skipping header row

    attendance_records = []
    for row in rows:
        cols = [col.text.strip() for col in row.find_all("td")]
        attendance_records.append({
            "RegNo": cols[0],
            "SubCode": cols[1],
            "Total": cols[2],
            "Present": cols[3],
            "Absent": cols[4],
            "OD": cols[5],
            "Total_Present": cols[6],
            "Present_Percentage": cols[7]
        })

    return {
        "AdminNo": admin_no,
        "Name": student_name,
        "Attendance": attendance_records
    }

@app.route('/attendance_1st_year', methods=['POST'])
def fetch_attendance():
    data = request.get_json()
    if not data or 'reg_no' not in data:
        return jsonify({"error": "Missing registration number"}), 400
    
    reg_no = data['reg_no']
    result = get_attendance(reg_no)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
