<script setup lang="ts">
import axios from "axios";
import {ref, reactive} from "vue";


const registerBrands = () => {
  // 銘柄情報を登録する際に使用するものであるため、普段は不活化
  axios.get('/api/register_brands.json').then(res => {
    console.log("registerBrands!")
  })
}

const registerTrades = () => {
  // 取引情報を登録する際に使用するものであるため、普段は不活化
  axios.get('api/register_trades.json').then(res => {
    console.log('registerTrades!')
  })
}
const getNewTrades = () => {
  // 毎日実行するもの。一度実行すると５０分程度時間がかかるため、クリックミスを避けるためにも実行前に確認する。
  const confirmed = confirm("本当に実行しますか？");
  if (confirmed) {
    axios.get('api/get_new_trades.json').then(res => {
      alert('完了しました')
    })
  } else {
    alert('処理を中断しました。')
  }
}
const analyze = () => {
  // 取得してきた取引情報を元に、チャートを生成する。
  axios.get('api/analyze.json').then(res => {
  })
}
window.onload = () => {
  // 画面更新時に実行するもの
  show()
  let date = new Date()
  let year = date.getFullYear()
  let month = date.getMonth() + 1
  let day = date.getDate()

  let toTwoDigits = (num, digit) => {
    num += ''
    if (num.length < digit) {
      num = '0' + num
    }
    return num
  }
  let yyyy = toTwoDigits(year, 4)
  let mm = toTwoDigits(month, 2)
  let dd = toTwoDigits(day, 2)
  let ymd = yyyy + "-" + mm + "-" + dd
  document.getElementById('judge_date').value = ymd
}

const reg_judge = () => {
  // 投資判断等を記録するもの。
  target_brand_code.value = document.getElementById('brand_code').innerText
  let is_holding = document.getElementById('is_holding')
  let is_watching = document.getElementById('is_watching')
  let judge_date = document.getElementById('judge_date')
  let judge_text = document.getElementById('judge_text')
  let judge_trend = document.querySelector('input[name="judge_trend"]:checked')

  axios.post('api/reg_judge', {
    brand_code: target_brand_code.value,
    // 銘柄のstatesを変更するもの。
    is_holding: is_holding.checked,
    is_watching: is_watching.checked,
    // 投資判断を登録するもの。
    judge_date: judge_date.value,
    judge_text: judge_text.value,
    judge_trend: judge_trend.value
  }).then(res => {
    document.getElementById('judge_text').value = '';
    for (const elem of document.getElementsByName('judge_trend')) {
      elem.checked = false;
    }
  })
  alert('登録しました')
}
const target_brand_code = ref('')
const is_holding = ref<boolean>()
const is_watching = ref<boolean>()
const judge_trend = ref('')
const judge_text = ref('')
const zero = ref("")
const p2 = ref('')
const p1 = ref('')
const m2 = ref('')
const m1 = ref('')
const holding = ref('')
const watching = ref('')
const judged_date = ref('')
const judged_trend = ref('')
const judged_text = ref('')

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
    holding.value = JSON.parse(res.data.holding)
    watching.value = JSON.parse(res.data.watching)
  })
}
const drawing = (url) => {
  img.value = url
  const index = url.indexOf('【')
  brand_code.value = url.slice(index + 1, index + 8)
  brand_name.value = url.slice(index + 10, url.indexOf('】'))
  brand_url.value = 'https://kabutan.jp/stock/news?code=' + brand_code.value.slice(0, 4)

  axios.post('api/get_states.json', {brand_code: brand_code.value}).then(res => {
    document.getElementById('is_holding').checked = res.data.is_holding;
    document.getElementById('is_watching').checked = res.data.is_watching;
    if ('judge_date' in res.data) {
      judged_date.value = res.data.judge_date
      judged_trend.value = res.data.judge_trend
      judged_text.value = res.data.judge_text
    } else {
      judged_date.value = ""
      judged_trend.value = ""
      judged_text.value = ""
    }
  })
}
const temp1 = ref('')
const survey=()=>{
  axios.get('api/survey').then(res=>{
    temp1.value = res.data.kind
    console.log(temp1.value)
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
        <li><a href="" @click.prevent="getNewTrades">最新の取引情報を取得</a></li>
        <li><a href="" @click.prevent="survey">新・画像生成</a></li>
<!--        <li><a href="" @click.prevent="analyze">画像生成</a></li>-->
<!--        <li><a href="" @click.prevent="show">画像表示</a></li>-->
      </ul>
    </nav>
    <div id="contents">
      <div id="main">
        <img :src="img" alt="" height="600" width="400">
<!--        <img :src="img" alt="" height="600" width="775">-->
      </div>
      <div id="left">
        <p>holding</p>
        <ul>
          <li v-for="p in holding"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{
              p.brand
            }}</a>
          </li>
        </ul>
        <p>watching</p>
        <ul>
          <li v-for="p in watching"><a @click.prevent="drawing(p.filename)" :href="p.filename">{{ p.rsi }} : {{
              p.brand
            }}</a>
          </li>
        </ul>
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
      <div id="right" style="padding-left: 10px">
        <h5 style="margin-bottom: 0"><span id="brand_code">{{ brand_code }}</span>　<span>{{ brand_name }}</span></h5>
        <a :href="brand_url" target="_blank">株探リンク</a><br><br>
        <input type="date" id="judge_date"><br>
        <input type="checkbox" id="is_holding"><label for="is_holding">保有フラグ</label><br>
        <input type="checkbox" id="is_watching"><label for="is_watching">監視フラグ</label><br>
        <input type="radio" name="judge_trend" value="up">上昇
        <input type="radio" name="judge_trend" value="down">下降
        <textarea id="judge_text" cols="40" rows="10"></textarea><br>
        <button class="styled" type="button" @click="reg_judge">save</button>
        <div id="history" v-show="judged_date" style="background-color: rgba(198,210,238,1)">
          <p>{{ judged_date }}</p>
          <p>{{ judged_trend }}</p>
          <p>{{ judged_text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#wrapper {
  border: red 3px solid;
  width: 100%;
  height: 670px;
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
  height: 610px;
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
