<template>
  <router-view />
  <Toast />
</template>

<script setup lang="ts">
import Toast from '@/components/common/Toast.vue'
</script>

<style>
@import '@/assets/css/tokens.css';
@import '@/assets/css/base.css';
@import '@/assets/css/utilities.css';
</style>
