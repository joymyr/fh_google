class Device:
    device_id: str
    device_name: str
    siren_status: str
    playback_status: str
    volume: int
    meta_track: str
    meta_artist: str
    meta_album: str
    meta_image: str

    def __init__(self, data):
        self.device_id = data["id"]
        self.device_name = data["name"]
        self.volume = data["status"]["volume"]
        self.siren_status = "off" if data['status']['status'] == "" and data['status']['title'] == "" and data['status']['application'] == "" else "off"
        self.playback_status = "play" if data['status']['status'] == "PLAYING" else "pause" if data['status']['application'] != "" or data['status']['title'] != "" else "stop"
        self.meta_track = data['status'].get('title', "")
        self.meta_artist = data['status'].get('subtitle', "")
        self.meta_album = data['status'].get('application', "")
        self.meta_image = data["status"].get('image_url', "")

    def compare(self, other):
        # Compare all attributes
        return (isinstance(other, Device) and
                self.device_id == other.device_id and
                self.device_name == other.device_name and
                self.siren_status == other.siren_status and
                self.playback_status == other.playback_status and
                self.volume == other.volume and
                self.meta_track == other.meta_track and
                self.meta_artist == other.meta_artist and
                self.meta_album == other.meta_album and
                self.meta_image == other.meta_image)
