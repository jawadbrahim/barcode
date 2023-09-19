import os
from flask import Flask, request, jsonify
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
from io import BytesIO

barcode_data_dir = 'barcode_data'
os.makedirs(barcode_data_dir, exist_ok=True)

app = Flask(__name__)

@app.route('/scan', methods=['GET', 'POST'])
def barcode_operations():
    if request.method == 'GET':
        return jsonify({'message': 'GET request received for /scan'})

    elif request.method == 'POST':
        image_url = request.json.get('image')
        name = request.json.get('name', '')  

        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_bytes = BytesIO(response.content)
                image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

                decoded_objects = decode(image)

                barcode_data = []

                for obj in decoded_objects:
                    barcode_data.append({
                        'type': obj.type,
                        'data': obj.data.decode('utf-8'),
                    })

            
                filename = os.path.join(barcode_data_dir, 'barcode_data.txt')
                with open(filename, 'a') as file:
                    for data in barcode_data:
                        file.write(f'Name: {name}, Type: {data["type"]}, Data: {data["data"]}\n')

                return jsonify({'success': True, 'barcodes': barcode_data, 'message': 'Data saved to file'})
            else:
                return jsonify({'success': False, 'message': 'Failed to fetch the image'})
        else:
            return jsonify({'success': False, 'message': 'No image URL provided'})

    else:
        return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/search', methods=['GET'])
def search_barcode():
    query = request.args.get('query')


    results = []
    filename = os.path.join(barcode_data_dir, 'barcode_data.txt')
    with open(filename, 'r') as file:
        for line in file:
            if query.lower() in line.lower():  
                results.append(line.strip())

    if results:
        return jsonify({'success': True, 'results': results})
    else:
        return jsonify({'success': False, 'message': 'No matching data found'})

if __name__ == '__main__':
    app.run(debug=True)
