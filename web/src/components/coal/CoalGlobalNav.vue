<template>
  <header class="coal-nav-shell">
    <div ref="navWrapRef" class="coal-nav">
      <button type="button" class="coal-nav__brand" @click="navigateAndClose('/coal')">
        <span class="coal-nav__logo" aria-hidden="true"></span>
        <span class="coal-nav__brand-copy">淖尔壕智能化选煤厂</span>
      </button>

      <nav class="coal-nav__links" aria-label="coal navigation">
        <div v-for="item in topNavItems" :key="item.path" class="coal-nav__menu-item">
          <button
            type="button"
            class="coal-nav__button"
            :class="{ active: route.path === item.path || item.children.some((child) => route.path === child.path) }"
            @click="toggleTopMenu(item.path)"
          >
            <span class="coal-nav__icon" aria-hidden="true">{{ iconFor(item.path) }}</span>
            <span>{{ item.label }}</span>
          </button>
          <div v-if="openTopMenuPath === item.path && item.children.length" class="coal-nav__dropdown">
            <button
              v-for="child in item.children"
              :key="child.path"
              type="button"
              class="coal-nav__dropdown-item"
              :class="{ active: route.path === child.path }"
              @click="navigateAndClose(child.path)"
            >
              <strong>{{ child.label }}</strong>
              <small>{{ child.desc || '进入该功能页面' }}</small>
            </button>
          </div>
        </div>
      </nav>

      <div class="coal-nav__tools">
        <button type="button" class="coal-nav__tool" title="搜索" aria-label="搜索">⌕</button>
        <button type="button" class="coal-nav__tool coal-nav__tool--notice" title="消息通知" aria-label="消息通知">◎</button>
        <button type="button" class="coal-nav__tool" title="系统设置" aria-label="系统设置" @click="navigateAndClose('/coal/settings')">⚙</button>

        <button type="button" class="coal-nav__avatar" title="个人中心" aria-label="个人中心">管</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  coalExtensionEntriesForHome,
  coalPlatformEntries,
  coalTopicEntries,
  type CoalNavItem,
} from '../../views/coal/coalNav'

const route = useRoute()
const router = useRouter()

const topNavItems: Array<{ label: string; path: string; children: CoalNavItem[] }> = [
  {
    label: '首页',
    path: '/coal',
    children: [
      { label: '平台首页', path: '/coal', desc: '平台总入口与核心导航' },
      { label: '综合看板', path: '/coal/dashboard', desc: '总览、告警、关键指标' },
      { label: '报表中心', path: '/coal/report', desc: '统一报表入口' },
    ],
  },
  {
    label: '生产运行',
    path: '/coal/production',
    children: [
      { label: '生产管理', path: '/coal/production', desc: '生产计划与执行' },
      { label: '调度管理', path: '/coal/dispatch', desc: '交接班与调度记录' },
      ...coalExtensionEntriesForHome.filter((item) =>
        ['/coal/planning', '/coal/process-flow', '/coal/process-check', '/coal/dispatch-log'].includes(item.path),
      ),
    ],
  },
  {
    label: '设备运维',
    path: '/coal/equipment',
    children: [
      { label: '设备管理', path: '/coal/equipment', desc: '设备台账、状态与维护' },
      { label: '备品备件', path: '/coal/spare-parts', desc: '备件库存与预警' },
      { label: '停送电审批', path: '/coal/power-operation', desc: '停电申请、审批、验电、检修、送电闭环' },
      ...coalExtensionEntriesForHome.filter((item) => ['/coal/mechanical'].includes(item.path)),
    ],
  },
  {
    label: '质量与能耗',
    path: '/coal/quality',
    children: [
      { label: '煤质管理', path: '/coal/quality', desc: '煤质分析与趋势预警' },
      { label: '节能与能耗', path: '/coal/energy', desc: '介药水电油风消耗管理' },
      ...coalExtensionEntriesForHome.filter((item) =>
        ['/coal/quality-entry', '/coal/quality-report', '/coal/medium', '/coal/reagent', '/coal/water', '/coal/power'].includes(item.path),
      ),
    ],
  },
  {
    label: '智能优化',
    path: '/coal/decision',
    children: [
      { label: '智能决策', path: '/coal/decision', desc: '工艺与生产优化建议' },
      ...coalExtensionEntriesForHome.filter((item) => ['/coal/model-analysis', '/coal/smart-density', '/coal/smart-reagent'].includes(item.path)),
    ],
  },
  {
    label: '平台与系统',
    path: '/coal/settings',
    children: [
      { label: '系统设置', path: '/coal/settings', desc: '用户、角色、点位与参数' },
      ...coalTopicEntries.filter((item) => ['/coal/monitor', '/coal/collaboration'].includes(item.path)),
      ...coalPlatformEntries,
    ],
  },
]
const navWrapRef = ref<HTMLElement | null>(null)
const openTopMenuPath = ref<string | null>(null)

const navIcons: Record<string, string> = {
  '/coal': '⌂',
  '/coal/dashboard': '▣',
  '/coal/production': '▤',
  '/coal/equipment': '◇',
  '/coal/quality': '◎',
  '/coal/storage': '▥',
  '/coal/energy': '↯',
  '/coal/spare-parts': '▧',
  '/coal/collaboration': '⇄',
  '/coal/dispatch': '⌁',
  '/coal/power-operation': '⎓',
  '/coal/decision': '✦',
  '/coal/monitor': '◌',
  '/coal/settings': '⚙',
  '/coal/report': '▨',
}

function iconFor(path: string) {
  return navIcons[path] || '·'
}

function navigateAndClose(path: string) {
  router.push(path)
  openTopMenuPath.value = null
}

function toggleTopMenu(path: string) {
  openTopMenuPath.value = openTopMenuPath.value === path ? null : path
}

function handleDocumentClick(event: MouseEvent) {
  if (!navWrapRef.value) return
  const target = event.target as Node
  if (!navWrapRef.value.contains(target)) {
    openTopMenuPath.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.coal-nav-shell {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 4000;
  width: 100%;
  padding: 10px 18px 0;
  background: transparent;
  border-bottom: 0;
  box-shadow: none;
}

.coal-nav {
  display: flex;
  align-items: center;
  gap: 28px;
  width: min(100%, 1880px);
  min-height: 90px;
  margin: 0 auto;
  padding: 14px 22px;
  border: 1px solid rgba(112, 207, 255, 0.1);
  border-radius: 20px;
  background:
    linear-gradient(90deg, rgba(18, 105, 165, 0.12), transparent 30%),
    linear-gradient(180deg, rgba(12, 33, 55, 0.38), rgba(7, 18, 31, 0.28));
  box-shadow: inset 0 1px 0 rgba(176, 232, 255, 0.08);
  backdrop-filter: blur(14px);
}

.coal-nav__brand {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  min-width: 380px;
  min-height: 58px;
  padding: 0 16px 0 6px;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.coal-nav__logo {
  position: relative;
  width: 42px;
  height: 42px;
  margin-right: 14px;
  border: 1px solid rgba(108, 238, 255, 0.38);
  border-radius: 14px;
  background:
    radial-gradient(circle at 50% 50%, rgba(111, 245, 255, 0.16), transparent 58%),
    linear-gradient(135deg, rgba(28, 218, 255, 0.28), rgba(34, 108, 180, 0.16));
  box-shadow: 0 0 18px rgba(38, 210, 255, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.coal-nav__logo::before,
.coal-nav__logo::after {
  position: absolute;
  content: '';
  inset: 11px 8px;
  border: 3px solid #86efff;
  border-radius: 50%;
  opacity: 0.84;
}

.coal-nav__logo::before {
  transform: rotate(28deg);
}

.coal-nav__logo::after {
  transform: rotate(-28deg);
}

.coal-nav__brand-copy {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
  color: #f3fbff;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-shadow: 0 0 14px rgba(54, 216, 255, 0.24), 0 2px 2px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
}

.coal-nav__links {
  display: flex;
  flex: 1;
  flex-wrap: nowrap;
  justify-content: space-between;
  gap: 10px 24px;
  min-width: 0;
  padding: 0 12px;
}

.coal-nav__menu-item {
  position: relative;
}

.coal-nav__button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 52px;
  padding: 0 10px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: rgba(229, 243, 255, 0.82);
  font-size: 18px;
  font-weight: 680;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.34);
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.coal-nav__button::after {
  position: absolute;
  right: 6px;
  bottom: 4px;
  left: 6px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(44, 225, 255, 0), rgba(44, 225, 255, 0.92), rgba(44, 225, 255, 0));
  opacity: 0;
  transform: scaleX(0.3);
  transition: 0.2s ease;
  content: '';
}

.coal-nav__icon {
  color: rgba(116, 229, 255, 0.76);
  font-size: 18px;
  line-height: 1;
}

.coal-nav__dropdown {
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  z-index: 20;
  display: grid;
  gap: 8px;
  width: 320px;
  max-height: 56vh;
  padding: 12px;
  overflow-y: auto;
  border: 1px solid rgba(109, 223, 255, 0.28);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(27, 65, 102, 0.98), rgba(12, 26, 45, 0.98));
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transform: translateX(-50%);
}

.coal-nav__dropdown-item {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid rgba(124, 214, 255, 0.16);
  border-radius: 14px;
  background: rgba(14, 27, 39, 0.94);
  color: #ecf8ff;
  text-align: left;
  cursor: pointer;
  transition: 0.2s ease;
}

.coal-nav__dropdown-item strong {
  font-size: 14px;
}

.coal-nav__dropdown-item small {
  color: rgba(218, 236, 252, 0.62);
  line-height: 1.5;
}

.coal-nav__dropdown-item.active,
.coal-nav__dropdown-item:hover {
  border-color: rgba(87, 216, 255, 0.3);
  background: rgba(20, 41, 58, 0.96);
}

.coal-nav__button.active,
.coal-nav__button:hover {
  color: #ffffff;
  background: transparent;
  transform: translateY(-1px);
}

.coal-nav__button.active::after,
.coal-nav__button:hover::after {
  opacity: 1;
  transform: scaleX(1);
}

.coal-nav__tools {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
  padding-left: 8px;
}

.coal-nav__tool,
.coal-nav__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  border: 1px solid rgba(121, 213, 255, 0.16);
  border-radius: 12px;
  list-style: none;
  background: rgba(16, 39, 63, 0.36);
  color: rgba(232, 247, 255, 0.9);
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.coal-nav__tool {
  width: 40px;
  font-size: 20px;
}

.coal-nav__tool--notice {
  position: relative;
}

.coal-nav__tool--notice::after {
  position: absolute;
  top: 8px;
  right: 9px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #2df4d1;
  box-shadow: 0 0 8px rgba(45, 244, 209, 0.82);
  content: '';
}

.coal-nav__avatar {
  width: 40px;
  border-color: rgba(56, 230, 255, 0.34);
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(43, 215, 255, 0.28), rgba(29, 191, 153, 0.18));
  color: #dffcff;
}

.coal-nav__tool:hover,
.coal-nav__avatar:hover {
  border-color: rgba(103, 230, 255, 0.46);
  background: rgba(55, 189, 255, 0.16);
  color: #ffffff;
  transform: translateY(-1px);
}

@media (max-width: 1420px) {
  .coal-nav {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .coal-nav__links {
    justify-content: flex-start;
    width: 100%;
  }

  .coal-nav__links {
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 8px 18px;
  }

  .coal-nav__tools {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 760px) {
  .coal-nav-shell {
    padding: 8px 10px 0;
  }

  .coal-nav__brand {
    min-width: 0;
  }

  .coal-nav__brand-copy {
    font-size: 18px;
  }

  .coal-nav__dropdown {
    left: 0;
    width: min(100vw - 24px, 360px);
    transform: none;
  }
}
</style>
