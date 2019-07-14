<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style lang="scss">
html {
  box-sizing: border-box;
}
*, *:before, *:after {
  box-sizing: inherit;
}
body {
  margin: 0;
  padding: 0;
  background: #000;
  color: #fff;
  font: 16px/1.5 'Share', 'Arial', 'serif';
}
p,
h2 {
  margin: 0;
  padding: 0;
}
</style>
