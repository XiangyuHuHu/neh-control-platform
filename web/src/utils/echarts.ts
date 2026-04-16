import * as echarts from 'echarts/core'
import {
  BarChart,
  GaugeChart,
  LineChart,
  PieChart,
  ScatterChart,
} from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart,
  GaugeChart,
  GridComponent,
  LegendComponent,
  LineChart,
  PieChart,
  ScatterChart,
  TooltipComponent,
  CanvasRenderer,
])

export const INDUSTRIAL_CHART_COLORS = {
  primary: '#62cfff',
  secondary: '#6fe6b6',
  tertiary: '#8ab8ff',
  warning: '#ffb547',
  critical: '#ff6b6b',
  grid: 'rgba(255,255,255,0.08)',
  axis: '#b8cce0',
}

export const buildIndustrialLineStyle = (color: string) => ({
  smooth: true,
  showSymbol: false,
  lineStyle: { width: 2.5, color },
  itemStyle: { color },
})

export { echarts }
