from flask import Flask,redirect,url_for,render_template,request,session,flash
from datetime import timedelta
import sqlite3
app=Flask(__name__)
app.secret_key="heljasdlfkjasdf"
app.permanent_session_lifetime=timedelta(days=1)
@app.route("/")
def home():
    return redirect(url_for("login"))
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":#invoked when form is already filled
        email=request.form['email']#get value submitted in the form for the input field with value="nm"
        password=request.form['pwd']
        conn = sqlite3.connect('data.db')
        cr=conn.cursor()
        cr.execute("select * from users where mailid= (?)",(email,) )
        result=cr.fetchall()
        print(result)
        print(password)
        if result[0][1]==password:
            print(result)
            print(password)
            print("passwords match")
            session.permanent=True
            session["email"]=email
            return redirect("user")
        else:
            flash("invlaid password")
            return redirect(url_for("login"))
    else:
        if "email" in session:#here we check if the user is logged in ..
            return redirect("user")#if we try to login when we are already logged in, we redirect to user page
        else:#user is not logged in
            return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email=request.form['email']
        password=request.form['pwd']
        confirm_pwd=request.form['confirm_pwd']
        if confirm_pwd!=password:
            return "passwords don't match"
        else:
            conn = sqlite3.connect('data.db')
            cr=conn.cursor()
            cr.execute("select * from users where mailid= (?)",(email,) )
            result=cr.fetchall()
            if len(result)==0:
                cr.execute("insert into users(mailid,password) values(?,?)",(email,password) )
                conn.commit()
                flash('your account has been created ',category='info')
                if "email" in session:
                    session.pop("email",None)
                return redirect(url_for("login"))
            else:
                flash('emailid already exists',category='info')
                return redirect(url_for("signup"))

    else:
        return render_template('signup.html')
@app.route("/user")
def user():
    if "email" in session:#check if the key "user" exists in session(think of this as a dictionary).ie. here we check if the user is already logged in
        email=session["email"]
        conn = sqlite3.connect('data.db')
        cr=conn.cursor()
        cr.execute("select day,content from dairy where email= (?) order by day desc",(email,) )
        result=cr.fetchall()
        if len(result)==0:
            flash("you haven't written anything..you can write something here...")
            return redirect(url_for("writedairy"))
        else:
            return render_template("userpage.html",notes=result)

    else:#user haven't logged in yet or user have left the browser. so we have to redirect to login page 
        return redirect(url_for("login"))
@app.route("/writedairy",methods=["POST","GET"])
def writedairy():
    if request.method == "POST":
        print("post condition success")
        if "email" in session:
            email=session["email"]
            date=request.form["date"]
            content=request.form["content"]
            print(email,date,content)
            if date=='':
                flash("please enter the date...")
                return render_template("writedairy.html")
            conn = sqlite3.connect('data.db')
            cr=conn.cursor()
            cr.execute("insert into dairy(email,day,content) values (?,?,?)",(email,date,content,))
            conn.commit()
            conn.close()
            return redirect(url_for("user"))
        else:
            email=session["email"]
            return redirect(url_for("login"))
    else:
        print("post condition failed")
        if "email" in session:
            return render_template('writedairy.html')
        else:
            return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("email",None)#removes the key value pair with key "user".This is done to clear the data
    return redirect(url_for("login"))#once we logout , we redirect to login page with GET method
@app.route("/delete/<date>")
def delete(date):
    if "email" in session:
        email=session["email"]
        conn = sqlite3.connect('data.db')
        cr=conn.cursor()
        cr.execute("delete from dairy where email=? and day=?",(email,date,))
        conn.commit()
        conn.close()
        return redirect(url_for("user"))
    else:
        return redirect(url_for("login"))
@app.route("/update/<date>",methods=["GET","POST"])
def update(date):
    if request.method == "GET":
        email=session["email"]
        conn = sqlite3.connect('data.db')
        cr=conn.cursor()
        cr.execute("select content from dairy where email=? and day=?",(email,date,))
        res=cr.fetchall()
        conn.close()
        return render_template("updatedairy.html",msg=res[0][0],date=date)
    else:
        email=session["email"]
        conn = sqlite3.connect('data.db')
        content=request.form["content"]
        print(content)
        cr=conn.cursor()
        cr.execute("update dairy set content=? where email=? and day=? ",(content,email,date,))
        conn.commit()
        conn.close()
        return redirect(url_for("user"))
if __name__=='__main__':
    app.run(debug=True)