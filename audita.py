import requests

url = "http://100.115.92.206:5000/"

headers_list = [
    {
        "User-Agent": "sqlmap/1.0",
        "X-Forwarded-For": "127.0.0.1",
        "Host": "evil.com"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "192.168.1.100",
        "Host": "192.168.100.12"
    },
    {
        "User-Agent": "curl/7.68.0",
        "X-Forwarded-For": "10.0.0.1",
        "Host": "malicious.internal"
    },
    {
        "User-Agent": "Internal-Scanner",
        "X-Forwarded-For": "admin.local",
        "Host": "localhost"
    }
]

print("[*] Analizando endpoint con headers manipulados...\n")

for i, headers in enumerate(headers_list):
    print(f"\n--- Prueba {i+1} ---")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers enviados: {headers}")
        print(f"Contenido (primeras 200 chars):\n{response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
