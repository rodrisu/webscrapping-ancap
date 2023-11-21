from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = Flask(__name__)

ANCAP_GASOLINE = [
    {"name": "Super 95", "url": "https://www.ancap.com.uy/1636/1/super-95.html"},
    {"name": "Premium 97", "url": "https://www.ancap.com.uy/1637/1/premium-97.html"},
    {"name": "Gasoil 10-S", "url": "https://www.ancap.com.uy/1641/1/gasoil-10-s.html"},
    {"name": "Gasoil 50-S", "url": "https://www.ancap.com.uy/1642/1/gasoil--50-s.html"},
]


def get_gasoline_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    producto_data_box = soup.select(".producto-data-box")

    return {
        "max_price": producto_data_box[0].select("#envaseprecio")[0].text.replace(" ", "").replace("$", ""),
        "ancap_price": producto_data_box[0].select("#envaseprecio")[1].text.replace(" ", "").replace("$", ""),
        "currency": "UYU",
    }

def get_super_95_info():
    super_95_url = next((g["url"] for g in ANCAP_GASOLINE if g["name"] == "Super 95"), None)

    if super_95_url:
        response = requests.get(super_95_url)
        soup = BeautifulSoup(response.text, "html.parser")
        producto_data_box = soup.select(".producto-data-box")

        return {
            "max_price": producto_data_box[0].select("#envaseprecio")[0].text.replace(" ", "").replace("$", ""),
            "ancap_price": producto_data_box[0].select("#envaseprecio")[1].text.replace(" ", "").replace("$", ""),
            "currency": "UYU",
        }
    else:
        return None


@app.route("/api/v1/gasoline", methods=["GET"])
def get_all_gasolines():
    gasoline = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_gasoline_info, ancap["url"]): ancap for ancap in ANCAP_GASOLINE}
        for future in concurrent.futures.as_completed(futures):
            ancap = futures[future]
            try:
                gasoline[ancap["name"]] = future.result()
            except Exception as e:
                print(f"Error fetching data for {ancap['name']}: {e}")

    return jsonify(gasoline)


@app.route("/api/v1/gasoline/<name>", methods=["GET"])
def get_one_gasoline(name):
    gas_name = name.lower().replace(" ", "_")
    gas = next((g for g in ANCAP_GASOLINE if g["name"].lower().replace(" ", "_") == gas_name), None)

    if gas:
        return jsonify(get_gasoline_info(gas["url"]))
    else:
        return jsonify({"error": "Gasoline type not found"}), 404

@app.route("/api/v1/super_95", methods=["GET"])
def super_95():
    return jsonify(get_super_95_info())


if __name__ == "__main__":
    app.run(debug=True)
