from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv

app = Flask(__name__)

# ------------------- ROUTES -------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cv')
def cv():
    return render_template('page1.html')

@app.route('/portofolio')
def portofolio():
    return render_template('page2.html')

@app.route('/biodata')
def biodata():
    return render_template('page3.html')

@app.route('/contact')
def contact():
    return render_template('page4.html')

# ------------------- FIBONACCI -------------------
def fibonacci_series(n):
    fib = [0, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

@app.route('/fibonacci', methods=['GET', 'POST'])
def fibonacci():
    if request.method == 'POST':
        num = int(request.form['number'])
        result = fibonacci_series(num)
        return render_template('fibonacci.html', result=result)
    return render_template('fibonacci.html')

# ------------------- DISPLAY CSV AS JSON  -------------------
@app.route('/csv')
def view_csv():
    csv_file_path = 'datapribadi.csv'
    data = []

    with open(csv_file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    
    return jsonify(data)

# ------------------- FORM PAGE  -------------------
# List to store form entries
entries = []

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        job = request.form['job']
        
        entries.append({'name': name, 'age': age, 'job': job})
        
        return redirect(url_for('form'))
    
    return render_template('form.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)