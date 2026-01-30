import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'nrega_bot_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nrega_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---

# 1. Semi-Skilled Format
class SemiSkilled(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100))
    panchayat = db.Column(db.String(100))
    fin_year = db.Column(db.String(20))
    reg_no = db.Column(db.String(50))
    mapped_jc = db.Column(db.String(50))
    status_jc = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    ac_no = db.Column(db.String(50))
    ifsc = db.Column(db.String(20))
    wagelist = db.Column(db.String(100))
    status_wl = db.Column(db.String(50))
    muster_roll = db.Column(db.String(50))

# 2. Deleted Jobcard Format
class DeletedJobcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100)) # Added for operator tracking
    panchayat = db.Column(db.String(100))
    job_card_no = db.Column(db.String(100))
    reason = db.Column(db.String(200)) # Optional reason

# 3. To Delete Bill / Voucher Format
class DeleteVoucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100)) # Added for operator tracking
    panchayat = db.Column(db.String(100))
    village = db.Column(db.String(100))
    fin_year = db.Column(db.String(20))
    scheme_name = db.Column(db.String(300))
    work_code = db.Column(db.String(100))
    bill_no = db.Column(db.String(50))
    voucher_year = db.Column(db.String(20))
    amount = db.Column(db.String(50))

with app.app_context():
    db.create_all()

# --- Helper: Financial Year List ---
def get_fin_years():
    return [
        "2019-2020", "2020-2021", "2021-2022", 
        "2022-2023", "2023-2024", "2024-2025", "2025-2026"
    ]

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# Form 1: Semi-Skilled
@app.route('/semi-skilled', methods=['GET', 'POST'])
def form_semi():
    if request.method == 'POST':
        try:
            new_entry = SemiSkilled(
                block_name=request.form['block_name'],
                panchayat=request.form['panchayat'],
                fin_year=request.form['fin_year'],
                reg_no=request.form['reg_no'],
                mapped_jc=request.form['mapped_jc'],
                status_jc=request.form['status_jc'],
                bank_name=request.form['bank_name'],
                ac_no=request.form['ac_no'],
                ifsc=request.form['ifsc'],
                wagelist=request.form['wagelist'],
                status_wl=request.form['status_wl'],
                muster_roll=request.form['muster_roll']
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Semi-Skilled Data Saved!', 'success')
            return redirect(url_for('form_semi'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('form_semi.html', years=get_fin_years())

# Form 2: Deleted Jobcard
@app.route('/deleted-jobcard', methods=['GET', 'POST'])
def form_jc():
    if request.method == 'POST':
        try:
            new_entry = DeletedJobcard(
                block_name=request.form['block_name'],
                panchayat=request.form['panchayat'],
                job_card_no=request.form['job_card_no'],
                reason=request.form.get('reason', '')
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Deleted Jobcard Saved!', 'success')
            return redirect(url_for('form_jc'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('form_jc.html')

# Form 3: Delete Voucher
@app.route('/delete-voucher', methods=['GET', 'POST'])
def form_voucher():
    if request.method == 'POST':
        try:
            new_entry = DeleteVoucher(
                block_name=request.form['block_name'],
                panchayat=request.form['panchayat'],
                village=request.form['village'],
                fin_year=request.form['fin_year'],
                scheme_name=request.form['scheme_name'],
                work_code=request.form['work_code'],
                bill_no=request.form['bill_no'],
                voucher_year=request.form['voucher_year'],
                amount=request.form['amount']
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Voucher Delete Request Saved!', 'success')
            return redirect(url_for('form_voucher'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('form_voucher.html', years=get_fin_years())

# Admin Dashboard
@app.route('/admin')
def admin():
    semi_data = SemiSkilled.query.all()
    jc_data = DeletedJobcard.query.all()
    voucher_data = DeleteVoucher.query.all()
    return render_template('admin.html', 
                           semi=semi_data, 
                           jc=jc_data, 
                           voucher=voucher_data)

# Export Function
@app.route('/export/<category>')
def export_data(category):
    output = []
    filename = "data.csv"
    
    if category == 'semi':
        data = SemiSkilled.query.all()
        # Matches user's exact CSV format
        output = [{
            'Sl.no': i+1, 'Block Name': r.block_name, 'Panchayat Name': r.panchayat, 
            'Financial Year': r.fin_year, 'Registration no': r.reg_no, 
            'Mapped With concerned JC No': r.mapped_jc, 'Status of JC': r.status_jc,
            'Bank Name': r.bank_name, 'A/c No': r.ac_no, 'IFSC Code': r.ifsc,
            'Wagelist of concerned Registration': r.wagelist, 
            'Status of wagelist': r.status_wl, 'Muster Roll No': r.muster_roll
        } for i, r in enumerate(data)]
        filename = "Semi_Skilled_Data.csv"

    elif category == 'jc':
        data = DeletedJobcard.query.all()
        output = [{
            'Block': r.block_name, 'PANCHAYAT': r.panchayat, 'JOB CARD NO': r.job_card_no
        } for r in data]
        filename = "Deleted_Jobcards.csv"

    elif category == 'voucher':
        data = DeleteVoucher.query.all()
        output = [{
            'Block': r.block_name, 'PANCHAYAT': r.panchayat, 'VILLAGE': r.village,
            'FINANCIAL YEAR': r.fin_year, 'SCHEME NAME': r.scheme_name,
            'WORK CODE': r.work_code, 'BILL NO.': r.bill_no,
            'FY (VOUCHER ENTRY YEAR)': r.voucher_year, 'AMOUNT': r.amount
        } for r in data]
        filename = "Delete_Voucher_Data.csv"

    df = pd.DataFrame(output)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)