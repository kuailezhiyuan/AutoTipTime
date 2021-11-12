import configUtil
from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from client import getCode, getToken
from flask_apscheduler import APScheduler

app = Flask(__name__)

# 定时任务，导入配置
# APSchedulerJobConfig 就是在 config.py文件中的 类 名称。
app.config.from_object(configUtil.APSchedulerJobConfig)

# 初始化Flask-APScheduler，定时任务
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()



@app.route('/', methods=['POST', 'GET'])
def login():
    configpasswd = configUtil.getPassword()
    if request.method == 'POST':
        passwd = request.form.get("password", '')
        if check_password_hash(configpasswd, passwd):
            resp = make_response(redirect(url_for("home")))
            resp.set_cookie("passwd", passwd, max_age=3600)
            return resp
        else:
            resp = make_response("密码错误")
            resp.delete_cookie("passwd")
            return resp
    else:
        passwd = request.cookies.get('passwd', '')
        if check_password_hash(configpasswd, passwd):
            return redirect(url_for("home"))
        else:
            resp = make_response(render_template('login.html'))
            resp.delete_cookie("passwd")
            return resp


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/getCode', methods=['POST'])
def codeApi():
    phone = request.form.get("phone", '')
    return getCode(phone)


@app.route('/getToken', methods=['POST'])
def tokenApi():
    phone = request.form.get("phone", '')
    code = request.form.get("code", '')
    data = getToken(phone, code)
    if data['errCode'] == 0:
        configUtil.updataConfig({"authorization": data['data']})
    return jsonify(data)


if __name__ == '__main__':
    app.run()
