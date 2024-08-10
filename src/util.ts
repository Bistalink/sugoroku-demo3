export type Player = {
  name: string,
  position: number,
  sid: string
}

export type GameState = {
  players: Player[],
  currentPlayer: number,
  goal: number,
  turn: number
}

export type PlayerState = {
  name: string,
  playable: boolean,
}