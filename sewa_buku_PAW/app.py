from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_mysqldb import MySQL
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField
from datetime import datetime
import MySQLdb
from models import MPengguna

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'sewa_buku'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Homepage
@app.route('/')
def index():
    return render_template('home.html')

# Member
@app.route('/members')
def members():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM members")
    members = cur.fetchall()

    if result > 0:
        return render_template('member.html', members=members)
    else:
        msg = 'Member tidak ditemukan'
        return render_template('member.html', warning=msg)
    cur.close()

# Melihat detail member by ID
@app.route('/member/<string:id>')
def viewMember(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM members WHERE id=%s", [id])
    member = cur.fetchone()

    if result > 0:
        return render_template('view_member_details.html', member=member)
    else:
        msg = 'Member tidak ditemukan'
        return render_template('view_member_details.html', warning=msg)
    cur.close()

# Mendefinisikan Form tambah member
class AddMember(Form):
    name = StringField('Nama', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])

# Tambah Member
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    form = AddMember(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        
        flash("Member berhasil ditambahkan", "success")
        return redirect(url_for('members'))
    return render_template('add_member.html', form=form)

# Edit Member by ID
@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
def edit_member(id):
    form = AddMember(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE members SET name=%s, email=%s WHERE id=%s", (name, email, id))
        mysql.connection.commit()
        cur.close()

        flash("Member Berhasil di update", "success")
        return redirect(url_for('members'))

    # Mengambil nilai dari member yang dipilih
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT name,email FROM members WHERE id=%s", [id])
    member = cur2.fetchone()
    return render_template('edit_member.html', form=form, member=member)

# Hapus Member by ID
@app.route('/delete_member/<string:id>', methods=['POST'])
def delete_member(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM members WHERE id=%s", [id])
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        flash("Member gagal dihapus", "danger")
        flash(str(e), "danger")
        return redirect(url_for('members'))
    finally:
        cur.close()

    flash("Member berhasil dihapus", "success")
    return redirect(url_for('members'))

# Buku
@app.route('/books')
def books():
    cur = mysql.connection.cursor()
    result = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books")
    books = cur.fetchall()

    if result > 0:
        return render_template('books.html', books=books)
    else:
        msg = 'Buku tidak ditemukan'
        return render_template('books.html', warning=msg)
    cur.close()

# Melihat detail buku by ID
@app.route('/book/<string:id>')
def viewBook(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    if result > 0:
        return render_template('view_book_details.html', book=book)
    else:
        msg = 'Buku tidak tersedia'
        return render_template('view_book_details.html', warning=msg)
    cur.close()

# Mendefiniskan form tambah buku
class AddBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])
    average_rating = FloatField(
        'Average Rating', [validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1, max=3)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField(
        'No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField(
        'No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField(
        'Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField(
        'Total No. of Books', [validators.NumberRange(min=1)])

# tambah Buku
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = AddBook(request.form)

    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM books WHERE id=%s", [form.id.data])
        book = cur.fetchone()
        if(book):
            error = 'Buku dengan id tersebut sudah ada'
            return render_template('add_book.html', form=form, error=error)
        cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [form.id.data,form.title.data,form.author.data,form.average_rating.data,form.isbn.data,form.isbn13.data,form.language_code.data,form.num_pages.data,form.ratings_count.data,form.text_reviews_count.data,form.publication_date.data,form.publisher.data,form.total_quantity.data,form.total_quantity.data])
        mysql.connection.commit()
        cur.close()

        flash("Buku berhasil ditambah", "success")
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)

# Edit Buku by ID
@app.route('/edit_book/<string:id>', methods=['GET', 'POST'])
def edit_book(id):
    form = AddBook(request.form)
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    if request.method == 'POST' and form.validate():
        if(form.id.data != id):
            cur.execute("SELECT id FROM books WHERE id=%s", [form.id.data])
            book = cur.fetchone()
            if(book):
                error = 'Buku dengan id tersebut sudah ada'
                return render_template('edit_book.html', form=form, error=error, book=form.data)

        # menghitung jml buku yg tersedia (untuk disewa)
        available_quantity = book['available_quantity'] + \
            (form.total_quantity.data - book['total_quantity'])
        cur.execute("UPDATE books SET id=%s,title=%s,author=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s,total_quantity=%s,available_quantity=%s WHERE id=%s", [form.id.data,form.title.data,form.author.data,form.average_rating.data,form.isbn.data,form.isbn13.data,form.language_code.data,form.num_pages.data,form.ratings_count.data,form.text_reviews_count.data,form.publication_date.data,form.publisher.data,form.total_quantity.data,available_quantity,id])
        mysql.connection.commit()
        cur.close()
        flash("Buku berhasil diupdate", "success")
        return redirect(url_for('books'))
    return render_template('edit_book.html', form=form, book=book)

# Hapus buku by ID
@app.route('/delete_book/<string:id>', methods=['POST'])
def delete_book(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM books WHERE id=%s", [id])
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        flash("Buku gagal dihapus", "danger")
        flash(str(e), "danger")
        return redirect(url_for('books'))
    finally:
        cur.close()
    flash("Buku berhasil dihapus", "success")
    return redirect(url_for('books'))

# Transaksi
@app.route('/transactions')
def transactions():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM transactions")
    transactions = cur.fetchall()

    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"

    if result > 0:
        return render_template('transaksi2.html', transactions=transactions)
    else:
        msg = 'Transaksi tidak ditemukan'
        return render_template('transaksi2.html', warning=msg)
    cur.close()

# mendefinisikan form sewa buku
class SewaBuku(Form):
    book_id = SelectField('Judul Buku', choices=[], coerce=int)
    member_id = SelectField('Nama Member', choices=[], coerce=int)
    per_day_fee = FloatField('Biaya Sewa /hari', [
                            validators.NumberRange(min=1)])

# sewa buku
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    form = SewaBuku(request.form)
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, title FROM books")
    books = cur.fetchall()
    book_ids_list = []
    for book in books:
        t = (book['id'], book['title'])
        book_ids_list.append(t)

    cur.execute("SELECT id, name FROM members")
    members = cur.fetchall()
    member_ids_list = []
    for member in members:
        t = (member['id'], member['name'])
        member_ids_list.append(t)
    form.book_id.choices = book_ids_list
    form.member_id.choices = member_ids_list

    if request.method == 'POST' and form.validate():
        cur.execute("SELECT available_quantity FROM books WHERE id=%s", [
                    form.book_id.data])
        result = cur.fetchone()
        available_quantity = result['available_quantity']

        if(available_quantity < 1):
            error = 'Buku tidak tersedia'
            return render_template('sewa_buku.html', form=form, error=error)

        cur.execute("INSERT INTO transactions (book_id,member_id,per_day_fee) VALUES (%s, %s, %s)", [form.book_id.data,form.member_id.data,form.per_day_fee.data,])

        # Update jumlah buku yg tersedia, untuk disewa
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity-1, rented_count=rented_count+1 WHERE id=%s", [form.book_id.data])
        mysql.connection.commit()
        cur.close()
        flash("Buku berhasil disewa", "success")
        return redirect(url_for('transactions'))
    return render_template('sewa_buku.html', form=form)

# mendefiniskan form pengembalian buku ( jumlah uang bayar)
class ReturnBook(Form):
    amount_paid = FloatField('Jumlah Uang Bayar:', [validators.NumberRange(min=0)])

# mengembalikan buku by Transaction ID
@app.route('/return_book/<string:transaction_id>', methods=['GET', 'POST'])
def return_book(transaction_id):
    form = ReturnBook(request.form)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM transactions WHERE id=%s", [transaction_id])
    transaction = cur.fetchone()

    # menghitung total biaya sewa ( /hari )
    date = datetime.now()
    difference = date - transaction['borrowed_on']
    difference = difference.days
    total_charge = difference * transaction['per_day_fee']

    if request.method == 'POST' and form.validate():
        cur.execute("SELECT amount_spent FROM members WHERE id=%s", [
                    transaction['member_id']])
        result = cur.fetchone()

        amount_spent = result['amount_spent']
        # Update tgl kembali, total tagihan, jumlah bayar utk transaksi
        cur.execute("UPDATE transactions SET returned_on=%s,total_charge=%s,amount_paid=%s WHERE id=%s", [date,total_charge,form.amount_paid.data,transaction_id])

        # Update  total pengeluaran member
        cur.execute("UPDATE members SET amount_spent=%s WHERE id=%s", [amount_spent+form.amount_paid.data,transaction['member_id']])

        # Update jumlah buku yg tersedia
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity+1 WHERE id=%s", [transaction['book_id']])
        mysql.connection.commit()
        cur.close()
        flash("Buku berhasil dikembalikan", "success")
        return redirect(url_for('transactions'))
    return render_template('return_book.html', form=form, total_charge=total_charge, difference=difference, transaction=transaction)
''''
@app.route('/logout')
def logout():
    session.pop('username', '')
    return redirect(url_for('index'))
'''
if __name__ == '__main__':
    app.secret_key = "secret"
    app.run(debug=True)
