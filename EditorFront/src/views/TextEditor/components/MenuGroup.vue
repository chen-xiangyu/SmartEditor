<template>
  <span class="title">{{ title }}</span>
  <template v-for="item in items">
    <MenuItem :item="item as MenuItemType"/>
  </template>
</template>

<script setup lang="ts" name="MenuGroup">
  import MenuItem from './MenuItem.vue'
  import { MenuItemType } from "../../../types"

  const {items, title} = defineProps<{ 
    items: MenuItemType[],
    title: string,
  }>()

</script>

<style scoped>
  .title {
    height: 1.5rem;
    line-height: 1.5rem;
    font-family: "KaiTi", "楷体", "STKaiti", "楷体_GB2312", serif; /* 设置楷体字体 */;
    font-size: 1.4rem;
    /* font-weight: bolder; */
  }
</style>