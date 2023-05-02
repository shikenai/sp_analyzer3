<script setup lang="ts">
import axios from "axios";
const registerBrands=()=>{
  axios.get('/api/register_brands.json').then(res=>{
    console.log("registerBrands!")
  })
}
const registerTrades=()=>{
  axios.get('api/register_trades.json').then(res=>{
    console.log('registerTrades!')
  })
}
</script>

<template>
  <div id="wrapper">
    <nav>
      <ul>
        <li><a href="http://localhost:8000/admin/">管理画面</a></li>
        <li><a href="" @click.prevent="registerBrands">regB</a></li>
        <li><a href="" @click.prevent="registerTrades">regT</a></li>
        <li><a href="">test3</a></li>
      </ul>
    </nav>
    <div id="contents">
      <p>asdf</p>
    </div>
  </div>
</template>

<style scoped>
#wrapper {
  border: red 3px solid;
  width: 100%;
}

nav {
  text-align: center;
  height: 90px;
  border: #1a1a1a 2px solid;
}

nav ul {
  /*margin: 10px;*/
  /*padding: 0;*/
  vertical-align: middle;
}

nav ul li {
  border: blue 1px dot-dash;
  list-style: none;
  display: inline-block;

  width: 18%;
  min-width: 90px;
}

nav ul li a {
  text-decoration: none;
  color: #333;
}

nav ul li.current a {
  color: #F33135;
}

nav ul li a:hover {
  color: #E7DA66;
}
</style>
