<script setup lang="ts">
import InputBlock from '@/components/InputBlock.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import ButtonBox from '@/components/ButtonBox.vue'
import axios from 'axios'
import { ref } from 'vue'
import { useToast } from 'vue-toast-notification'
import GridTile from '@/components/GridTile.vue'

interface Cell {
  loc_x: number
  loc_y: number
  value: string
  is_answer: boolean
  direction: { NS: boolean; EW: boolean; NESW: boolean; NWSE: boolean }
}

const { project_name, puzzle_id, columns, rows } = defineProps<{
  project_name: string
  puzzle_id: string
  columns: number
  rows: number
}>()

const cells = defineModel<Cell[][]>({
  required: false,
  default: undefined,
})
const emit = defineEmits(['reload'])

const co_ords = ref({
  x_value: -1,
  y_value: -1,
  cell: undefined as Cell | undefined,
})
const change_letter_confirm = ref<boolean>(false)
const new_letter = ref<string>('')
const toast = useToast()

const set_target_letter = (x: number, y: number, cell: Cell) => {
  if (x > columns || y > rows) {
    toast.error('Please select a valid cell')
    return
  }
  if (cell.is_answer) {
    toast.error('Cannot change answer cell')
    return
  }

  co_ords.value.x_value = x
  co_ords.value.y_value = y
  co_ords.value.cell = cell
  change_letter_confirm.value = true
}
const change_letter = async () => {
  if (co_ords.value.x_value === -1 || co_ords.value.y_value === -1 || !co_ords.value.cell) {
    toast.error('Please select a cell first')
    return
  }
  if (new_letter.value === '') {
    toast.error('Please select a letter first')
    return
  }
  await axios
    .put(
      `/projects/project/${project_name}/puzzledata/puzzle/${puzzle_id}/cell/${co_ords.value.x_value}/${co_ords.value.y_value}/`,
      { letter: new_letter.value },
    )
    .then(() => {
      toast.success('Letter changed successfully')
      emit('reload')
      co_ords.value.x_value = -1
      co_ords.value.y_value = -1
      co_ords.value.cell = undefined
      new_letter.value = ''
    })
    .catch((error) => {
      toast.error('Error changing letter:', error.message)
    })
  change_letter_confirm.value = false
}
</script>

<template>
  <div class="puzzle_grids">
    <div class="puzzle_grid">
      <div class="grid_title">Puzzle Grid</div>
      <template v-for="(row, y) in cells" :key="y">
        <template v-for="(cell, x) in row" :key="x">
          <GridTile @pressed="set_target_letter(x, y, cell)">{{ cell.value }}</GridTile>
        </template>
      </template>
    </div>
    <div class="puzzle_grid">
      <div class="grid_title">Solution Grid</div>
      <template v-for="(row, y) in cells" :key="y">
        <template v-for="(cell, x) in row" :key="x">
          <GridTile @pressed="true" :solution="true" :directions="cell.direction">{{
            cell.value
          }}</GridTile>
        </template>
      </template>
    </div>
  </div>
  <div class="confirm_container" v-if="change_letter_confirm">
    <div class="card modal">
      <HeadingBlock :level="2">Change to:</HeadingBlock>
      <InputBlock
        type="select"
        v-model="new_letter"
        :options="[
          'A',
          'B',
          'C',
          'D',
          'E',
          'F',
          'G',
          'H',
          'I',
          'J',
          'K',
          'L',
          'M',
          'N',
          'O',
          'P',
          'Q',
          'R',
          'S',
          'T',
          'U',
          'V',
          'W',
          'X',
          'Y',
          'Z',
        ]"
        >New Letter:
      </InputBlock>
      <div class="actions">
        <ButtonBox icon="check_circle" text="Proceed" colour="green" @pressed="change_letter()" />
        <ButtonBox
          icon="cancel"
          text="Cancel"
          colour="indigo"
          @pressed="change_letter_confirm = false"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.confirm_container {
  position: fixed;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5);
  width: 100%;
  height: 100%;
}

.modal {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.actions {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  align-items: center;
}
.puzzle_grids {
  display: flex;
  justify-content: space-evenly;
  margin: 0.5em;
}
.puzzle_grid {
  display: grid;
  --puzzle-rows: v-bind(rows);
  --puzzle-columns: v-bind(columns);
  grid-template-columns: repeat(var(--puzzle-columns), 1.3em);
  grid-template-rows: repeat(var(--puzzle-rows) + 1, 1.3em);
  border: 1px solid var(--color-border);
}
.grid_title {
  grid-column: 1/-1;
  margin: 0.5em;
  place-self: center;
}
.grid_square {
  border: 1px solid var(--color-border);
  padding: 0.15em;
  text-align: center;
  cursor: pointer;
  position: relative;
}
.NS::after {
  content: '';
  border-left: 2px solid var(--vt-c-black);
  height: 1.45em;
  position: absolute;
  left: 50%;
  top: -0.1em;
}
.EW::after {
  content: '';
  border-top: 2px solid var(--vt-c-black);
  width: 1.35em;
  position: absolute;
  left: -0.1em;
  top: 50%;
}
.NESW::after {
  content: '';
  position: absolute;
  top: 100%;
  left: -0.1em;
  width: 1.93em;
  height: 0;
  border-top: 2px solid var(--vt-c-black);
  transform: rotate(-47.5deg);
  transform-origin: left top;
}
.NWSE::after {
  content: '';
  position: absolute;
  top: -0.1em;
  left: 0;
  width: 1.93em;
  height: 0;
  border-bottom: 2px solid var(--vt-c-black);
  transform: rotate(47.5deg);
  transform-origin: left top;
}
.is_answer {
  background-color: var(--vt-c-green-trans-bkg);
}
</style>
