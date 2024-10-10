#Tarea02 Redes de computadores INF224
#Daniel Belozo Ossandón daniel.belozo@alumnos.uv.cl
#Mariajosé Baxmann Román mariajose.baxmann@alumnos.uv.cl
#Francisco Villagran Madrid francisco.villagran@alumnos.uv.cl

import http.client
import json
import subprocess
import re
import sys
import getopt
import time

# Función para obtener el fabricante a partir de la MAC y el tiempo de respuesta
def get_mac(mac: str):
    conn = http.client.HTTPSConnection("api.maclookup.app")
    
    # Medimos el tiempo de inicio
    start_time = time.time()
    
    conn.request("GET", f"/v2/macs/{mac}")
    
    # Obtener la respuesta
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    
    # Medimos el tiempo final
    end_time = time.time()

    # Parsear el JSON
    json_data = json.loads(data)

    # Calcular el tiempo de respuesta en milisegundos
    elapsed_time = (end_time - start_time) * 1000

    return json_data, elapsed_time

# Función para obtener la tabla ARP y devolver las MACs y IPs como tuplas
def get_arp_table():
    tabla_arp = subprocess.run(["arp", "-a"], stdout=subprocess.PIPE)
    macs = re.findall(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(tabla_arp.stdout).replace("-", ":"))
    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', str(tabla_arp.stdout))
    return list(zip(ips, macs))

# Función para filtrar direcciones MAC de broadcast y multicast
def is_broadcast_or_multicast(mac):
    return mac.startswith("ff:ff:ff") or mac.startswith("01:00:5e")

# Función para procesar los resultados y devolver el formato requerido
def process_result(mac_vendor, ip_mac):
    ip, mac = ip_mac
    vendor_data, _ = mac_vendor(mac)
    vendor = vendor_data['company']
    return f"{ip} / {mac} / {vendor if vendor else 'Not Found'}"

# Función principal para procesar la tabla ARP de manera funcional
def process_arp_table():
    arp_table = get_arp_table()
    mac_vendor = get_mac
    valid_arp_entries = filter(lambda x: not is_broadcast_or_multicast(x[1]), arp_table)
    return list(map(lambda x: process_result(mac_vendor, x), valid_arp_entries))

# Función principal de búsqueda por MAC
def search_mac(mac):
    response, elapsed_time = get_mac(mac)  # Extraemos tanto el JSON como el tiempo de respuesta
    if response['found']:
        return f"MAC Address : {mac}\nFabricante : {response['company']}\nTiempo de respuesta: {elapsed_time:.2f} ms"
    else:
        return f"MAC Address : {mac}\nFabricante : Not Found\nTiempo de respuesta: {elapsed_time:.2f} ms"

# Función para mostrar el uso del programa
def print_usage():
    print("Uso: python OUILookup.py --mac <mac> | --arp")
    print("--mac: MAC a consultar. Ej: aa:bb:cc:00:00:00.")
    print("--arp: Muestra los fabricantes de los hosts disponibles en la tabla ARP.")
    print("--help: Muestra este mensaje y termina.")

if __name__ == "__main__":
    # Configuración de getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        sys.exit(2)

    mac = None
    arp_flag = False

    # Procesamiento de las opciones
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit()
        elif opt in ("-m", "--mac"):
            mac = arg
        elif opt in ("-a", "--arp"):
            arp_flag = True

    # Si se solicita la tabla ARP, procesa en forma funcional
    if arp_flag:
        results = process_arp_table()
        print("IP/MAC/Vendor:")
        print("\n".join(results))
    elif mac:
        # Si se ingresa una MAC específica, búscala directamente
        print(search_mac(mac))
    else:
        # Si no se ingresan opciones, mostrar el uso del programa
        print_usage()
