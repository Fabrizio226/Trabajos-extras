import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Estado global simulado de la estación
station_config = {
    "device_id": "ESP32-NODE-01",
    "location": "Reserva Forestal Valparaíso - Sector Norte",
    "test_mode": False  # Para activar/desactivar la alerta manualmente
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # 1. Si el usuario interactuó con la página (envió un formulario)
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Cambiar ubicación
        if action == 'change_location':
            new_loc = request.form.get('location_select')
            if new_loc:
                station_config["location"] = new_loc
                
        # Forzar estado de Alerta
        elif action == 'trigger_alert':
            station_config["test_mode"] = True
            
        # Normalizar estado
        elif action == 'reset_alert':
            station_config["test_mode"] = False

    # 2. Lógica para calcular las lecturas
    if station_config["test_mode"]:
        # Valores de emergencia forzados
        temp = 43.5
        hum = 18
        smoke = "DETECTADO"
        status = "PELIGRO"
    else:
        # Valores simulados aleatorios normales
        temp = round(random.uniform(20.0, 32.0), 1)
        hum = random.randint(35, 60)
        smoke = "NORMAL"
        status = "NORMAL"

    sensor_data = {
        "device_id": station_config["device_id"],
        "location": station_config["location"],
        "temperature": temp,
        "humidity": hum,
        "smoke_level": smoke,
        "status": status,
        "is_test": station_config["test_mode"]
    }

    team = [
        {"name": "Annerill Anabalon", "role": ""},
        {"name": "Jheimy Tolentino", "role": ""},
        {"name": "Javiera Zapata", "role": ""},
        {"name": "Fabrizio Ortiz", "role": ""},
        {"name": "Fabian Cartes", "role": ""}
    ]

    return render_template('index.html', data=sensor_data, team=team)

if __name__ == '__main__':
    app.run(debug=True)