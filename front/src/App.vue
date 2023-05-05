<script setup lang="ts">
import axios from "axios";
import {ref, reactive} from "vue";

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
const zero = ref("")
const p2 = ref('')
const p1 = ref('')
const m2 = ref('')
const m1 = ref('')

const img = ref('')

const brand_code = ref('')
const brand_name = ref('')
const show = () => {
  axios.get('api/show.json').then(res => {
    zero.value = JSON.parse(res.data.zero)
    p2.value = JSON.parse(res.data.p2)
    p1.value = JSON.parse(res.data.p1)
    m2.value = JSON.parse(res.data.m2)
    m1.value = JSON.parse(res.data.m1)
    console.log(p2.value)
  })
}
const drawing =(url)=>{
  console.log('drawing')
  console.log(url)
  img.value = url
  const index = url.indexOf('【')
  brand_code.value = url.slice(index+1, index+8)
  console.log(brand_code.value)
  brand_name.value = url.slice(index+10, url.indexOf('】'))
  console.log(brand_name.value)
}
</script>

<template>
  <div id="wrapper">
    <nav>
      <ul>
        <li><a href="http://localhost:8000/admin/">管理画面</a></li>
        <!--        <li><a href="" @click.prevent="registerBrands">regB</a></li>-->
        <!--        <li><a href="" @click.prevent="registerTrades">regT</a></li>-->
        <li><a href="" @click.prevent="getNewTrades">最新の取引情報を取得</a></li>
        <li><a href="" @click.prevent="analyze">画像生成</a></li>
        <li><a href="" @click.prevent="show">画像表示</a></li>
      </ul>
    </nav>
    <div id="contents">
      <div id="left">
        <p>p2</p>
        <ul>
          <li v-for="p in p2"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{p.rsi}} : {{p.brand}}</a></li>
        </ul>
        <p>p1</p>
        <ul>
          <li v-for="p in p1"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{p.rsi}} : {{p.brand}}</a></li>
        </ul>
        <p>m2</p>
        <ul>
          <li v-for="p in m2"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{p.rsi}} : {{p.brand}}</a></li>
        </ul>
        <p>m1</p>
        <ul>
          <li v-for="p in m1"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{p.rsi}} : {{p.brand}}</a></li>
        </ul>
        <p>zero</p>
        <ul>
          <li v-for="p in zero"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{p.rsi}} : {{p.brand}}</a></li>
        </ul>
      </div>
      <div id="main">
        <img :src="img" alt="" height="550" width="775">
      </div>
      <div id="right">

      </div>
    </div>
  </div>
</template>

<style scoped>
#wrapper {
  border: red 3px solid;
  width: 100%;
  height: 610px;
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
  width: 165px;
  height: 550px;
  border: blueviolet solid 3px;
  float: left;
  overflow-x: scroll;
  white-space: nowrap;
}

#main {
  width: 950px;
  height: 550px;
  border: #E7DA66 solid 2px;
}


</style>
