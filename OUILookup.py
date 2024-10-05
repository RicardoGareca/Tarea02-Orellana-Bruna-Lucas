# Integrante Lucas Orellana Bruna, lucas.orellana@alumnos.uv.cl, 21.275.378-5
import requests 
import time
import subprocess
import re
import sys
import getopt

# Función para obtener el fabricante de la MAC desde la API
def get_vendor_from_mac(mac_address):
    url = f'https://api.maclookup.app/v2/macs/{mac_address}'
    start_time = time.time()

    try:
        response = requests.get(url)
        response_time = int((time.time() - start_time) * 1000)  # Tiempo de respuesta en milisegundos

        if response.status_code == 200:
            data = response.json()
            if 'company' in data:
                return data['company'], response_time
            else:
                return "Not found", response_time
        else:
            return "Error: Unable to fetch data", response_time

    except requests.RequestException as e:
        return f"Error: {str(e)}", 0

# Función para extraer las MACs de la tabla ARP y obtener los fabricantes
def get_arp_table_vendors():
    # Obtener la tabla ARP en sistemas Linux/Windows
    try:
        if sys.platform == "win32":
            arp_result = subprocess.check_output("arp -a", shell=True).decode()
        else:
            arp_result = subprocess.check_output("arp", shell=True).decode()

        arp_entries = re.findall(r'([0-9a-fA-F:.-]{17})', arp_result)

        results = []
        for mac in arp_entries:
            mac_cleaned = mac.replace("-", ":").replace(".", ":")
            vendor, _ = get_vendor_from_mac(mac_cleaned)
            results.append(f'{mac_cleaned} / {vendor}')
        
        return results
    except subprocess.CalledProcessError as e:
        return f"Error: Could not retrieve ARP table: {str(e)}"

# Función principal para procesar los argumentos
def main(argv):
    mac = None
    show_arp = False

    try:
        opts, args = getopt.getopt(argv, "", ["mac=", "arp", "help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "--mac":
            mac = arg
        elif opt == "--arp":
            show_arp = True
        elif opt == "--help":
            print_help()
            sys.exit()

    if mac:
        mac_cleaned = mac.replace("-", ":").replace(".", ":")
        vendor, response_time = get_vendor_from_mac(mac_cleaned)
        print(f"MAC address : {mac_cleaned}")
        print(f"Fabricante  : {vendor}")
        print(f"Tiempo de respuesta: {response_time}ms")

    elif show_arp:
        arp_vendors = get_arp_table_vendors()
        print("IP/MAC/Vendor:")
        for entry in arp_vendors:
            print(entry)

    else:
        print_help()

# Función para mostrar la ayuda
def print_help():
    help_message = """
    Use: python OUILookup.py --mac <mac> | --arp | [--help]
    
    --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
    --arp: Muestra los fabricantes de los hosts disponibles en la tabla ARP.
    --help: Muestra este mensaje y termina.
    """
    print(help_message)

if __name__ == "__main__":
    main(sys.argv[1:])
