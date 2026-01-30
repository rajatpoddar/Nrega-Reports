import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'nrega_bot_secret_key' # Secret key session ke liye zaroori hai

# --- YAHAN SE CHANGES HAI (Absolute Path Fix) ---

# 1. Pata lagao ki app.py computer me kahan rakhi hai
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Data folder ka pura rasta (path) set karo
data_dir = os.path.join(basedir, 'data')

# 3. Agar folder nahi hai, to wahin banao
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 4. Database ko batao ki file kahan banani hai (Absolute Path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(data_dir, 'nrega_data.db')

# ------------------------------------------------

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models (Same as before) ---
class SemiSkilled(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100))
    panchayat = db.Column(db.String(100))
    fin_year = db.Column(db.String(20))
    work_code = db.Column(db.String(100))
    mason_name = db.Column(db.String(100))
    reg_no = db.Column(db.String(50))
    mapped_jc = db.Column(db.String(50))
    status_jc = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    ac_no = db.Column(db.String(50))
    ifsc = db.Column(db.String(20))
    wagelist = db.Column(db.String(100))
    status_wl = db.Column(db.String(50))
    muster_roll = db.Column(db.String(50))

class DeletedJobcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100))
    panchayat = db.Column(db.String(100))
    job_card_no = db.Column(db.String(100))
    reason = db.Column(db.String(200))

class DeleteVoucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100))
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

# --- Helper Functions ---
def get_fin_years():
    return ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"]

def get_suggestions():
    """Database se unique Block, Panchayat aur Village nikalta hai suggestion ke liye"""
    blocks = set()
    panchayats = set()
    villages = set()

    # Sabhi tables se data collect karein
    for row in db.session.query(SemiSkilled.block_name, SemiSkilled.panchayat).all():
        if row.block_name: blocks.add(row.block_name)
        if row.panchayat: panchayats.add(row.panchayat)

    for row in db.session.query(DeletedJobcard.block_name, DeletedJobcard.panchayat).all():
        if row.block_name: blocks.add(row.block_name)
        if row.panchayat: panchayats.add(row.panchayat)

    for row in db.session.query(DeleteVoucher.block_name, DeleteVoucher.panchayat, DeleteVoucher.village).all():
        if row.block_name: blocks.add(row.block_name)
        if row.panchayat: panchayats.add(row.panchayat)
        if row.village: villages.add(row.village)
    
    return sorted(list(blocks)), sorted(list(panchayats)), sorted(list(villages))

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/semi-skilled', methods=['GET', 'POST'])
def form_semi():
    if request.method == 'POST':
        # 1. Save Data to DB
        new_entry = SemiSkilled(
            block_name=request.form['block_name'],
            panchayat=request.form['panchayat'],
            fin_year=request.form['fin_year'],
            work_code=request.form['work_code'],
            mason_name=request.form['mason_name'],
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
        
        # 2. Save location to Session for next entry
        session['last_block'] = request.form['block_name']
        session['last_panchayat'] = request.form['panchayat']
        
        flash('Semi-Skilled Data Saved!', 'success')
        return redirect(url_for('form_semi'))

    # Load suggestions and last saved values
    blocks, panchayats, _ = get_suggestions()
    return render_template('form_semi.html', years=get_fin_years(), blocks=blocks, panchayats=panchayats)

# --- DELETE ROUTE ---
@app.route('/delete/<category>/<int:id>')
def delete_item(category, id):
    try:
        if category == 'semi':
            item = SemiSkilled.query.get_or_404(id)
        elif category == 'jc':
            item = DeletedJobcard.query.get_or_404(id)
        elif category == 'voucher':
            item = DeleteVoucher.query.get_or_404(id)
        
        db.session.delete(item)
        db.session.commit()
        flash('Entry Deleted Successfully!', 'warning')
    except Exception as e:
        flash(f'Error deleting: {e}', 'danger')
    
    return redirect(url_for('admin'))

# --- EDIT ROUTE ---
@app.route('/edit/<category>/<int:id>', methods=['GET', 'POST'])
def edit_item(category, id):
    # Data fetch karein
    if category == 'semi':
        item = SemiSkilled.query.get_or_404(id)
    elif category == 'jc':
        item = DeletedJobcard.query.get_or_404(id)
    elif category == 'voucher':
        item = DeleteVoucher.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Form se data lekar update karein
            item.block_name = request.form['block_name']
            item.panchayat = request.form['panchayat']
            
            if category == 'semi':
                item.fin_year = request.form['fin_year']
                item.work_code = request.form['work_code']
                item.mason_name = request.form['mason_name']
                item.reg_no = request.form['reg_no']
                item.mapped_jc = request.form['mapped_jc']
                item.status_jc = request.form['status_jc']
                item.bank_name = request.form['bank_name']
                item.ac_no = request.form['ac_no']
                item.ifsc = request.form['ifsc']
                item.wagelist = request.form['wagelist']
                item.status_wl = request.form['status_wl']
                item.muster_roll = request.form['muster_roll']

            elif category == 'jc':
                item.job_card_no = request.form['job_card_no']
                item.reason = request.form['reason']

            elif category == 'voucher':
                item.village = request.form['village']
                item.fin_year = request.form['fin_year']
                item.scheme_name = request.form['scheme_name']
                item.work_code = request.form['work_code']
                item.bill_no = request.form['bill_no']
                item.voucher_year = request.form['voucher_year']
                item.amount = request.form['amount']

            db.session.commit()
            flash('Entry Updated Successfully!', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f'Error updating: {e}', 'danger')

    return render_template('edit.html', item=item, category=category, years=get_fin_years())

@app.route('/deleted-jobcard', methods=['GET', 'POST'])
def form_jc():
    if request.method == 'POST':
        new_entry = DeletedJobcard(
            block_name=request.form['block_name'],
            panchayat=request.form['panchayat'],
            job_card_no=request.form['job_card_no'],
            reason=request.form.get('reason', '')
        )
        db.session.add(new_entry)
        db.session.commit()

        # Save session
        session['last_block'] = request.form['block_name']
        session['last_panchayat'] = request.form['panchayat']

        flash('Deleted Jobcard Saved!', 'success')
        return redirect(url_for('form_jc'))

    blocks, panchayats, _ = get_suggestions()
    return render_template('form_jc.html', blocks=blocks, panchayats=panchayats)

@app.route('/delete-voucher', methods=['GET', 'POST'])
def form_voucher():
    if request.method == 'POST':
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

        # Save session
        session['last_block'] = request.form['block_name']
        session['last_panchayat'] = request.form['panchayat']
        session['last_village'] = request.form['village']

        flash('Voucher Delete Request Saved!', 'success')
        return redirect(url_for('form_voucher'))

    blocks, panchayats, villages = get_suggestions()
    return render_template('form_voucher.html', years=get_fin_years(), blocks=blocks, panchayats=panchayats, villages=villages)

@app.route('/admin', methods=['GET'])
def admin():
    # 1. Filters Get karna (URL se)
    block_filter = request.args.get('block_name')
    panchayat_filter = request.args.get('panchayat')

    # 2. Queries Banana
    query_semi = SemiSkilled.query
    query_jc = DeletedJobcard.query
    query_voucher = DeleteVoucher.query

    # 3. Filters Apply karna
    if block_filter:
        query_semi = query_semi.filter_by(block_name=block_filter)
        query_jc = query_jc.filter_by(block_name=block_filter)
        query_voucher = query_voucher.filter_by(block_name=block_filter)
    
    if panchayat_filter:
        query_semi = query_semi.filter_by(panchayat=panchayat_filter)
        query_jc = query_jc.filter_by(panchayat=panchayat_filter)
        query_voucher = query_voucher.filter_by(panchayat=panchayat_filter)

    # 4. Data Fetch karna
    semi_data = query_semi.all()
    jc_data = query_jc.all()
    voucher_data = query_voucher.all()

    # 5. Dropdown ke liye unique list (Suggestions wale function se)
    blocks, panchayats, _ = get_suggestions()

    return render_template('admin.html', 
                           semi=semi_data, 
                           jc=jc_data, 
                           voucher=voucher_data,
                           all_blocks=blocks,
                           all_panchayats=panchayats,
                           sel_block=block_filter,
                           sel_panchayat=panchayat_filter)

@app.route('/export/<category>')
def export_data(category):
    output = []
    filename = "data.csv"
    
    if category == 'semi':
        data = SemiSkilled.query.all()
        output = [{'Sl.no': i+1, 'Block Name': r.block_name, 'Panchayat Name': r.panchayat, 'Financial Year': r.fin_year, 'Work Code': r.work_code, 'Mason Name': r.mason_name, 'Registration no': r.reg_no, 'Mapped With concerned JC No': r.mapped_jc, 'Status of JC': r.status_jc, 'Bank Name': r.bank_name, 'A/c No': r.ac_no, 'IFSC Code': r.ifsc, 'Wagelist of concerned Registration': r.wagelist, 'Status of wagelist': r.status_wl, 'Muster Roll No': r.muster_roll} for i, r in enumerate(data)]
        filename = "Semi_Skilled_Data.csv"
    elif category == 'jc':
        data = DeletedJobcard.query.all()
        output = [{'Block': r.block_name, 'PANCHAYAT': r.panchayat, 'JOB CARD NO': r.job_card_no} for r in data]
        filename = "Deleted_Jobcards.csv"
    elif category == 'voucher':
        data = DeleteVoucher.query.all()
        output = [{'Block': r.block_name, 'PANCHAYAT': r.panchayat, 'VILLAGE': r.village, 'FINANCIAL YEAR': r.fin_year, 'SCHEME NAME': r.scheme_name, 'WORK CODE': r.work_code, 'BILL NO.': r.bill_no, 'FY (VOUCHER ENTRY YEAR)': r.voucher_year, 'AMOUNT': r.amount} for r in data]
        filename = "Delete_Voucher_Data.csv"

    df = pd.DataFrame(output)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)