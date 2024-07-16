import { defineStore} from 'pinia'
import { h, ref, type Component } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  const headings = ref()
  const activeHeading = ref()
  const editorInstance = ref()
  const setHeadings = (data: any) => {
    headings.value = data
  }
  const setActiveHeading = (data: any) => {
    activeHeading.value = data
  }
  const setEditorInstance = (data: any) => {
    console.log(editorInstance.value)

    editorInstance.value = data
  }
  return {
    headings,
    setHeadings,
    activeHeading,
    setActiveHeading,
    editorInstance,
    setEditorInstance
  }
})
