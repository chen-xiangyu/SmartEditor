<template>
  <div ref="chartRef" :style="{ width: props.width, height: props.height }"></div>
</template>

<script setup lang="ts" name="EChart">
  import { ref, watch, onMounted, onBeforeUnmount, defineProps } from 'vue'
  import { ECharts, EChartsOption, init } from 'echarts'

  const props = defineProps<{
    width: string,
    height: string,
    option: EChartsOption,
  }>()

  const chartRef = ref<HTMLDivElement | null>(null)
  let chart: ECharts | undefined
  let timer: ReturnType<typeof setTimeout> | undefined
  let title = ""

  // 初始化echarts
  const initChart = (): void => {
    if (chart !== undefined) {
      chart.dispose()
    }
    if (chartRef.value !== null) {
      chart = init(chartRef.value)
      // 拿到option配置项，渲染echarts
      chart?.setOption(props.option, true)
      if (Array.isArray(props.option.title)) {
        // 如果是数组，取第一个标题的 text 属性
        title = props.option.title[0]?.text || ''
      } else if (props.option.title) {
        // 如果是对象，直接取 text 属性
        title = props.option.title.text || ''
      }
    }
  }

  // 重新渲染echarts
  const resizeChart = (): void => {
    if (timer !== undefined) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      if (chart) {
        chart.resize()
      }
    }, 500)
  }

  onMounted(() => {
    initChart()
    window.addEventListener('resize', resizeChart)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeChart)
    if (timer !== undefined) {
      clearTimeout(timer)
    }
  })

  // 获取图表的Base64字符串
  const getChartBase64 = (): string | undefined => {
    if (chart) {
      return chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
    }
    return undefined
  }

  watch(
    () => props.option,
    () => {
      initChart()
    },
    {
      deep: true
    }
  )
  defineExpose({ getChartBase64, title })
</script>
