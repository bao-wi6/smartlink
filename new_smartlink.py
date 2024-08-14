from flask import Flask, request, jsonify
import json
import requests

import logging

logging.basicConfig(level=logging.DEBUG)

logging.info("Starting the Flask app")

app = Flask(__name__)

@app.route('/apiv3/deviceManagement/lorawan-downlinks/smart/<device_id>/', methods=['POST'])
def downlink_smart(device_id):
    data = request.get_data(as_text=True)
    output = parse_data(data)
    
    # Get the fport from the incoming data
    try:
        data_detail = json.loads(data)
        fport = int(data_detail['values'][0][0])
    except (ValueError, IndexError) as err:
        return jsonify({"error": "Invalid request structure"}), 404
    
    # Get the base_URL from the environment or configuration
    base_url = "api.wiotys.net"
    
    if not base_url:
        return jsonify({"error": "Base URL is missing"}), 400
    
    wiotys_url = f'https://{base_url}/apiv3/deviceManagement/lorawan-downlinks'
    
    # Use the access token from the incoming request
    access_token = request.headers.get("Authorization")
    if not access_token:
        return jsonify({"error": "Access token missing in the request"}), 401
    
    # Prepare the payload
    payload = {
        "payload": output,
        "port": fport,
        "lorawanPrivate": f"/lorawan-privates/{device_id}"
    }
    
    # Post the payload to Wiotys_URL
    headers = {
        'Authorization': access_token,  # Directly pass the token from the incoming request
        'Content-Type': 'application/ld+json',
    }
    
    response = requests.post(wiotys_url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return f"Payload {output} is created and sent successfully. Request sent: \n{response.text}", 200
    else:
        return f"Problem when sending: {response.text}", response.status_code


def format_message(ref, value):

    service=ref.split('|', 4)
    if service[2] == 'IKeepAlive':
        output = '02' + "%0.2X" % int(value)
        
    elif service[2] == 'IOpenWindowDetection1degree':
        data_detail=value.split('|', 4)
        enabled = data_detail[0]
        closeTime = int(int(data_detail[1])/5)
        delta = int(data_detail[3])
        motorPosition = int(data_detail[2])
        motorPositionFirstPart = motorPosition & 0xff
        motorPositionSecondPart = (motorPosition >> 8) & 0xff
        output = "06" + "%0.2X" % int(enabled) +  "%0.2X" % closeTime +  "%0.2X" % motorPositionFirstPart  +  "%0.2X" % ((motorPositionSecondPart << 4) | delta) 

    elif service[2] == 'IOpenWindowDetection0_1degree':
        data_detail=value.split('|', 3)
        enabledValue = data_detail[0]
        duration = int(int(data_detail[1])/5)
        delta = int(float(data_detail[2]) * 10)
        output = "45" + "%0.2X" % int(enabledValue) +  "%0.2X" % duration +  "%0.2X" % delta

    elif service[2] == 'IChildLock':
        output = '07' + "%0.2X" % int(value)

    elif service[2] == 'IChildLockBehavior':
        output = '35' + "%0.2X" % int(value)

    elif service[2] == 'ITemperatureRange':
        data_detail=value.split('|', 2)
        output = "08" + "%0.2X" % int(data_detail[0]) +  "%0.2X" % int(data_detail[1])

    elif service[2] == 'IOperationMode':
        output = '0D' + "%0.2X" % int(value)

    elif service[2] == 'ITargetTemperature':
        output = '0E' + "%0.2X" % int(value)

    elif service[2] == 'IMotorPosition':
        motorPosition = int(value)
        motorPositionFirstPart = motorPosition & 0xff
        motorPositionSecondPart = (motorPosition >> 8) & 0xff
        output = "2D" + "%0.2X" % motorPositionSecondPart +  "%0.2X" % motorPositionFirstPart

    return output


def parse_data(data):
    print("Data parsed OK")

    try:
        data_detail = json.loads(data)
    except ValueError as err:
        return "Invalid json", 404

    # find header that shall contain fport, type, ref and value
    if not "fport" in data_detail['columns']:
        return "Invalid request. fport not specified in columns structure", 404

    if not "type" in data_detail['columns']:
        return "Invalid request. type not specified in columns structure", 404

    if not "ref" in data_detail['columns']:
        return "Invalid request. ref not specified in columns structure", 404

    if not "value" in data_detail['columns']:
        return "Invalid request. value not specified in columns structure", 404

    output=""

    #parse elements in values
    for value in data_detail['values']:
        #print(value)
        if len(value) != 4:
            return "Invalid request. Check the values structure", 404
        fport=value[0]
        type=value[1]
        ref=value[2]
        value=value[3]
        #print("fport = " + fport + " type = " + type + " ref = " + ref + " value = " + str(value))
        output = output + format_message(ref, value)

    return output


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8686)
