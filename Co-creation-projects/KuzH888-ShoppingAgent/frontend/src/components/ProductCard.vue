<script setup lang="ts">
import { Backpack, Eye, Headphones, House, MessageCircle, Scale, Star } from '@lucide/vue'
import { computed } from 'vue'

import { useChatStore } from '@/stores/chat'
import { useStorefrontStore } from '@/stores/storefront'
import type { Product } from '@/types/api'

const props = defineProps<{ product: Product }>()
const chat = useChatStore()
const storefront = useStorefrontStore()
const isCompared = computed(() => storefront.compareIds.includes(props.product.id))

const visual = computed(() => {
  if (props.product.category === 'digital_accessories') {
    return { icon: Headphones, label: '数码配件', className: 'digital' }
  }
  if (props.product.category === 'home_office') {
    return { icon: House, label: '居家办公', className: 'home' }
  }
  return { icon: Backpack, label: '旅行生活', className: 'travel' }
})

const featureLabels: Record<string, string> = {
  active_noise_cancellation: '主动降噪',
  adjustable_brightness: '亮度可调',
  adjustable_colour_temperature: '色温可调',
  adjustable_speed: '风速可调',
  airline_friendly: '适合航空出行',
  battery_display: '电量显示',
  bluetooth: '蓝牙',
  bpa_free: '不含 BPA',
  breathable: '透气',
  built_in_microphone: '内置麦克风',
  cable_management: '线材收纳',
  carry_on_friendly: '可随身登机',
  carry_pouch: '附收纳袋',
  ceramic_lined: '陶瓷内胆',
  child_resistant: '儿童防护',
  clip_on: '夹式设计',
  comfortable_earcups: '舒适耳罩',
  compact: '小巧',
  desk_stand: '桌面支架',
  dual_port: '双接口',
  durable: '耐用',
  easy_clean: '易清洁',
  lightweight: '轻便',
  ergonomic: '人体工学',
  expandable: '可扩展',
  fast_charging: '快速充电',
  foldable: '可折叠',
  gan: '氮化镓',
  handheld: '可手持',
  height_adjustable: '高度可调',
  hidden_pocket: '隐藏口袋',
  high_capacity: '大容量',
  high_fidelity_audio: '高保真音质',
  inflatable: '可充气',
  portable: '便携',
  eye_care: '护眼',
  water_resistant: '防泼水',
  insulated: '保温',
  laptop_compartment: '笔记本隔层',
  leak_resistant: '防漏杯盖',
  leakproof: '防漏',
  memory_foam: '记忆棉',
  modular: '模块化',
  multi_device: '多设备',
  multi_port: '多接口',
  neck_support: '颈部支撑',
  non_slip: '防滑',
  privacy_friendly: '隐私友好',
  qr_contact: '二维码联系',
  quiet: '静音',
  quiet_keys: '静音按键',
  rechargeable: '可充电',
  shoe_compartment: '鞋履隔层',
  six_piece_set: '六件套',
  ultralight: '超轻',
  usb_c: 'USB-C',
  usb_c_power: 'USB-C 供电',
  ventilated: '通风散热',
  washable: '可清洗',
  washable_cover: '可洗外套',
  wired_mode: '有线模式',
  wireless: '无线',
  wrist_rest: '腕托',
}

function askAboutProduct() {
  chat.openWithPrompt(`请介绍 ${props.product.name.zh}（${props.product.id}），它适合什么需求？`)
}
</script>

<template>
  <article class="product-card">
    <div class="product-visual" :class="visual.className">
      <span>{{ visual.label }}</span>
      <component :is="visual.icon" :size="54" :stroke-width="1.45" aria-hidden="true" />
      <small>{{ product.id }}</small>
    </div>

    <div class="product-content">
      <div class="rating-row">
        <span><Star :size="15" fill="currentColor" /> {{ product.rating }}</span>
        <span>{{ product.review_count }} 条评价</span>
      </div>
      <h3>{{ product.name.zh }}</h3>
      <p>{{ product.description.zh }}</p>

      <div class="feature-list" aria-label="商品功能">
        <span v-for="feature in product.features.slice(0, 3)" :key="feature">
          {{ featureLabels[feature] ?? feature.replaceAll('_', ' ') }}
        </span>
      </div>

      <div class="product-footer">
        <div>
          <strong>{{ product.currency }} {{ product.price.toFixed(2) }}</strong>
          <small>{{ product.stock > 0 ? `现货 ${product.stock} 件` : '暂时缺货' }}</small>
        </div>
        <button type="button" :aria-label="`咨询 ${product.name.zh}`" @click="askAboutProduct">
          <MessageCircle :size="18" />问客服
        </button>
      </div>
      <div class="product-secondary-actions">
        <button type="button" @click="storefront.openDetails(product)">
          <Eye :size="16" />查看详情
        </button>
        <button
          type="button"
          :class="{ selected: isCompared }"
          :disabled="!isCompared && storefront.compareIds.length >= 3"
          @click="storefront.toggleCompare(product.id)"
        >
          <Scale :size="16" />{{ isCompared ? '取消对比' : '加入对比' }}
        </button>
      </div>
    </div>
  </article>
</template>
