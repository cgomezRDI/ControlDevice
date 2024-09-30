from flask import Flask, request, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/hostname', methods=['GET'])
def obtener_hostname():
    hostname = socket.gethostname()
    return jsonify({'hostname': hostname})

@app.route('/hostname', methods=['POST'])
def cambiar_hostname():
    data = request.get_json()
    if 'hostname' not in data:
        return jsonify({'error': 'No hostname provided'}), 400
    
    new_hostname = data['hostname']
    
    # Change the hostname
    try:
        # Change the current hostname
        os.system(f'sudo hostnamectl set-hostname {new_hostname}')
        
        # Update /etc/hosts file to reflect the new hostname
        with open('/etc/hosts', 'r') as file:
            hosts_content = file.read()
        
        hosts_content = hosts_content.replace(socket.gethostname(), new_hostname)
        
        with open('/etc/hosts', 'w') as file:
            file.write(hosts_content)
        
        return jsonify({'hostname': new_hostname}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
