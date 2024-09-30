from flask import Flask, request, jsonify
import socket
import os
import netifaces
import re

app = Flask(__name__)
SPECIFIC_INTERFACE = 'eth0'

def get_mac_address(interface):
    try:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_LINK in addresses:
            mac = addresses[netifaces.AF_LINK][0]['addr']
            if mac and len(mac.split(':')) == 6:  # Check if it looks like a MAC address
                return mac
    except KeyError:
        pass
    return None

def mac_to_serial(mac_address):
    # Elimina los dos puntos de la dirección MAC
    clean_mac = mac_address.replace(":", "").upper()
    
    # Asegúrate de que la dirección MAC tenga la longitud correcta
    if len(clean_mac) != 12 or not re.match(r'^[0-9A-F]{12}$', clean_mac):
        raise ValueError("Invalid MAC address format")
    
    # Convierte los caracteres hexadecimales a alfanuméricos (si es necesario)
    # Aquí se puede implementar una lógica más compleja si se desea un formato específico
    
    # Agrupa los caracteres en bloques de 4 para legibilidad
    serial = ''.join(clean_mac[i:i+4] for i in range(0, len(clean_mac), 4))
    return serial


@app.route('/hostname', methods=['GET'])
def obtener_hostname():
    hostname = socket.gethostname()
    mac_address = get_mac_address(SPECIFIC_INTERFACE)
    serial_num = mac_to_serial(mac_address)
    return jsonify({'hostname': hostname, 'mac_address': mac_address, 'serial_number': serial_num}), 200

@app.route('/hostname', methods=['POST'])
def cambiar_hostname():
    data = request.get_json()
    if 'hostname' not in data:
        return jsonify({'error': 'No hostname provided'}), 400
    
    new_hostname = data['hostname']
    
    # Change the hostname
    try:
        # Cambiar el hostname actual
        os.system(f'sudo hostnamectl set-hostname {new_hostname}')
        
        # Actualizar el archivo /etc/hosts para reflejar el nuevo hostname
        with open('/etc/hosts', 'r') as file:
            hosts_content = file.read()
        
        hosts_content = hosts_content.replace(socket.gethostname(), new_hostname)
        
        with open('/etc/hosts', 'w') as file:
            file.write(hosts_content)
        
        # Obtener la dirección MAC
        mac_address = get_mac_address(SPECIFIC_INTERFACE)
        
        return jsonify({'hostname': new_hostname, 'mac_address': mac_address}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
