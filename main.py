from itertools import dropwhile
from flask import Flask, request, render_template
from flask import send_file
import RPi.GPIO as GPIO
from time import sleep
import threading
import os
import helper
import detect_baud, check_uart_console, check_default_key, capture_uart_boot
from power_module import PowerMod

switching_pin = 19
volt_pin = 20
relay_pin = 21


GPIO.setmode(GPIO.BCM) 
GPIO.setup(volt_pin, GPIO.OUT)
FIRM_DIR = "extracted_firm"
LOG_DIR = "uart_logs"
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, GPIO.HIGH)
power_thread = PowerMod(channel_pin=26, switching_pin=6)
power_thread.start()

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route("/spi.html")
def spi():
    return render_template('spi.html')

@app.route("/uart.html")
def uart_handler_ind():
    return render_template('uart.html')

@app.route("/voltage-module.html")
def volt_glitcher_hand():
    return render_template('voltage-module.html')

@app.route("/list_firm.html")
def an_firm():
    firmware_list = os.listdir(FIRM_DIR)
    return render_template("list_of_firm.html", files = firmware_list)

@app.route("/list_logs.html")
def uart_log():
    firmware_list = os.listdir(LOG_DIR)
    return render_template("list_of_logs.html", files = firmware_list)

@app.route("/set_volt")
def volt_glitch():
    freq = request.args.get("freq")
    channel = request.args.get("channel")
    print(f"setting frq {freq} delay {channel}")
    power_thread.set_delay(int(freq))
    power_thread.set_channel(int(channel))
    return "OK"

@app.route("/check_uart_console")
def uart_console():
    baud = 115200
    if check_uart_console.main(baud):
        return "Console Found"
    return "No Console Found"
    
@app.route("/boot_log_analyse")
def boot_log():
    file_name = request.args.get("file_name", default=None)
    if file_name is not None:
        check_default_key.output_file = "uart_logs/"+file_name
    imp = check_default_key.main()
    imp_output = "\n".join(imp)
    output=""
    with open("uart_logs/"+file_name, "r") as f:
        for i in f:
            output+=i
    return render_template("string_analysis.html", data = output, invoked_data=imp_output)

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

@app.route("/show_raw_boot_logs")
def cap_boot_show():
    log_name = request.args.get("log_name", default=None)
    output=""
    if log_name is None:
        log_name = "uart_boot_log"
    with open("uart_logs/"+log_name, "r") as f:
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



@app.route("/download_firm")
def down_firm():
    fname=request.args.get("filename", default="test", type=str)
    print("downloading "+fname)
    return send_file(FIRM_DIR+"/"+fname+".bin", as_attachment=True)

@app.route("/dump_firm")
def dump_firm():
    firm_name = request.args.get("filename", default = 'test.bin', type = str)
    return helper.dump_firm_call("8000", firm_name)



@app.route("/get_strings")
def analyse_firm():
    filename = request.args.get("file_name")
    return render_template("string_analysis.html", invoked_data="none", data= "\n".join(helper.get_strings(FIRM_DIR+"/"+filename)))
    
@app.route("/get_binwalk")
def analyse_firm_binwalk():
    filename = request.args.get("file_name")
    output = helper.binwalk_des(FIRM_DIR+"/"+filename)
    print(output)
    return render_template("bin_analysis.html", info= output)


app.run(host='0.0.0.0', port=5000)
