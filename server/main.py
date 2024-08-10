from typing import TypedDict
from random import randrange
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import os

# Flaskの初期設定
app = Flask(__name__, template_folder="../dist", static_folder="../dist/assets")
app.config["SECRET_KEY"] = "secretkey"
socketio = SocketIO(app, cors_allowed_origins="*")

class Player(TypedDict):
  name: str
  position: int
  sid: str


class Game:
  game_state = {
    "players": [],
    "turn": 0,
    "current_player": 0,
    "goal": 10
  }

  # 与えられたプレイヤーのリストでゲームを初期化
  def __init__(self, player_list):
    for p in player_list:
      self.game_state["players"].append({
        "name": p["name"],
        "sid": p["sid"],
        "position": 0
      })

  def move(self, diff, player_idx):
    self.game_state["players"][player_idx]["position"] += diff
    self.update_state()

  def add_turn(self, diff):
    self.game_state["turn"] += diff
    self.game_state["current_player"] = self.game_state["turn"] % len(self.game_state["players"])
    self.update_state()

  def update_state(self):
    emit("update_state", self.game_state, broadcast=True)

  def request_dice(self, playeridx):
    emit("request:dice", room=game.get_sid_by_playeridx(playeridx))
  
  def get_playeridx_by_sid(self, sid):
    for index, player in enumerate(self.game_state["players"]):
      if player["sid"] == sid:
        return index
    return None
  
  def get_sid_by_playeridx(self, playeridx):
    return self.game_state["players"][playeridx]["sid"]
  
  def gameover(self, playeridx):
    emit("gameover", self.game_state["players"][playeridx]["name"], broadcast=True)


player_list = []
game = None


@app.route("/")
def index():
  return render_template("index.html")

@socketio.on("dice")
def on_roll_dice():
  idx = game.get_playeridx_by_sid(request.sid)
  print(f"Player {idx} diced!")

  # サイコロを振る
  diced = randrange(1, 6)
  # プレイヤーを動かす
  game.move(diced, idx)
  if game.game_state["players"][idx]["position"] >= game.game_state["goal"]:
    game.gameover(idx)
    return
  # 次の人に回す
  game.add_turn(1)
  # 次の人にサイコロを振らせる
  game.request_dice(game.game_state["current_player"])


@socketio.on("join")
def on_join(playername):
  global player_list
  player_list.append({"name": playername, "sid": request.sid})
  emit("update_player_list", player_list, broadcast=True)
  print(f"Player {playername} joined!")


@socketio.on("start")
def on_start():
  global game
  idx = 0
  game = Game(player_list)
  emit("request:dice", room=game.game_state["players"][idx]["sid"])
  emit("started", broadcast=True)
  print("Game start requested and START!")
  print(f"Dice requested to player {idx}!")


port = int(os.environ.get("PORT", 5555))
socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)