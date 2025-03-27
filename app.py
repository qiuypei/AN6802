from flask import Flask,request,render_template

app = Flask(__name__)

@app.route("/",methods=["POST","GET"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["POST","GET"])
def main():
    user_name = request.form.get("q")
    return(render_template("main.html"))

@app.route("/ethical_test",methods=["POST","GET"])
def ethical_test():
    return(render_template("ethical_test.html"))

if __name__ == "__main__":
    app.run()