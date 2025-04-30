import requests
import re
import json
from datetime import datetime
from urllib.parse import urljoin
import os
import subprocess

def analizar_respuesta(respuesta):
    salida = "\n[+] Análisis de posibles datos sensibles:\n"
    texto = respuesta.text
    patron = r'(?i)(usuario|user|email|correo)[^:]*[:=]\s*["\']?([\w\.-]+)?["\']?|' \
             r'(apikey|token)[^:]*[:=]\s*["\']?([\w-]+)["\']?|' \
             r'(["\']?password["\']?)\s*[:=]\s*["\']?([\w@!#%&]+)?["\']?'

    matches = re.findall(patron, texto)
    if matches:
        salida += "[!] Posibles datos sensibles encontrados:\n"
        for match in matches:
            clave = [m for m in match if m]
            if clave:
                salida += f"    - {' '.join(clave)}\n"
    else:
        salida += "[+] No se detectaron datos sensibles simples.\n"

    if any(c in texto.lower() for c in ['login', 'password', 'token']):
        salida += "[!] Posible estructura con credenciales detectada.\n"
    else:
        salida += "[+] No se detectaron estructuras con credenciales.\n"

    return salida

def verificar_headers(headers):
    salida = "\n[+] Headers de seguridad:\n"
    claves = {
        'Content-Security-Policy': "No presente",
        'Strict-Transport-Security': "No presente",
        'X-Content-Type-Options': "No presente",
        'X-Frame-Options': "No presente",
        'X-XSS-Protection': "No presente"
    }

    for key in claves.keys():
        if key in headers:
            claves[key] = "Presente"

    for k, v in claves.items():
        salida += f"    - {k}: {v}\n"

    return salida

def pruebas_inyeccion(texto):
    salida = "\n[+] Pruebas de inyección:\n"
    if re.search(r"(select\s.+\sfrom|union\sselect|--|\bor\b\s1=1)", texto, re.IGNORECASE):
        salida += "    - SQLi: Detectado\n"
    else:
        salida += "    - SQLi: No detectado\n"

    if re.search(r"<script.*?>.*?</script>", texto, re.IGNORECASE):
        salida += "    - JS: Detectado\n"
    else:
        salida += "    - JS: No detectado\n"

    return salida

def fuzz_endpoints_y_headers(url_base):
    salida = "\n[+] Fuzzing de rutas y headers comunes:\n"

    rutas_comunes = [
        "/", "/api", "/api/v1", "/api/v2", "/api/login", "/login", "/admin", "/user",
        "/users", "/auth", "/auth/login", "/register", "/dashboard", "/panel", "/signin", "/signup"
    ]

    headers_prueba = [
        {"User-Agent": "Mozilla/5.0", "X-Forwarded-For": "127.0.0.1"},
        {"User-Agent": "sqlmap/1.0", "X-Forwarded-For": "192.168.1.1"},
        {"User-Agent": "curl/7.68.0", "Host": "evil.com"},
    ]

    for ruta in rutas_comunes:
        full_url = urljoin(url_base, ruta)
        for headers in headers_prueba:
            try:
                response = requests.get(full_url, headers=headers, timeout=8)
                salida += f"[+] [{response.status_code}] {full_url} | Headers: {headers}\n"
                if "admin" in response.text.lower() or "dashboard" in response.text.lower():
                    salida += "    [!] Posible panel de administración detectado.\n"
            except Exception as e:
                salida += f"[!] Error al probar {full_url} con headers {headers}: {e}\n"

    return salida + "[+] Fuzzing completado.\n"

def ejecutar_comando(nombre, comando):
    salida = f"\n[+] Resultados de {nombre}:\n"
    try:
        resultado = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, timeout=90)
        salida += resultado.decode(errors="ignore")  # Se eliminó el truncamiento
    except Exception as e:
        salida += f"[!] Error al ejecutar {nombre}: {e}\n"
    return salida

def realizar_auditoria(url, method='GET', headers=None, body=None, fuzz=False):
    headers = headers or {}
    body = body or None

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=body, timeout=10)
        else:
            return f"[!] Método {method} no soportado."

        now = datetime.now()
        resultado = f"\n[+] Auditoría realizada el {now}\n"
        resultado += f"[+] URL: {url}\n"
        resultado += f"[+] Método: {method}\n"
        resultado += f"[+] Headers: {headers}\n"
        resultado += f"[+] Status: {response.status_code}\n"
        resultado += f"[+] Respuesta (preview): {response.text[:400]}\n"

        resultado += analizar_respuesta(response)
        resultado += verificar_headers(response.headers)
        resultado += pruebas_inyeccion(response.text)

        if fuzz:
            resultado += fuzz_endpoints_y_headers(url)

        # Ejecutar Nmap y Nikto
        resultado += ejecutar_comando("Nmap", f"nmap -sV -T4 {url}")
        resultado += ejecutar_comando("Nikto", f"nikto -h {url}")

        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/auditoria_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(resultado)

        resultado += f"\n[+] Log guardado en {log_file}\n"
        print(resultado)  # Imprimir el resultado completo en consola
        return resultado

    except Exception as e:
        return f"[!] Error en la auditoría: {e}"
