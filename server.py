import base64
import hashlib
import json
import mimetypes
import sqlite3
import struct
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
SCRIPT_DIR = ROOT / "demo"
DB_PATH = ROOT / "script_kill.sqlite3"
# HOST = "127.0.0.1"
HOST = "0.0.0.0"
PORT = 8088
WAITING_ROOM_TTL = 24 * 60 * 60
FINISHED_ROOM_TTL = 7 * 24 * 60 * 60

rooms_lock = threading.Lock()
room_clients = {}


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.executescript(
            """
            create table if not exists users (
                open_id text primary key,
                nickname text not null,
                created_at integer not null
            );
            create table if not exists rooms (
                room_id text primary key,
                script_id integer not null,
                title text not null,
                status text not null,
                host_open_id text not null,
                current_round integer not null default 1,
                created_at integer not null,
                finished_at integer
            );
            create table if not exists room_players (
                room_id text not null,
                open_id text not null,
                nickname text not null,
                character_id integer,
                ready integer not null default 0,
                joined_at integer not null,
                primary key (room_id, open_id)
            );
            create table if not exists room_answers (
                room_id text not null,
                open_id text not null,
                answers_json text not null,
                score integer not null,
                is_winner integer not null default 0,
                submitted_at integer not null,
                primary key (room_id, open_id)
            );
            create table if not exists room_clues (
                room_id text not null,
                round integer not null,
                clue_index integer not null,
                released_by text not null,
                released_at integer not null,
                primary key (room_id, round, clue_index)
            );
            """
        )
        # Safe migration for older local sqlite files.
        cols = [row[1] for row in conn.execute("pragma table_info(rooms)").fetchall()]
        if "finished_at" not in cols:
            conn.execute("alter table rooms add column finished_at integer")


def load_scripts():
    scripts = {}
    for path in sorted(SCRIPT_DIR.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            script = raw.get("params", {}).get("script", raw.get("script", raw))
            script_id = int(script["scriptId"])
            
            # 读取status字段，默认为1（显示）
            status = int(script.get("status", 1))
            
            # status=0的剧本不加载（隐藏）
            if status == 0:
                continue
            
            script["_sourceFile"] = path.name
            scripts[script_id] = script
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return scripts


def read_script(script_id=None):
    scripts = load_scripts()
    if not scripts:
        raise RuntimeError("no_script_files_found")
    if script_id is None:
        return next(iter(scripts.values()))
    script = scripts.get(int(script_id))
    if not script:
        raise KeyError("script_not_found")
    return script


def public_character(character, include_private=False):
    safe = {key: value for key, value in character.items() if key != "data"}
    if include_private:
        safe["data"] = character.get("data", {})
    return safe


def public_script_summary(script):
    return {
        "scriptId": script.get("scriptId"),
        "scriptName": script.get("scriptName"),
        "cover": script.get("cover") or script.get("album"),
        "music": script.get("music"),
        "author": script.get("author"),
        "player": script.get("player"),
        "duration": script.get("duration"),
        "tags": script.get("tags", []),
        "scene": script.get("scene"),
        "introduce": script.get("introduce"),
        "characters": [public_character(item) for item in script.get("characters", [])],
        "roundCount": len(script.get("rounds", [])),
    }


def visible_rounds(script, room, revealed_clues=None, requester_is_host=False):
    if room["status"] != "playing":
        return []
    revealed_clues = revealed_clues or set()
    current_round = int(room["current_round"])
    rounds = []
    for item in script.get("rounds", []):
        if int(item.get("round", 0)) != current_round:
            continue
        safe = dict(item)
        if not requester_is_host:
            safe.pop("hostGuide", None)
        public_clues = []
        for index, clue in enumerate(item.get("publicClues", [])):
            released = (current_round, index) in revealed_clues
            public_clues.append({
                "index": index,
                "keyword": clue.get("keyword", f"线索{index + 1}"),
                "content": clue.get("content") if released else "",
                "content_audio": clue.get("content_audio") if released else "",
                "released": released,
            })
        safe["publicClues"] = public_clues
        rounds.append(safe)
    return rounds


def visible_final_questions(script, include_answers=False):
    questions = []
    for item in script.get("finalQuestions", []):
        safe = dict(item)
        if not include_answers:
            safe.pop("answer", None)
        questions.append(safe)
    return questions


def visible_script_for_room(script, room, players, open_id=None, revealed_clues=None):
    requester = next((dict(player) for player in players if player["open_id"] == open_id), None)
    requester_is_host = bool(open_id and room["host_open_id"] == open_id)
    my_character_id = requester.get("character_id") if requester else None
    safe = public_script_summary(script)
    safe["characters"] = [
        public_character(item, include_private=(item.get("id") == my_character_id))
        for item in script.get("characters", [])
    ]
    safe["rounds"] = visible_rounds(script, room, revealed_clues, requester_is_host)
    safe["finalQuestions"] = visible_final_questions(script, include_answers=(room["status"] == "finished")) if room["status"] in ("answering", "finished") else []
    if room["status"] == "finished":
        safe["answers"] = script.get("answers", {})
    return safe


def cleanup_old_rooms():
    now = int(time.time())
    with db() as conn:
        rows = conn.execute(
            """
            select room_id from rooms
            where (status = 'waiting' and created_at < ?)
               or (status = 'finished' and coalesce(finished_at, created_at) < ?)
            """,
            (now - WAITING_ROOM_TTL, now - FINISHED_ROOM_TTL),
        ).fetchall()
        room_ids = [row["room_id"] for row in rows]
        for room_id in room_ids:
            delete_room_records(conn, room_id)
    return room_ids


def delete_room_records(conn, room_id):
    conn.execute("delete from room_clues where room_id = ?", (room_id,))
    conn.execute("delete from room_answers where room_id = ?", (room_id,))
    conn.execute("delete from room_players where room_id = ?", (room_id,))
    conn.execute("delete from rooms where room_id = ?", (room_id,))


def delete_lonely_waiting_rooms(conn, open_id, exclude_room_id=None):
    rows = conn.execute(
        """
        select r.room_id from rooms r
        join room_players p on p.room_id = r.room_id
        where r.host_open_id = ? and r.status = 'waiting'
        group by r.room_id
        having count(p.open_id) = 1 and max(p.open_id) = ?
        """,
        (open_id, open_id),
    ).fetchall()
    deleted = []
    for row in rows:
        room_id = row["room_id"]
        if room_id == exclude_room_id:
            continue
        delete_room_records(conn, room_id)
        deleted.append(room_id)
    return deleted


def send_json(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_body(handler):
    size = int(handler.headers.get("Content-Length", "0") or 0)
    if not size:
        return {}
    return json.loads(handler.rfile.read(size).decode("utf-8"))


def ensure_user(open_id, nickname):
    with db() as conn:
        conn.execute(
            "insert or ignore into users(open_id, nickname, created_at) values(?, ?, ?)",
            (open_id, nickname, int(time.time())),
        )
        conn.execute("update users set nickname = ? where open_id = ?", (nickname, open_id))


def get_room(conn, room_id):
    return conn.execute("select * from rooms where room_id = ?", (room_id,)).fetchone()


def is_host(conn, room_id, open_id):
    room = get_room(conn, room_id)
    return bool(room and room["host_open_id"] == open_id)


def room_state(room_id, open_id=None):
    with db() as conn:
        room = get_room(conn, room_id)
        if not room:
            return None
        script = read_script(room["script_id"])
        players = conn.execute(
            "select open_id, nickname, character_id, ready from room_players where room_id = ? order by joined_at",
            (room_id,),
        ).fetchall()
        answer_rows = conn.execute(
            "select open_id, answers_json, score, is_winner, submitted_at from room_answers where room_id = ? order by submitted_at",
            (room_id,),
        ).fetchall()
        clues = conn.execute(
            "select round, clue_index, released_by, released_at from room_clues where room_id = ?",
            (room_id,),
        ).fetchall()
        revealed_clues = {(int(row["round"]), int(row["clue_index"])) for row in clues}
    return {
        "room": dict(room),
        "script": visible_script_for_room(script, room, players, open_id, revealed_clues),
        "players": [dict(player) for player in players],
        "answers": [
            {
                "open_id": row["open_id"],
                "score": row["score"],
                "is_winner": row["is_winner"],
                "submitted_at": row["submitted_at"],
                "answers": json.loads(row["answers_json"] or "{}") if room["status"] == "finished" else {},
            }
            for row in answer_rows
        ],
        "clues": [dict(row) for row in clues],
    }


def list_rooms(open_id=None):
    cleanup_old_rooms()
    params = []
    owner_where = ""
    if open_id:
        owner_where = "where r.host_open_id = ? or exists (select 1 from room_players rp where rp.room_id = r.room_id and rp.open_id = ?)"
        params.extend([open_id, open_id])
    with db() as conn:
        rows = conn.execute(
            f"""
            select r.room_id, r.script_id, r.title, r.status, r.current_round, r.host_open_id,
                   count(p.open_id) as player_count, r.created_at
            from rooms r
            left join room_players p on p.room_id = r.room_id
            {owner_where}
            group by r.room_id
            order by r.created_at desc
            limit 30
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def broadcast(room_id):
    with rooms_lock:
        clients = list(room_clients.get(room_id, {}).items())
    for client, open_id in clients:
        try:
            state = room_state(room_id, open_id)
            if not state:
                payload = ws_encode(json.dumps({"type": "room_deleted"}, ensure_ascii=False))
            else:
                payload = ws_encode(json.dumps({"type": "room_state", "data": state}, ensure_ascii=False))
            client.sendall(payload)
        except OSError:
            with rooms_lock:
                room_clients.get(room_id, {}).pop(client, None)


def ws_encode(message):
    data = message.encode("utf-8")
    length = len(data)
    if length < 126:
        header = bytes([0x81, length])
    elif length < 65536:
        header = bytes([0x81, 126]) + struct.pack("!H", length)
    else:
        header = bytes([0x81, 127]) + struct.pack("!Q", length)
    return header + data


def ws_read(sock):
    first = sock.recv(2)
    if len(first) < 2:
        return None
    opcode = first[0] & 0x0F
    if opcode == 8:
        return None
    masked = first[1] & 0x80
    length = first[1] & 0x7F
    if length == 126:
        length = struct.unpack("!H", sock.recv(2))[0]
    elif length == 127:
        length = struct.unpack("!Q", sock.recv(8))[0]
    mask = sock.recv(4) if masked else b""
    data = sock.recv(length)
    if masked:
        data = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
    return data.decode("utf-8")


def ws_handshake(handler):
    key = handler.headers.get("Sec-WebSocket-Key", "")
    accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    handler.send_response(101, "Switching Protocols")
    handler.send_header("Upgrade", "websocket")
    handler.send_header("Connection", "Upgrade")
    handler.send_header("Sec-WebSocket-Accept", accept)
    handler.end_headers()


def validate_start(conn, room_id, open_id):
    room = get_room(conn, room_id)
    if not room:
        return "room_not_found"
    script = read_script(room["script_id"])
    if room["host_open_id"] != open_id:
        return "only_host_can_start"
    if room["status"] != "waiting":
        return "room_already_started"
    players = conn.execute("select character_id, ready from room_players where room_id = ?", (room_id,)).fetchall()
    if len(players) != int(script.get("player", 0)):
        return f"need_{script.get('player')}_players"
    if any(not row["character_id"] or not row["ready"] for row in players):
        return "all_players_must_choose_character"
    if len({row["character_id"] for row in players}) != len(players):
        return "character_must_be_unique"
    return None


def calculate_score(script_id, submitted):
    script = read_script(script_id)
    answers = {str(item["id"]): item["answer"] for item in script.get("finalQuestions", [])}
    return sum(1 for qid, answer in answers.items() if submitted.get(qid) == answer)


class AppHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/api/scripts":
            send_json(self, {"scripts": [public_script_summary(script) for script in load_scripts().values()]})
            return
        if parsed.path == "/api/rooms":
            open_id = query.get("open_id", [None])[0]
            send_json(self, {"rooms": list_rooms(open_id)})
            return
        if parsed.path.startswith("/api/rooms/"):
            room_id = parsed.path.rsplit("/", 1)[-1]
            open_id = query.get("open_id", [None])[0]
            state = room_state(room_id, open_id)
            send_json(self, state or {"error": "room_not_found"}, 200 if state else 404)
            return
        if parsed.path == "/ws":
            self.handle_ws(parsed)
            return
        self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        body = read_body(self)
        if parsed.path == "/api/login":
            open_id = body.get("open_id") or f"demo_{uuid.uuid4().hex[:10]}"
            nickname = body.get("nickname") or f"玩家{open_id[-4:]}"
            ensure_user(open_id, nickname)
            send_json(self, {"open_id": open_id, "nickname": nickname})
            return
        if parsed.path == "/api/rooms":
            self.create_room(body)
            return
        if parsed.path.endswith("/join"):
            self.join_room(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/choose"):
            self.choose_character(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/start"):
            self.start_room(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/round"):
            self.change_round(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/release-clue"):
            self.release_clue(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/answering"):
            self.enter_answering(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/submit"):
            self.submit_answer(parsed.path.split("/")[-2], body)
            return
        if parsed.path.endswith("/delete"):
            self.delete_room(parsed.path.split("/")[-2], body)
            return
        send_json(self, {"error": "not_found"}, 404)

    def create_room(self, body):
        open_id = body["open_id"]
        nickname = body.get("nickname") or f"玩家{open_id[-4:]}"
        try:
            script = read_script(body.get("script_id") or body.get("scriptId"))
        except KeyError:
            send_json(self, {"error": "script_not_found"}, 404)
            return
        ensure_user(open_id, nickname)
        with db() as conn:
            deleted_rooms = delete_lonely_waiting_rooms(conn, open_id)
            existing = conn.execute(
                "select room_id from rooms where host_open_id = ? and script_id = ? and status in ('waiting', 'playing', 'answering') order by created_at desc limit 1",
                (open_id, script["scriptId"]),
            ).fetchone()
            if existing:
                state = room_state(existing["room_id"], open_id)
                state["deleted_rooms"] = deleted_rooms
                send_json(self, state)
                return
            room_id = uuid.uuid4().hex[:6].upper()
            conn.execute(
                "insert into rooms(room_id, script_id, title, status, host_open_id, current_round, created_at) values(?, ?, ?, ?, ?, ?, ?)",
                (room_id, script["scriptId"], script["scriptName"], "waiting", open_id, 1, int(time.time())),
            )
            conn.execute(
                "insert into room_players(room_id, open_id, nickname, joined_at) values(?, ?, ?, ?)",
                (room_id, open_id, nickname, int(time.time())),
            )
        state = room_state(room_id, open_id)
        state["deleted_rooms"] = deleted_rooms
        send_json(self, state)
        broadcast(room_id)

    def join_room(self, room_id, body):
        open_id = body["open_id"]
        nickname = body.get("nickname") or f"玩家{open_id[-4:]}"
        ensure_user(open_id, nickname)
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            script = read_script(room["script_id"])
            already = conn.execute("select 1 from room_players where room_id = ? and open_id = ?", (room_id, open_id)).fetchone()
            if room["status"] != "waiting" and not already:
                send_json(self, {"error": "room_not_waiting"}, 409)
                return
            count = conn.execute("select count(*) as n from room_players where room_id = ?", (room_id,)).fetchone()["n"]
            if count >= int(script.get("player", 0)) and not already:
                send_json(self, {"error": "room_full"}, 409)
                return
            deleted_rooms = [] if already else delete_lonely_waiting_rooms(conn, open_id, exclude_room_id=room_id)
            conn.execute(
                "insert or ignore into room_players(room_id, open_id, nickname, joined_at) values(?, ?, ?, ?)",
                (room_id, open_id, nickname, int(time.time())),
            )
        state = room_state(room_id, open_id)
        state["deleted_rooms"] = deleted_rooms
        send_json(self, state)
        broadcast(room_id)

    def release_clue(self, room_id, body):
        open_id = body.get("open_id")
        clue_round = int(body.get("round") or 0)
        clue_index = int(body.get("clue_index") if body.get("clue_index") is not None else -1)
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            if room["host_open_id"] != open_id:
                send_json(self, {"error": "only_host_can_release_clue"}, 403)
                return
            if room["status"] != "playing":
                send_json(self, {"error": "room_not_playing"}, 409)
                return
            if clue_round != int(room["current_round"]):
                send_json(self, {"error": "can_only_release_current_round_clue"}, 409)
                return
            script = read_script(room["script_id"])
            round_data = next((item for item in script.get("rounds", []) if int(item.get("round", 0)) == clue_round), None)
            if not round_data or clue_index < 0 or clue_index >= len(round_data.get("publicClues", [])):
                send_json(self, {"error": "clue_not_found"}, 404)
                return
            conn.execute(
                "insert or ignore into room_clues(room_id, round, clue_index, released_by, released_at) values(?, ?, ?, ?, ?)",
                (room_id, clue_round, clue_index, open_id, int(time.time())),
            )
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def choose_character(self, room_id, body):
        open_id = body["open_id"]
        character_id = int(body["character_id"])
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            script = read_script(room["script_id"])
            valid_ids = {int(item["id"]) for item in script.get("characters", [])}
            if character_id not in valid_ids:
                send_json(self, {"error": "invalid_character"}, 400)
                return
            if room["status"] != "waiting":
                send_json(self, {"error": "cannot_choose_after_start"}, 409)
                return
            selected_by_other = conn.execute(
                "select open_id from room_players where room_id = ? and character_id = ? and open_id <> ?",
                (room_id, character_id, open_id),
            ).fetchone()
            if selected_by_other:
                send_json(self, {"error": "character_taken"}, 409)
                return
            conn.execute(
                "update room_players set character_id = ?, ready = 1 where room_id = ? and open_id = ?",
                (character_id, room_id, open_id),
            )
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def start_room(self, room_id, body):
        open_id = body.get("open_id")
        with db() as conn:
            error = validate_start(conn, room_id, open_id)
            if error:
                send_json(self, {"error": error}, 409)
                return
            conn.execute("update rooms set status = 'playing', current_round = 1 where room_id = ?", (room_id,))
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def change_round(self, room_id, body):
        open_id = body.get("open_id")
        new_round = int(body["round"])
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            script = read_script(room["script_id"])
            if room["host_open_id"] != open_id:
                send_json(self, {"error": "only_host_can_advance"}, 403)
                return
            if room["status"] != "playing":
                send_json(self, {"error": "room_not_playing"}, 409)
                return
            new_round = max(1, min(len(script.get("rounds", [])), new_round))
            conn.execute("update rooms set current_round = ? where room_id = ?", (new_round, room_id))
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def enter_answering(self, room_id, body):
        open_id = body.get("open_id")
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            script = read_script(room["script_id"])
            if room["host_open_id"] != open_id:
                send_json(self, {"error": "only_host_can_advance"}, 403)
                return
            if room["status"] != "playing":
                send_json(self, {"error": "room_not_playing"}, 409)
                return
            if int(room["current_round"]) != len(script.get("rounds", [])):
                send_json(self, {"error": "must_finish_all_rounds"}, 409)
                return
            conn.execute("update rooms set status = 'answering' where room_id = ?", (room_id,))
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def submit_answer(self, room_id, body):
        open_id = body["open_id"]
        answers = body.get("answers") or {}
        with db() as conn:
            room = get_room(conn, room_id)
            if not room:
                send_json(self, {"error": "room_not_found"}, 404)
                return
            score = calculate_score(room["script_id"], answers)
            if room["status"] != "answering":
                send_json(self, {"error": "room_not_answering"}, 409)
                return
            player = conn.execute("select 1 from room_players where room_id = ? and open_id = ?", (room_id, open_id)).fetchone()
            if not player:
                send_json(self, {"error": "not_in_room"}, 403)
                return
            conn.execute(
                "insert or replace into room_answers(room_id, open_id, answers_json, score, is_winner, submitted_at) values(?, ?, ?, ?, 0, ?)",
                (room_id, open_id, json.dumps(answers, ensure_ascii=False), score, int(time.time())),
            )
            player_count = conn.execute("select count(*) as n from room_players where room_id = ?", (room_id,)).fetchone()["n"]
            answer_count = conn.execute("select count(*) as n from room_answers where room_id = ?", (room_id,)).fetchone()["n"]
            if answer_count >= player_count:
                max_score = conn.execute("select max(score) as m from room_answers where room_id = ?", (room_id,)).fetchone()["m"]
                conn.execute("update room_answers set is_winner = case when score = ? then 1 else 0 end where room_id = ?", (max_score, room_id))
                conn.execute("update rooms set status = 'finished', finished_at = ? where room_id = ?", (int(time.time()), room_id))
        send_json(self, room_state(room_id, open_id))
        broadcast(room_id)

    def delete_room(self, room_id, body):
        open_id = body.get("open_id")
        with db() as conn:
            if not is_host(conn, room_id, open_id):
                send_json(self, {"error": "only_host_can_delete"}, 403)
                return
            delete_room_records(conn, room_id)
        send_json(self, {"ok": True})
        broadcast(room_id)

    def serve_static(self, request_path):
        if request_path == "/":
            request_path = "/index.html"
        target = (PUBLIC_DIR / request_path.lstrip("/")).resolve()
        if not str(target).startswith(str(PUBLIC_DIR.resolve())) or not target.exists():
            send_json(self, {"error": "not_found"}, 404)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type = f"{content_type}; charset=utf-8"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_ws(self, parsed):
        query = parse_qs(parsed.query)
        room_id = query.get("room_id", [""])[0]
        if not room_id:
            send_json(self, {"error": "room_id_required"}, 400)
            return
        ws_handshake(self)
        sock = self.connection
        with rooms_lock:
            room_clients.setdefault(room_id, {})[sock] = query.get("open_id", [None])[0]
        broadcast(room_id)
        try:
            while True:
                message = ws_read(sock)
                if message is None:
                    break
                data = json.loads(message)
                if data.get("type") == "ping":
                    sock.sendall(ws_encode(json.dumps({"type": "pong"})))
        except (OSError, json.JSONDecodeError):
            pass
        finally:
            with rooms_lock:
                room_clients.get(room_id, {}).pop(sock, None)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    init_db()
    PUBLIC_DIR.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Script Kill H5 demo running: http://{HOST}:{PORT}")
    server.serve_forever()
