from flask import Flask,request,render_template
import sqlite3
import datetime
import google.generativeai as genai
import os
import wikipedia
import time, requests

api = os.getenv("makersuite")
model = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=api)

TOKEN = '7592004244:AAHzhUteT37T-PSupqKQmwsXF5kD0StjwgY'
BASE_URL = f"http://api.telegram.org/bot{TOKEN}/"
last_processed_id = 0

app = Flask(__name__)

flag = 1

@app.route("/",methods=["POST","GET"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["POST","GET"])
def main():
    global flag
    if flag == 1:
        t = datetime.datetime.now()
        user_name = request.form.get("q")
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("insert into user (name, timestamp) values (?,?)", (user_name, t))
        conn.commit()
        c.close()
        conn.close
        flag = 0
    return(render_template("main.html"))

@app.route("/foodexp",methods=["POST","GET"])
def foodexp():
    return(render_template("foodexp.html"))

@app.route("/foodexp1",methods=["POST","GET"])
def foodexp1():
    return(render_template("foodexp1.html"))

@app.route("/foodexp2",methods=["POST","GET"])
def foodexp2():
    return(render_template("foodexp2.html"))

@app.route("/foodexp_pred",methods=["POST","GET"])
def foodexp_pred():
    q = float(request.form.get("q"))
    return(render_template("foodexp_pred.html",r=(q*0.4851)+147.4))

@app.route("/ethical_test",methods=["POST","GET"])
def ethical_test():
    return(render_template("ethical_test.html"))

@app.route("/test_result",methods=["POST","GET"])
def test_result():
    answer = request.form.get("answer")
    if answer=="false":
        return(render_template("pass.html"))
    elif answer=="true":
        return(render_template("fail.html"))

@app.route("/FAQ",methods=["POST","GET"])
def FAQ():
    return(render_template("FAQ.html"))

@app.route("/FAQ1",methods=["POST","GET"])
def FAQ1():
    r = model.generate_content("Factors for Profit")
    return(render_template("FAQ1.html",r=r.candidates[0].content.parts[0]))

@app.route("/FAQinput",methods=["POST","GET"])
def FAQinput():
    q = request.form.get("q")
    r = wikipedia.summary(q)
    return(render_template("FAQinput.html",r=r))

@app.route("/userLog",methods=["POST","GET"])
def userLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from user")
    r = ""
    for row in c:
        r = r + str(row) + "\n"
    print(r)
    c.close()
    conn.close
    return(render_template("userLog.html",r=r))

@app.route("/deleteLog",methods=["POST","GET"])
def deleteLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from user")
    conn.commit()
    c.close()
    conn.close
    return(render_template("deleteLog.html"))

@app.route('/telegram', methods=['GET', 'POST'])
def telegram_intermediate():
    return render_template("telegram_start.html")

@app.route('/start_telegram_chat', methods=['GET', 'POST'])
def start_telegram_chat():
    global last_processed_id
    
    response = requests.get(BASE_URL + 'getUpdates')
    data = response.json()
    
    try:
        last_message = data['result'][-1]['message']
        chat_id = last_message['chat']['id']
        last_processed_id = last_message['message_id']
        
        welcome_text = "Welcome to the food expenditure prediction. Please enter your income:"
        requests.get(BASE_URL + f'sendMessage?chat_id={chat_id}&text={welcome_text}')
        
        while True:
            time.sleep(5)  
            response = requests.get(BASE_URL + 'getUpdates')
            data = response.json()
            
            if not data.get('result'):
                continue
                
            last_message = data['result'][-1]['message']
            current_msg_id = last_message['message_id']
            
            if current_msg_id > last_processed_id:
                last_processed_id = current_msg_id
                text = last_message.get('text', '')
                
                try:
                    income = float(text)
                    prediction = round((income * 0.4851) + 147.4, 2)
                    reply = f"Your predicted food expenditure is {prediction}\n\nType another number to predict again, or 'exit' to end."
                    requests.get(BASE_URL + f'sendMessage?chat_id={chat_id}&text={reply}')
                except ValueError:
                    if text.lower() == 'exit':
                        requests.get(BASE_URL + f'sendMessage?chat_id={chat_id}&text="Goodbye!"')
                        break
                    reply = "Invalid input. Please enter a valid number for income:"
                    requests.get(BASE_URL + f'sendMessage?chat_id={chat_id}&text={reply}')
    
    except (KeyError, IndexError) as e:
        return f"No valid message found. Error: {str(e)}"
    
    return render_template("telegram.html")

if __name__ == '__main__':
    app.run(debug=True)