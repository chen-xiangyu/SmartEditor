<template>
  <div ref="mapRef" :style="{ width: props.width, height: props.height }"></div>
</template>

<script setup lang="ts" name="MindMap">
  import { onMounted, ref } from 'vue'
  import MindElixir, { MindElixirInstance, Options, MindElixirData } from 'mind-elixir'

  const props = defineProps<{
    width: string,
    height: string,
    data: MindElixirData,
  }>()

  const mapRef = ref<HTMLDivElement | null>(null)
  let mind: MindElixirInstance | null = null

  onMounted(() => {
    console.log("on mind map mounted", props.data)
    if (mapRef.value) {
      const options: Options = {
        el: mapRef.value,
        locale: 'zh',
      }
      mind = new MindElixir(options)
      mind.init(props.data)
    }
  })

  const exportAsBase64 = async (type: 'png' | 'svg'): Promise<string | null> => {
    try {
      let blob: Blob | null = null
      if (type === 'png') {
        blob = await mind?.exportPng(false)
      } else {
        blob = await mind?.exportSvg(false)
      }

      if (!blob) return null;

      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          if (typeof reader.result === 'string') {
            resolve(reader.result);
          } else {
            reject('Failed to convert blob to base64.');
          }
        };
        reader.onerror = () => {
          reject('Failed to read blob as base64.');
        };
      });
      console.log("get base64")
      reader.readAsDataURL(blob);
      return await base64Promise;
    } catch (e) {
      console.error('Error exporting as base64:', e);
      return null;
    }
  };

  // const handleExportAsBase64 = async (type: 'png' | 'svg') => {
  //   const base64 = await exportAsBase64(type);
  //   if (base64) {
  //     console.log(`Base64 (${type}):`, base64);
  //   } else {
  //     console.error('Failed to export base64.');
  //   }
  // };

  defineExpose({ exportAsBase64 })
</script>