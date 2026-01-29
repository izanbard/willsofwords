export interface Cell {
  loc_x: number
  loc_y: number
  value: string
  is_answer: boolean
  is_profane: boolean
  direction: { NS: boolean; EW: boolean; NESW: boolean; NWSE: boolean }
}

export interface FoundProfanity {
  word: string
  accepted: boolean
  direction: string
  word_range: number[]
  coords: number[][]
}

export interface PuzzleData {
  project_config: Record<string, string | number | boolean>
  puzzle_id: string
  puzzle_title: string
  display_title: string
  input_word_list: string[]
  long_fact: string
  short_fact: string
  rows: number
  columns: number
  cells: Cell[][]
  puzzle_search_list: string[]
  density: number
  profanity: Record<string, FoundProfanity[]>
}

export interface PuzzleBaseData {
  title: string
  puzzle_list: string[]
  page_count: number
}

export interface Category {
  category: string
  word_list: string[]
  short_fact: string
  long_fact: string
}

export interface Wordlist {
  title: string
  category_prompt: string
  wordlist_prompt: string
  creation_date: string
  category_list: Category[]
}
