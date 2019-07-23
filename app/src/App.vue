<template>
  <div id="app">
    <router-view :key="`${$route.path}:${$route.query.url}`"/>
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
  font: 16px/1.2 'Share', 'Arial', 'serif';
}
p,
h2 {
  margin: 0;
  padding: 0;
}
a {
  padding: 4px;
  color: #fff;
    transition: all 150ms ease;
  &:hover {
    background: white;
    color: #000;
  }
}
</style>
