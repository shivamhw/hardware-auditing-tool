import subprocess
import binwalk

def list_device_call(speed):
    process = subprocess.Popen(["bash", "list_flash.sh", speed], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.wait()
    result = process.communicate()
    if result[0] == "error":
        return '{"error" : "error in probing"}'
    size = result[0]
    return size

def dump_firm_call(speed):
    print("starting dumping")
    process = subprocess.Popen(["bash", "dump_flash.sh", speed], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.wait()
    result = process.communicate()
    if result[0] == "failed":
        return '{"error" : "error in dumping"}'
    return '{"data" : "success"}'

def get_strings(filepath):
    print("starting strings", filepath)
    process = subprocess.Popen(["/usr/bin/strings", filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = process.communicate()
    # process.wait()
    return result

def binwalk_des(filename="test.bin"):
    output = {"summary" : [], "detailed" : []}
    rt = binwalk.scan(filename, '--signature', '-q')
    for result in rt[0].results:
        print(result.offset, result.description)
        output["summary"].append(f"{result.offset} | {result.description}")
    rt = binwalk.scan(filename, '--signature', '-q', '-M', '-e')
    for result in rt[0].results:
        print(result.offset, result.description)
        output["detailed"].append(f"{result.offset} | {result.description}")
    return output


