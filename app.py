from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_attendance(reg_no, year):
    try:
        if year == "1st year":
            url = 'https://sadakath.ac.in/attend/attendance3.aspx'
        else:
            url = 'https://sadakath.ac.in/attend/attendance2.aspx'

        data = {'regno': reg_no}
        response = requests.post(url, data=data)

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})

        records = []
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                record = {
                    'CCode': cols[0].text.strip(),
                    'SName': cols[1].text.strip(),
                    'Total': cols[2].text.strip(),
                    'Present': cols[3].text.strip(),
                    'Absent': cols[4].text.strip(),
                    'OD': cols[5].text.strip(),
                    'Percentage': cols[6].text.strip()
                }
                records.append(record)
        return records
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/attendance', methods=['POST'])
def get_attendance():
    data = request.json
    reg_no = data.get('reg_no')
    year = data.get('year')
    records = scrape_attendance(reg_no, year)
    return jsonify({'Records': records})

if __name__ == '__main__':
    app.run(debug=True)
