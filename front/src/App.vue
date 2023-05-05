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
  const confirmed = confirm("本当に実行しますか？");
  if (confirmed) {
    axios.get('api/get_new_trades.json').then(res => {
      console.log('get new trades')
    })
  } else {
    alert('処理を中断しました。')
  }
}
const analyze = () => {
  axios.get('api/analyze.json').then(res => {
    console.log('analyze')
  })
}
window.onload = () => {
  show()
}
const reg_judge=()=>{
  console.log('judge')
  target_brand_code.value = document.getElementById('brand_code').innerText
  console.log(target_brand_code.value)
  axios.post('api/post',{data: 'example'}).then(res=>{
    console.log('posted')
  })
}
const target_brand_code = ref('')
const zero = ref("")
const p2 = ref('')
const p1 = ref('')
const m2 = ref('')
const m1 = ref('')

const img = ref('')

const brand_code = ref('')
const brand_name = ref('')
const brand_url = ref('')
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
const drawing = (url) => {
  console.log('drawing')
  console.log(url)
  img.value = url
  const index = url.indexOf('【')
  brand_code.value = url.slice(index + 1, index + 8)
  brand_name.value = url.slice(index + 10, url.indexOf('】'))
  brand_url.value = 'https://kabutan.jp/stock/news?code=' + brand_code.value.slice(0, 4)
  console.log(brand_url)
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
          <li v-for="p in p2"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{ p.brand }}</a>
          </li>
        </ul>
        <p>p1</p>
        <ul>
          <li v-for="p in p1"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{ p.brand }}</a>
          </li>
        </ul>
        <p>m2</p>
        <ul>
          <li v-for="p in m2"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{ p.brand }}</a>
          </li>
        </ul>
        <p>m1</p>
        <ul>
          <li v-for="p in m1"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{ p.brand }}</a>
          </li>
        </ul>
        <p>zero</p>
        <ul>
          <li v-for="p in zero"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} :
            {{ p.brand }}</a></li>
        </ul>
      </div>
      <div id="main" v-show="img">
        <img :src="img" alt="" height="540" width="775">
      </div>
      <div id="right" v-show="brand_url">
        <h5 style="margin-bottom: 0"><span id="brand_code">{{ brand_code }}</span>　<span>{{ brand_name }}</span></h5>
        <a :href="brand_url" target="_blank">株探リンク</a><br>
        <button class="styled" type="button" @click="reg_judge">save</button>
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

#contents {
  display: flex;
  flex-direction: row;
  height: 550px;
}

#left {
  flex: 1;
  border: blueviolet solid 3px;
  overflow-x: scroll;
  white-space: nowrap;
}

#left p {
  margin: 0;
  padding-left: 5px;
}

#left ul {
  margin-top: 0;
  padding-top: 0;
}

#main {
  flex: 2;
  border: #E7DA66 solid 2px;
}

#right {
  flex: 1;
  border: green solid 1px;
}

.styled {
    border: 0;
    line-height: 2.5;
    padding: 0 20px;
    font-size: 1rem;
    text-align: center;
    color: #fff;
    text-shadow: 1px 1px 1px #000;
    border-radius: 10px;
    background-color: rgba(220, 0, 0, 1);
    background-image: linear-gradient(to top left, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2) 30%, rgba(0, 0, 0, 0));
    box-shadow: inset 2px 2px 3px rgba(255, 255, 255, 0.6), inset -2px -2px 3px rgba(0, 0, 0, 0.6);
}

.styled:hover {
    background-color: rgba(255, 0, 0, 1);
}

.styled:active {
    box-shadow: inset -2px -2px 3px rgba(255, 255, 255, 0.6), inset 2px 2px 3px rgba(0, 0, 0, 0.6);
}

</style>
