from flask import Flask, jsonify, redirect, render_template, request, session
from operator import length_hint
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_sqlalchemy import SQLAlchemy  
from flask import redirect, session
from functools import wraps


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db2 = SQLAlchemy(app)

# Check for environment variable
#if not ("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve"):
    # raise RuntimeError("DATABASE_URL is not set")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve")
db = scoped_session(sessionmaker(bind=engine))

busqueda = ""

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def api1(isbn):
    isbn= isbn
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    return response


class Books(db2.Model):
    __tablename__ = "books"
    id = db2.Column(db2.Integer, primary_key=True)
    isbn = db2.Column(db2.String, nullable=False)
    title = db2.Column(db2.String, nullable=False)
    author = db2.Column(db2.String, nullable=False )
    year = db2.Column(db2.String, nullable=False)

    def __repr__(self):
        
        return f"{self.title} {self.author}"

class users(db2.Model):
    __tablename__ = "users"
    id = db2.Column(db2.Integer, primary_key=True)
    username = db2.Column(db2.String, nullable=False)
    hash = db2.Column(db2.String,  nullable=False)

def search(busquedaLibro):
    busquedaLibro = (f"%{busquedaLibro}%")
    search = busquedaLibro = Books.query.filter(or_(Books.year.ilike(busquedaLibro), Books.isbn.ilike(busquedaLibro), 
    Books.title.ilike(busquedaLibro), Books.author.ilike(busquedaLibro)))
    return search


@app.route("/libro2",methods=["GET", "POST"])
@login_required
def libro2():
    if request.method == "POST":
        pass
    else:
        busquedaLibro = request.args.get("busquedaLibro1")
        page_num = 1
        
        print(f"{busquedaLibro} busqueda Libro")
        #result = Books.query.filter(or_(Books.year.like(busquedaLibro), Books.isbn.like(busquedaLibro), 
        #Books.title.like(busquedaLibro), Books.author.like(busquedaLibro))).paginate(per_page=5, page=page_num, error_out=True)
        result = search(busquedaLibro)
        result = result.paginate(per_page=20, page=page_num, error_out=True)
        return render_template("libro.html", employees=result, busquedaLibro=busquedaLibro, page_num=page_num)



@app.route("/Libro/<int:page_num>/<string:isbn>",methods=["GET", "POST"])
@login_required
def libro(page_num,isbn):
    if request.method == "POST":
        busquedaLibro = isbn
        return render_template("paginaDeLibro.html",isbn = busquedaLibro) 
    
    else:
        busquedaLibro = isbn
        lista = []
        for i in busquedaLibro:
            if i == "%":
                pass
            else:
                lista.append(i)
        print(f"{lista}")
        page_num = page_num
        busquedaLibro = "".join(lista)
        print(f"{busquedaLibro} busqueda Libro")
        #result = Books.query.filter(or_(Books.year.like(busquedaLibro), Books.isbn.like(busquedaLibro), 
        #Books.title.like(busquedaLibro), Books.author.like(busquedaLibro))).paginate(per_page=5, page=page_num, error_out=True)
        result = search(busquedaLibro)
        result = result.paginate(per_page=20, page=page_num, error_out=True)
        return render_template("libro.html", employees=result, busquedaLibro=busquedaLibro, page_num=page_num)


@app.route("/",methods=["GET", "POST"])
@login_required
def index():

    busquedaLibro = request.args.get("busquedaLibro") 
    if not busquedaLibro:
        return render_template("index.html")
        
    busquedaLibro = (f"%{busquedaLibro}%")
    
    busqueda = busquedaLibro
    #resultado = db.execute("SELECT * FROM books WHERE isbn ILIKE :busquedaLibro  OR \
        #lower(title) ILIKE lower(:busquedaLibro) OR lower(author) ILIKE lower(:busquedaLibro) OR year ILIKE :busquedaLibro order by year desc", 
            #{"busquedaLibro": busquedaLibro })

    page_num = 1

    # '%' attention to spaces
    # query_sql = """SELECT * FROM books WHERE isbn ILIKE :busquedaLibro  OR 
    #     lower(title) ILIKE lower(:busquedaLibro) OR lower(author) ILIKE lower(:busquedaLibro) 
    #     OR year ILIKE :busquedaLibro order by year desc"""

    # db is sqlalchemy session object
    #resultado = db.execute(text(query_sql), {"busquedaLibro": busquedaLibro}).fetchall()
    #result = Books.query.filter(or_(Books.year.like(busquedaLibro), Books.isbn.like(busquedaLibro), 
    #Books.title.like(busquedaLibro), Books.author.like(busquedaLibro))).paginate(per_page=5, page=page_num, error_out=True)
    #print(f"{resultado} books")
    result = search(busquedaLibro)
    result = result.paginate(per_page=20, page=page_num, error_out=True)
    return render_template("libro.html", employees=result, busquedaLibro=busquedaLibro, page_num=page_num)
    

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # verificamos si el usuario nuevo ingreso en algo en los campos correspondientes
        if not username:
            return render_template("register.html")

        elif not password:
            return render_template("register.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        # print(f"{rows}")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmation = request.form.get("confirmation").strip()

        # verificamos si el usuario nuevo ingreso en algo en los campos correspondientes
        if not username:
            return render_template("register.html")

        elif not password:
            return render_template("register.html")

        elif password != confirmation:
            return render_template("register.html")


        # Verificamos si el nombre del usuario esta disponible
        consulta = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchall()
        print(f"{consulta}")
        
        if len(consulta) != 0:
            print("Ho0la")
            return render_template("register.html")
        
        print("Hola")
        
        # insertamos al nuevo usuario
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash) RETURNING id",
                            {"username": username, "hash": generate_password_hash(password)}).fetchone()

        db.commit()

       # print("XDD")
        # iniciamos session00000
        print(rows[0])
        session["user_id"] = rows[0]
        # print("Hola1")

        return redirect("/")
    else:
       return render_template("register.html")



@app.route("/paginaDeLibro/<string:isbn>", methods=["GET", "POST"])
@login_required
def paginaDeLibro(isbn):
    isbn = isbn
    isbn_api = api1(isbn)
    image = isbn_api["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]

    resultado = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    
    book_id = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchall()
    id_book = book_id[0][0]

    #Extraemos los comentarios y los nombres de los usuarios
    review = db.execute("SELECT users.username, review_average.review_count, review_average.comentario FROM users INNER JOIN review_average ON users.id = review_average.user_id  \
                    WHERE review_average.book_id = :id_book", {"id_book": id_book}).fetchall()
    personas = length_hint(review)

    if request.method == "GET":
        #print(f"{resultado}")
        print("kevinGET")
        return render_template("paginaDeLibro.html", resultado=resultado, review=review, personas=personas, image=image)

    else:
        print("kevinPOST")
        review_count = request.form.get("review_count").strip()
        comentario = request.form.get("comentario").strip()

        if not review_count:
            return render_template("paginaDeLibro.html", resultado=resultado, review=review, personas=personas,  image=image)

        if not comentario:
            return render_template("paginaDeLibro.html", resultado=resultado, review=review, personas=personas,  image=image)
            
        #print(review_count)
        #print(comentario)

        #si ya hizo un comentario
        confirmacion = db.execute("SELECT * FROM review_average WHERE user_id = :user_id AND book_id = :book_id ",
                        {"user_id": session["user_id"], "book_id": id_book}).fetchall()
        

        if len(confirmacion) != 0:
            print("ya comento")
            #rint(f"{length_hint(review)}")
            personas = length_hint(review)
            return render_template("paginaDeLibro.html", resultado=resultado, review=review, personas=personas,  image=image)
        
    
        else:
            db.execute("INSERT INTO review_average (book_id, user_id, review_count, comentario) VALUES  \
                            (:book_id, :user_id, :review_count, :comentario)  RETURNING id",
                            {"book_id": id_book, "user_id": session["user_id"] , "review_count": review_count, "comentario": comentario})

            db.commit()
        #print(confirmacion)
        #print(f"{id_book}")    
        #print(session["user_id"])
        
        #Extraemos los comentarios y los nombres de los usuarios
        review = db.execute("SELECT users.username, review_average.review_count, review_average.comentario FROM users INNER JOIN review_average ON users.id = review_average.user_id  \
                WHERE review_average.book_id = :id_book", {"id_book": id_book}).fetchall()
        #Personas que han interactuado
        personas = length_hint(review)
        print(f"{review}")
        
        return render_template("paginaDeLibro.html", resultado=resultado, review=review, personas=personas,  image=image)
       


@app.route("/api/<string:isbn>", methods=["GET", "POST"])
@login_required
def api(isbn):
    isbn1 = isbn
    isbn1 = api1(isbn1)
    selector = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    # print(isbn)
    lista = []

    for i in selector:
        lista.append(list(i))
    print(f"{lista}")
    title = lista[0][2]
    year = lista[0][4]
    isbn = lista[0][1]
    author = lista[0][3]
    average_score = isbn1["items"][0]["volumeInfo"]["averageRating"]
    review_count = isbn1["items"][0]["volumeInfo"]["ratingsCount"]
    #title = isbn["items"][0]["volumeInfo"]["title"]
    #author  = isbn["items"][0]["volumeInfo"]["authors"]
    #year = isbn["items"][0]["volumeInfo"]["authors"]
    # print(title)
    return jsonify({"author": author, "year": year, "isbn": isbn, "title": title, "average_score": average_score, "review_count": review_count })
