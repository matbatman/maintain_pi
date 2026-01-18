import requests

class YandexSmartHome:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.iot.yandex.net/v1.0"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_devices(self):
        url = f"{self.base_url}/devices"
        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()["devices"]

    def turn_on(self, device_id: str):
        return self._send_action(device_id, "on", True)

    def turn_off(self, device_id: str):
        return self._send_action(device_id, "on", False)

    def set_brightness(self, device_id: str, value: int):
        return self._send_action(device_id, "brightness", value)

    def set_color(self, device_id: str, rgb: list):
        return self._send_action(device_id, "rgb", rgb)

    def _send_action(self, device_id: str, capability: str, value):
        url = f"{self.base_url}/devices/actions"
        payload = {
            "devices": [
                {
                    "id": device_id,
                    "actions": [
                        {
                            "type": "devices.capabilities.on_off" if capability == "on" else
                                    "devices.capabilities.range" if capability == "brightness" else
                                    "devices.capabilities.color_setting",
                            "state": {
                                "instance": "on" if capability == "on" else
                                            "brightness" if capability == "brightness" else
                                            "rgb",
                                "value": value
                            }
                        }
                    ]
                }
            ]
        }
        r = requests.post(url, json=payload, headers=self._headers())
        r.raise_for_status()
        return r.json()
