<template>
  <div class="workflow-design-page">
    <WorkflowDesigner />
  </div>
</template>

<script setup lang="ts">
import WorkflowDesigner from './WorkflowDesigner.vue'
</script>

<style scoped>
.workflow-design-page {
  height: 100%;
  width: 100%;
  overflow: auto;
}
</style>
