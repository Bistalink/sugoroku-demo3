export type Player = {
  name: string,
  position: number,
  sid: string,
  level: number,
  skip: boolean
}

export type GameState = {
  players: Player[],
  currentPlayer: number,
  goal: number,
  turn: number,
  event_list: number[],
  log: string[]
}

export type RequestedQuestion = {
  content: [string, string],
  question_idx: number,
  sid: string
}