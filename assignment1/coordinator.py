import json, queue, random, threading
from dataclasses import dataclass, field

try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None

from tuple_space import TupleSpace

@dataclass
class MQTTConfig:
    host: str = "localhost"
    port: int = 1883
    client_id: str = field(default_factory=lambda: f"jira-tk-{random.randint(1000,9999)}")
    keepalive: int = 30
    enabled: bool = True

class Coordinator:
    def __init__(self, space: TupleSpace, cfg: MQTTConfig):
        self.space = space
        self.cfg = cfg
        self._client = None
        self.local_mode = False
        self._inbox: "queue.Queue[tuple[str, dict]]" = queue.Queue()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)

        if mqtt is None or not cfg.enabled:
            self.local_mode = True
        else:
            try:
                self._client = mqtt.Client(client_id=cfg.client_id, clean_session=True)
                self._client.on_connect = self._on_connect
                self._client.on_message = self._on_message
                self._client.connect(cfg.host, cfg.port, cfg.keepalive)
                self._client.loop_start()
            except Exception:
                self.local_mode = True

        self._thread.start()
        self.publish_snapshot(retain=True)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("jira/cmd/create_bug")
        client.subscribe("jira/cmd/pick_bug")
        client.subscribe("jira/cmd/update_status")
        self.publish_snapshot(retain=True)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            return
        self._inbox.put((msg.topic, payload))

    def create_bug(self, title: str, priority: str):
        bug = (
            self.space.new_bug_id(),
            title,
            priority,
            "Open",
            "Unassigned",
        )
        if self.local_mode:
            self.space.out(bug)
            self.publish_snapshot()
        else:
            self._publish("jira/cmd/create_bug", {"tuple": bug})

    def pick_bug(self, bug_id: int, dev: str):
        if self.local_mode:
            self.space.pick_specific(bug_id, dev)
            self.publish_snapshot()
        else:
            self._publish("jira/cmd/pick_bug", {"bug_id": bug_id, "dev": dev})

    def update_status(self, bug_id: int, dev: str, new_status: str):
        if self.local_mode:
            self.space.update_status(bug_id, dev, new_status)
            self.publish_snapshot()
        else:
            self._publish("jira/cmd/update_status", {"bug_id": bug_id, "dev": dev, "status": new_status})

    def _publish(self, topic: str, obj: dict, retain: bool=False):
        if self._client:
            self._client.publish(topic, json.dumps(obj), qos=1, retain=retain)

    def publish_snapshot(self, retain: bool=False):
        snapshot = {"bugs": self.space.list_all()}
        if self.local_mode:
            self._inbox.put(("jira/state/snapshot", snapshot))
        else:
            self._publish("jira/state/snapshot", snapshot, retain=retain)

    def _worker(self):
        while not self._stop.is_set():
            try:
                topic, payload = self._inbox.get(timeout=0.25)
            except queue.Empty:
                continue
            if topic == "jira/cmd/create_bug":
                tpl = tuple(payload.get("tuple"))
                if len(tpl) == 5:
                    self.space.out(tpl)
                    self.publish_snapshot()
            elif topic == "jira/cmd/pick_bug":
                dev = payload.get("dev") or "Unknown"
                bug_id = int(payload.get("bug_id", -1))
                if bug_id > 0:
                    self.space.pick_specific(bug_id, dev)
                    self.publish_snapshot()
            elif topic == "jira/cmd/update_status":
                dev = payload.get("dev") or "Unknown"
                bug_id = int(payload.get("bug_id", -1))
                status = payload.get("status") or ""
                if bug_id > 0 and status:
                    self.space.update_status(bug_id, dev, status)
                    self.publish_snapshot()

    def stop(self):
        self._stop.set()
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
