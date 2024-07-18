<template>
  <div class="container">
    <bubble-menu
      :editor="props.editor"
      :tippy-options="{ 
        placement: 'bottom-start',
        duration: 100
      }"
      v-if="editor"
    >
      <button class="menu-item" :title="'人工智能'" ref="buttonRef" @click="show">
        <svg class="remix">
          <use :xlink:href="`${remixiconUrl}#ri-${'robot-2-line'}`" />
        </svg>
      </button>
      <MenuGroup :title="''" :items="textHandleItems"/>
    </bubble-menu>
  </div>

</template>

<script setup lang="ts" name="SelectionBubbleMenu">
  import { ref } from 'vue'
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  import { BubbleMenu, Editor } from '@tiptap/vue-3'
  import MenuGroup from './MenuGroup.vue'
  const props = defineProps<{ editor: Editor, showDataModal: any }>()
  
  const buttonRef = ref()
  function show(){
    if (buttonRef.value) {
      const buttonRect = buttonRef.value.getBoundingClientRect()
      props.showDataModal(buttonRect.bottom, buttonRect.left)
    }
  }
  
  const textHandleItems = [
    {
      icon: 'bold',
      title: 'Bold',
      action: () => props.editor?.chain().focus().toggleBold().run(),
      isActive: () => props.editor?.isActive('bold')
    },
    {
      icon: 'italic',
      title: 'Italic',
      action: () => props.editor?.chain().focus().toggleItalic().run(),
      isActive: () => props.editor?.isActive('italic')
    },
    {
      icon: 'strikethrough',
      title: 'Strike',
      action: () => props.editor?.chain().focus().toggleStrike().run(),
      isActive: () => props.editor?.isActive('strike')
    },
    {
      icon: 'code-view',
      title: 'Code',
      action: () => props.editor?.chain().focus().toggleCode().run(),
      isActive: () => props.editor?.isActive('code')
    },
    {
      icon: 'subscript',
      title: 'Subscript',
      action: () => props.editor?.chain().focus().toggleSubscript().run(),
      isActive: () => props.editor?.isActive('subscript')
    },
    {
      icon: 'superscript',
      title: 'Superscript',
      action: () => props.editor?.chain().focus().toggleSuperscript().run(),
      isActive: () => props.editor?.isActive('superscript')
    },
    {
      icon: 'underline',
      title: 'Underline',
      action: () => props.editor?.chain().focus().toggleUnderline().run(),
      isActive: () => props.editor?.isActive('underline')
    },
  ]
</script>

<style lang="scss" scoped>

  .container {
    position: relative;
    /* 确保容器内部的定位正确 */
  }
/* Bubble menu */
  .bubble-menu {
    background-color: var(--white);
    border: 1px solid var(--gray-1);
    border-radius: 0.7rem;
    box-shadow: var(--shadow);
    display: flex;
    padding: 0.2rem;

    button {
      background-color: unset;

      &:hover {
        background-color: var(--gray-3);
      }

      &.is-active {
        background-color: var(--purple);

        &:hover {
          background-color: var(--purple-contrast);
        }
      }
    }
  }

  .menu-item {
    background: transparent;
    border: none;
    border-radius: 0.4rem;
    color: #333;
    cursor: pointer;
    height: 1.75rem;
    padding: 0.25rem;
    margin-right: 0.25rem;
    width: 1.75rem;

    svg {
      fill: currentColor;
      height: 100%;
      width: 100%;
    }

    &.is-active,
    &:hover {
      background-color: #d6d6d6;
    }
  }
</style>