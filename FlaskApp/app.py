from flask import Flask, render_template, json, request, redirect, session, jsonify
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'Why would I tell you my secret key?'


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1amanda1'
app.config['MYSQL_DATABASE_DB'] = 'Prtracker'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def main():
    return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')



@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
                        
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()



@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall() 

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong email or password.')
        else:
            return render_template('error.html',error='Wrong email or password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html') 
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/showAddPr')
def showAddPr():
    return render_template('addpr.html')


@app.route('/addPr',methods=['POST'])
def addPr():

    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _amount = request.form['inputAmount']
            _date_ach = request.form['inputDate_Ach']
            _description = request.form['inputDescription']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addPr',(_title,_amount,_date_ach,_description,_user))
            data = cursor.fetchall() 

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred')
        else:
            return render_template('error.html',error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getPr')
def getPr():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetPrByUser',(_user,))
            prs = cursor.fetchall()
            
            prs_dict = []
            for pr in prs:
                pr_dict = {
                    'Id': pr[0],
                    'Title': pr[1],
                    'Amount': pr[2],
                    'Date_Ach': pr[3],
                    'Description': pr[4],
                    'Date': pr[6]}
                prs_dict.append(pr_dict)
            
            return json.dumps(prs_dict)

        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/getPrById', methods=['POST'])
def getPrById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetPrById',(_id, _user))
            result = cursor.fetchall()

            pr = []
            pr.append({'Id': result[0][0], 'Title':result[0][1],'Amount':result[0][2],'Date_Ach': result[0][3], 'Description':result[0][4]})

            return json.dumps(pr)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))


@app.route('/updatePr', methods=['POST'])
def updatePr():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _amount = request.form['amount']
            _date_ach = request.form['date_ach']
            _description = request.form['description']
            _pr_id = request.form['id']

            conn= mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_updatePr',(_title,_amount,_date_ach,_description,_pr_id,_user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'ERROR'})
    except Exception as e:
        return json.dumps({'status': 'Unauthorized Access'})
    finally:
        cursor.close()
        conn.close()

@app.route('/deletePr',methods=['POST'])
def deletePr():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deletePr',(_id,_user))
            result = cursor.fetchall()

            if len(result) is 0:
                conn.commit()
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'An error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)