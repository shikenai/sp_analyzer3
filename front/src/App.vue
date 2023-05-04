<script setup lang="ts">
import axios from "axios";
import {reactive} from "vue";

const registerBrands = () => {
  axios.get('/api/register_brands.json').then(res => {
    console.log("registerBrands!")
  })
}
const registerTrades = () => {
  axios.get('api/register_trades.json').then(res => {
    console.log('registerTrades!')
  })
}
const getNewTrades = () => {
  axios.get('api/get_new_trades.json').then(res => {
    console.log('get new trades')
  })
}
const analyze = () => {
  axios.get('api/analyze.json').then(res => {
    console.log('analyze')
  })
}
const show =()=>{
  axios.get('api/show.json').then(res =>{
    console.log('show')
    console.log(res.data.zero)
    console.log(res.data.p1)
    console.log(res.data.p2)
    console.log(res.data.m1)
    console.log(res.data.m2)
  })
}



</script>

<template>
  <div id="wrapper">
    <nav>
      <ul>
        <li><a href="http://localhost:8000/admin/">管理画面</a></li>
        <!--        <li><a href="" @click.prevent="registerBrands">regB</a></li>-->
        <!--        <li><a href="" @click.prevent="registerTrades">regT</a></li>-->
        <li><a href="" @click.prevent="getNewTrades">get daily Trades</a></li>
        <li><a href="" @click.prevent="analyze">analyze</a></li>
        <li><a href="" @click.prevent="show">show</a></li>
      </ul>
    </nav>
    <div id="contents">
      <div id="left">
        <ul>
          <li v-for="p in p2">
            {{p}}
          </li>
        </ul>
      </div>
      <div id="main">

      </div>
<!--      <img src="/src/assets/img/0【9989.jp  サンドラッグ】(0;82).png" alt="" height="500" width="900">-->
    </div>
  </div>
</template>

<style scoped>
#wrapper {
  border: red 3px solid;
  width: 100%;
  height: 550px;
}

nav {
  text-align: center;
  height: 60px;
  border: #1a1a1a 1px solid;
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

#left {
  width: 90px;
  height: 490px;
  border: blueviolet solid 3px;
  float: left;
}
#main{
  width: 1025px;
  height: 490px;
  border: #E7DA66 solid 2px;
}


</style>
