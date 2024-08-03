<template>
    <el-text class="title">{{ title }}</el-text>
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

<style lang="scss" scoped>
  .title {
    display: inline-block;
    font-family: "KaiTi", "楷体", "STKaiti", "楷体_GB2312", serif;
    height: 1.2rem;
    padding: 0.15rem;
    line-height: 1.2rem;
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
    font-weight: bolder;
  }
</style>