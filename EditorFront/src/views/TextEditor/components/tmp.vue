<!-- <template v-if="visibleChart">
  <div :style="{ width: '600px', height: '350px' }">
    <EChart ref="chartRef" :option="chartOption" width="500px" height="300px"/>
  </div>
  
</template>
<template v-else>
  <el-input
    v-model="cardMsg"
    :autosize="{ minRows: 1, maxRows: 16 }"
    type="textarea"
    :placeholder="textPrompt"
  />
  <template v-if="isMultiMedia">
    <el-button type="primary" @mousedown="copyText()">复制</el-button>
  </template>
  <template v-else>
    <el-button type="primary" @mousedown="replace()">替换</el-button>
    <el-button type="success" @mousedown="append()">追加</el-button>
  </template>
</template>
<el-button type="info" @mousedown="ignore()">舍弃</el-button>
</el-card> -->