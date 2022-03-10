from itertools import dropwhile
from flask import Flask, request, render_template
from flask import send_file
import RPi.GPIO as GPIO
from time import sleep
import threading
import os
import helper
import detect_baud, check_uart_console, check_default_key, capture_uart_boot

volt_pin = 21
relay_pin = 26
GPIO.setmode(GPIO.BCM) 
GPIO.setup(volt_pin, GPIO.OUT)
FIRM_DIR = "/home/pi/firm"


class MyThread(threading.Thread):
  # overriding constructor
    def __init__(self, i):
# calling parent class constructor
        self.delay = i
        threading.Thread.__init__(self)
    
    def run(self) -> None:
        while 1:
            GPIO.output(volt_pin, GPIO.HIGH)
            sleep(self.delay)
            GPIO.output(volt_pin,GPIO.LOW)
            sleep(self.delay)
            print(self.delay)

    def set_delay(self, d):
        self.delay=d
        
voltage_thread = MyThread(1)
# voltage_thread.start()

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text

@app.route("/spi.html")
def spi():
    return render_template('spi.html')

@app.route("/uart.html")
def uart_handler_ind():
    return render_template('uart.html')

@app.route("/baudrate_detector.html")
def uart_handler_ind1():
    return render_template('baudrate_detector.html')

@app.route("/check_uart_console")
def uart_console():
    baud = 115200
    if check_uart_console.main(baud):
        return "Console Found"
    return "No Console Found"
    
@app.route("/boot_log_analyse")
def boot_log():
    imp = check_default_key.main()
    output = "\n".join(imp)
    return render_template("output_logs.html", data = output)

@app.route("/capture_boot_logs")
def cap_boot():
    sampling_rate = request.args.get("sampling_rate")
    power_cycle = request.args.get("power_cycle_delay")
    baud_rate = request.args.get("baud_rate")
    output=""
    capture_uart_boot.main(baud_rate, sampling_rate, power_cycle)
    with open(capture_uart_boot.output_file, "r") as f:
        for i in f:
            output+=i
    print(output)
    return render_template("output_logs.html", data = output)

@app.route("/detect_baudrate")
def baud_detect():
    sampling_rate = request.args.get("sampling_rate")
    power_cycle_delay = request.args.get("power_cycle_delay")
    print(sampling_rate, power_cycle_delay, "baud detect")
    detect_baud.main(sampling_rate, power_cycle_delay)
    bauds = ""
    with open(detect_baud.output_file, "r") as f:
        for i in f:
            bauds+=i
    print(bauds)
    return render_template("detect_baudrate_result.html", result = bauds)


@app.route("/list_devices")
def list_devices():
    speed = request.args.get("speed", default = '4096', type = str)
    list_output = helper.list_device_call(speed)
    return f"<pre>{list_output}</pre>"


@app.route("/set_volt")
def set_volt():
    return "ok"


@app.route("/download_firm")
def down_firm():
    fname=request.args.get("filename", default="test", type=str)
    print("downloading "+fname)
    return send_file(fname+".bin", as_attachment=True)

@app.route("/dump_firm")
def dump_firm():
    firm_name = request.args.get("filename", default = 'test.bin', type = str)
    return helper.dump_firm_call("8000")

@app.route("/list_firm")
def an_firm():
    firmware_list = os.listdir(FIRM_DIR)
    return " ".join(firmware_list)

@app.route("/analyse_firm")
def analyse_firm():
    filename = request.args.get("file_name")
    # return render_template("output_logs.html", data= "\n".join(helper.binwalk_des(FIRM_DIR+"/"+filename)))
    return render_template("output_logs.html", data= "\n".join(helper.get_strings(FIRM_DIR+"/"+filename)))
    


# @app.route('/volt', methods=['POST'])
# def set_volt():
#     delay = float(request.form['freq'])
#     voltage_thread.set_delay(float(delay))
#     return render_template('my-form.html')
GPIO.output(relay_pin, GPIO.HIGH)
app.run(host='0.0.0.0', port=5000)
