<script lang="ts">
  import type { Socket } from "socket.io-client";
  import type { GameState, Player, RequestedQuestion} from "./util";
  import "animate.css"

  import bike from "./assets/bike.png"
  import girl from "./assets/girl.png"
  import bb_footer from "./assets/bb_footer.png"
  

  export let socket: Socket
  export let started: boolean = false;

  let gameover: boolean;              // ゲームが終了したかどうか
  let gameState: GameState;           // ゲームの内部状態
  let playerState: Player;       // このセッションのプレイヤーの内部状態

  let diceRequested: boolean = false; // サイコロを振るリクエスト中

  let position: number;
  let animationRequired = ""

  let questionContent = "";
  let questionLabel = "";
  let questionIdx = 0;

  let showAnswerScreen = false;
  let canAnswer = false;

  let event_description = [
    "正解：+1マス",
    "正解：+2マス",
    "不正解：-1マス",
    "不正解：-2マス",
    "不正解：1回休み",
    "正解：もう1回サイコロを振る"
  ]

  let event_colors = [
    "white",
    "#B4FEBC",
    "#CF5A3D",
    "#BB2E1F",
    "#A70101",
    "linear-gradient(to right,#de4141,#e8ac51,#f2e55c,#39a869,#4784bf,#5d5099,#a55b9a)"
  ]

  let railOffset = 0;
  let log: string[] = [];

  let winner: string = "";            // 勝者

  // イベントボード
  // TODO: 仮
  let board_events = Array.from({length: 30}, ()=> Math.floor(Math.random() * 6));
  console.log("board:", board_events)

  // ゲーム状態が更新されたとき
  socket.on("update_state", (data: GameState)=>{
    gameState = data;
    showAnswerScreen = false;

    log = gameState.log;
    if (log.length > 3){
      log = log.slice(-3)
    }
  })

  // プレイヤーの状態が更新されたとき
  socket.on("update_player_state", (data: Player)=>{
    playerState = data;
    position = playerState.position;
    console.log(data);
  })

  // ゲームが終了したとき
  socket.on("gameover", (playername: string)=>{
    gameover = true;
    winner = playername;
  })

  // サイコロを振るリクエストが来たとき
  socket.on("request:dice", ()=>{
    console.log("Dice requested by server");
    diceRequested = true;
  })

  socket.on("animate", (sid: string)=>{
    animationRequired = sid;
    setTimeout(() => {
      animationRequired = "";
    }, 700);
  })

  socket.on("request:answer", (question: RequestedQuestion)=>{
    setTimeout(() => {
      showAnswerScreen = true;  
      canAnswer = question.sid == playerState.sid;
    }, 1300);
    
    (document.getElementById("answerInput") as HTMLInputElement).focus();

    questionContent = question.content[0];
    questionLabel = question.content[1];
    questionIdx = question.question_idx;

    console.log("Question: ", question.content, "Index: ", question.question_idx);
  })

  socket.on("error", (text)=>{
    alert(text);
    location.reload();
  })

  function dice(){
    socket.emit("dice");
    diceRequested = false;
  }

  function answer(){
    const answerBox = document.getElementById("answerInput") as HTMLInputElement;
    const answer = answerBox.value;
    const payload = {
      answer: answer,
      question_idx: questionIdx
    }

    socket.emit("answer", payload);

    showAnswerScreen = false;
    answerBox.value = "";
  }

  function restart(){
    socket.emit("restart");
  }
</script>


{#if started}
<div>
  <!-- サイコロ回すやつ -->
  <div>
    <button on:click={dice} class="" disabled="{!diceRequested}">サイコロを回す</button>
  </div>

  {#if gameState != undefined && playerState != undefined}
  <div>
    <!-- {#each gameState.players as p}
      <h3>プレイヤー名：{p.name} ポジション：{p.position}</h3>
    {/each} -->

    <!-- プレイヤー情報 -->
    <div id="playerName">プレーヤー名: {playerState.name}</div>
    <div id="position">現在：{playerState.position} マス目</div>
    <div id="remaining">残り：{gameState.goal - playerState.position}マス</div>

    <!-- ログ画面 -->
    <div class="log-screen">
      <div>
      {#each log as logLine}
        <p>{logLine}</p>
      {/each}
      </div>
    </div>

    <!-- レール -->
    <!-- TODO:ループで回して全員分表示させる -->
    {#each gameState.players as player}
    <div class="lane">
      <img class="{animationRequired && animationRequired == player["sid"] ? "animate__animated animate__wobble" : ""}" src="{bike}" alt="">
      <div class="rail-wrapper">
        <div class="rail" style="left: {-player.position * 5 + 5}rem;">
          {#each gameState.event_list as event, index}
          <div class="cell"> <!-- TODO: 最初のマスは確定で白いろにする -->
            <div style="background: {event_colors[event]};"></div>
            <p>{index}</p>
          </div>
          <!-- <p style="width: 1rem; padding: 0; margin: 0">{one_grid}</p> -->
          {/each}
        </div>
      </div>  
    </div>
    {/each}

    <!-- 問題回答画面 -->
    <div class="answer-screen" style="{showAnswerScreen ? "opacity: 1;" : "display: none; opacity: 0;"}">
      <div class="wrapper">
        <h2>{questionContent}</h2>
        <h3>{questionLabel}</h3>
        <div style="display: {canAnswer ? "" : "none"};">
          <h4>{event_description[gameState.event_list[playerState.position]]}</h4>
          <input id="answerInput" type="text">
          <button on:click={answer}>回答</button>
        </div>
      </div>
    </div>

    <!-- ゲームクリア画面 -->
    <div class="gameover" style="display: {gameover ? "" : "none"};">
      <div>
        <h1>{winner} がゴールしました！</h1>
        <button on:click={restart}>リスタート</button>
      </div>
    </div>

    <!-- 装飾 -->
    <div class="decoration">
      <footer style="background-image: url({bb_footer})"></footer>
      <img class="girl" src="{girl}" alt="">
    </div>
  </div>
  {/if}
</div>
{/if}

<style lang="scss">
  .lane {
    display: flex;
    position: relative;
    flex-direction: column;
    height: 10rem;

    img {
      position: absolute;
      width: 4rem;
      height: 4rem;
      left: 5rem;
      //background-color: red;
    }
  }

  .rail-wrapper {
    position: relative;
    overflow: hidden;
    width:40rem;
    height: 3rem;
    top: 5rem;
  }

  .rail {
    position: absolute;
    display: flex;
    flex-direction: row;
    gap: 1rem;
    transition: all 0.2s;

    div.cell {
      width: 4rem;
      height: 0.4rem;
      margin: 0;
      padding: 0;

      div {
        background-color: white;
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        border-radius: 4px;
      }
    }
  }

  .answer-screen {
    position: absolute;
    display: flex;
    justify-content: center;
    align-items: center;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidd;

    div.wrapper {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background-color: rgba(0, 0, 0, 0.2);
      border: 1px solid rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(10px);
      min-width: 50rem;
      min-height: 30rem;
      border-radius: 8px;
      gap: 0.5rem;
    }
  }

  .log-screen {
    display: flex;
    position: absolute;
    justify-content: flex-end;
    align-items: flex-start;
    pointer-events: none;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;

    div {
      display: flex;
      position: absolute;
      flex-direction: column;
      width: 30rem;
      height: 30rem;
      margin: 1rem;
      gap: 2px;
      
      p {
      margin: 0;
      background-color: rgba(255, 255, 255, 0.1);
      padding: 1px;
      }
    }
  }

  .gameover {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;

    div {
      background-color: rgba(255, 255, 255, 0.2);
      padding: 2rem;
      border-radius: 8px;
      backdrop-filter: blur(10px);
    }
  }

  .decoration {
    position: absolute;
    left: 0;
    top: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    pointer-events: none;

    img.girl {
      width: 220px;
    }
  }

  footer {
    position: absolute;
    pointer-events: none;
    z-index: -2;
    left: 0;
    bottom: 0;
    width: 100vw;
    height: 73px;
  }
</style>