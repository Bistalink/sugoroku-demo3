<script lang="ts">
  import {connect} from "socket.io-client"

  // Svelteコンポーネントのインポート
  import GameConfig from "./GameConfig.svelte";
  import Sugoroku from "./Sugoroku.svelte";

  let isGameStarted = false;  // ゲームが始まっているかどうか
  const socket = connect(location.href);

  // 一般メッセージを受信した場合
  socket.on("alert", text=>{
    alert(text)
  });

  // ゲームがスタートしたら画面を切り替える
  socket.on("started", ()=>{
    isGameStarted = true;
  })
</script>


<main>
  <GameConfig socket={socket} hidden={isGameStarted}/>
  <Sugoroku socket={socket} started={isGameStarted}/>
</main>


<style>
</style>
