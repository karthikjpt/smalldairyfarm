import os
import csv
from flask import Flask, render_template, request

app = Flask(__name__)

def generate_unique_id(name):
    cleaned_name = name.replace(" ", "").lower()
    csv_file = os.path.join('member_data', 'member_data.csv')

    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # Read existing IDs from the CSV file
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            row_count = sum(1 for row in reader)  # Count rows after skipping the header

    else:
        row_count = 0

    # Generate the unique ID based on the row count
    # Format the row_count with leading zeros for up to three digits
    unique_id = f"{row_count + 1:03}-{cleaned_name}"
    return unique_id


# Function to save data to CSV file
def save_to_member_csv(filename, data, folder):
    csv_file = os.path.join(folder, filename)
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if os.stat(csv_file).st_size == 0:
            writer.writerow(["ID", "Name", "Join Date", "Phone Number"])
        writer.writerow(data)

# Function to save data to CSV file
def save_to_dailyinward_csv(filename, data, folder):
    csv_file = os.path.join(folder, filename)
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if os.stat(csv_file).st_size == 0:
            writer.writerow(["Date", "Season", "ID", "Quantity", "Fat", 'SMF', 'Rate', 'Total Amount'])
        writer.writerow(data)

@app.route('/member_register', methods=['POST'])
def member_register():
    if request.method == 'POST':
        name = request.form['name']
        join_date = request.form['join_date']
        phone_number = request.form['phone_number']
        unique_id = generate_unique_id(name)
        save_to_member_csv('member_data.csv', [unique_id, name, join_date, phone_number], 'member_data')
        success_message = 'Registration successful!'
        return render_template('member_register.html', success_message=success_message)

@app.route('/daily_milk_register', methods=['GET', 'POST'])
def daily_milk_register():
    if request.method == 'POST':
        date = request.form['date']
        season = request.form['season']
        member_id = request.form['id']
        quantity = float(request.form['quantity'])
        fat = float(request.form['fat'])
        smf = float(request.form['smf'])
        rate = float(request.form['rate'])
        total_amount = float(request.form['total_amount'])
        
        last_date = request.form['last_date']
        last_season = request.form['last_season']
        
        # Save the new entry to CSV file
        save_to_dailyinward_csv('dailyinward.csv', [date, season, member_id, quantity, fat, smf, rate, total_amount], folder='daily_records')
        
        # Render the template with success message and last entry preserved
        return render_template('daily_milk_register.html', success_message='Entry added successfully!', ids=get_ids_from_csv(), last_date=date, last_season=season, rate=rate, total_amount=total_amount)

    # If it's a GET request, simply render the template with the last entry preserved
    return render_template('daily_milk_register.html', ids=get_ids_from_csv(), last_date='', last_season='', rate='', total_amount='')


def get_ids_from_csv():
    csv_file = os.path.join('member_data', 'member_data.csv')
    ids = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            ids.append(row[0])
    return ids

@app.route('/generate_receipt', methods=['GET', 'POST'])
def generate_receipt():
    if request.method == 'POST':
        selected_ids = request.form.getlist('member_id')
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Filter data based on selected member IDs and date range
        filtered_data = []
        csv_file_path = os.path.join('daily_records', 'dailyinward.csv')
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    if row[2] in selected_ids and start_date <= row[0] <= end_date:
                        filtered_data.append(row)

        # Prepare individual receipts for each member ID
        individual_receipts = {}
        for member_id in selected_ids:
            member_receipts = [row for row in filtered_data if row[2] == member_id]
            individual_receipts[member_id] = member_receipts

        return render_template('view_inward.html', individual_receipts=individual_receipts)

    return render_template('generate_receipt.html', ids=get_ids_from_csv())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/member_new_register')
def register():
    return render_template('member_register.html')

@app.route('/daily_milk_register')
def daily_milk_register_page():
    return render_template('daily_milk_register.html', ids=get_ids_from_csv())

if __name__ == '__main__':
    if not os.path.exists('member_data'):
        os.makedirs('member_data')
    if not os.path.exists('daily_records'):
        os.makedirs('daily_records')
    app.run(debug=True)

