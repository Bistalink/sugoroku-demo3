<script lang="ts">
  import type { Socket } from "socket.io-client";
  import type { GameState, PlayerState, Player} from "./util";
  

  export let socket: Socket
  export let started: boolean = false;

  let gameover: boolean;
  let gameState: GameState;
  let playerState: PlayerState;

  let diceRequested: boolean = false;

  let winner: string = "";

  socket.on("update_state", (data: GameState)=>{
    gameState = data;
    console.log(data);
  })

  socket.on("update_player_state", (data: PlayerState)=>{
    playerState = data;
    console.log(data);
  })

  socket.on("gameover", (playername: string)=>{
    gameover = true;
    winner = playername;
  })

  socket.on("request:dice", ()=>{
    console.log("Dice requested by server");
    diceRequested = true;
  })

  function dice(){
    socket.emit("dice");
    diceRequested = false;
  }
</script>


{#if started}
<div>
  <!-- サイコロ回すやつ -->
  <div style="display: {diceRequested ? "" : "none"};">
    <button on:click={dice}>サイコロを回す</button>
  </div>

  {#if gameState != undefined}
  <div>
    {#each gameState.players as p}
      <h3>プレイヤー名：{p.name} ポジション：{p.position}</h3>
    {/each}
    <!-- ゲームクリア画面 -->
    <div style="display: {gameover ? "" : "none"};">
      <h1>{winner} がゴールしました！</h1>
    </div>
  </div>
  {/if}
</div>
{/if}

<style>
</style>