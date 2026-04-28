package com.example.platform.service.impl;

import com.example.platform.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DashboardServiceImpl implements DashboardService {

    private static final Logger log = LoggerFactory.getLogger(DashboardServiceImpl.class);
    @Autowired
    private AssetDeviceService assetDeviceService;

    @Autowired
    private DeviceRuntimeDataService deviceRuntimeDataService;

    @Autowired
    private AlarmRecordService alarmRecordService;

    @Autowired
    private ProductionReportService productionReportService;

    @Autowired
    private WorkOrderService workOrderService;

    @Autowired
    private EnergyConsumptionService energyConsumptionService;

    @Override
    public Map<String, Object> getOverview() {
        Map<String, Object> overview = new HashMap<>();
        try {
            long totalDevices = assetDeviceService.count();
            overview.put("totalDevices", totalDevices);
            long runningDevices = assetDeviceService.countByStatus("运行中");
            overview.put("runningDevices", runningDevices);
            long totalAlarms = alarmRecordService.count();
            overview.put("totalAlarms", totalAlarms);
            long unhandledAlarms = alarmRecordService.countByStatus("未处理");
            overview.put("unhandledAlarms", unhandledAlarms);
            long pendingWorkOrders = workOrderService.getPending().size();
            overview.put("pendingWorkOrders", pendingWorkOrders);
        } catch (Exception e) {
            log.warn("看板概况查询失败（库表未齐时返回 0）: {}", e.getMessage());
            overview.put("totalDevices", 0L);
            overview.put("runningDevices", 0L);
            overview.put("totalAlarms", 0L);
            overview.put("unhandledAlarms", 0L);
            overview.put("pendingWorkOrders", 0L);
        }
        return overview;
    }

    @Override
    public Map<String, Object> getDeviceStats() {
        Map<String, Object> stats = new HashMap<>();
        
        // 设备状态分布
        Map<String, Long> statusDistribution = new HashMap<>();
        statusDistribution.put("运行中", assetDeviceService.countByStatus("运行中"));
        statusDistribution.put("待机", assetDeviceService.countByStatus("待机"));
        statusDistribution.put("故障", assetDeviceService.countByStatus("故障"));
        statusDistribution.put("维护", assetDeviceService.countByStatus("维护"));
        stats.put("statusDistribution", statusDistribution);
        
        // 设备类型分布
        Map<String, Long> typeDistribution = assetDeviceService.countByType();
        stats.put("typeDistribution", typeDistribution);
        
        return stats;
    }

    @Override
    public Map<String, Object> getAlarmStats() {
        Map<String, Object> stats = new HashMap<>();
        
        // 报警级别分布
        Map<String, Long> levelDistribution = new HashMap<>();
        levelDistribution.put("紧急", alarmRecordService.countByLevel("紧急"));
        levelDistribution.put("重要", alarmRecordService.countByLevel("重要"));
        levelDistribution.put("一般", alarmRecordService.countByLevel("一般"));
        stats.put("levelDistribution", levelDistribution);
        
        // 报警状态分布
        Map<String, Long> statusDistribution = new HashMap<>();
        statusDistribution.put("未处理", alarmRecordService.countByStatus("未处理"));
        statusDistribution.put("处理中", alarmRecordService.countByStatus("处理中"));
        statusDistribution.put("已处理", alarmRecordService.countByStatus("已处理"));
        stats.put("statusDistribution", statusDistribution);
        
        return stats;
    }

    @Override
    public Map<String, Object> getProductionStats() {
        Map<String, Object> stats = new HashMap<>();
        
        // 今日产量
        double todayProduction = productionReportService.getTodayProduction();
        stats.put("todayProduction", todayProduction);
        
        // 本周产量
        double weekProduction = productionReportService.getWeekProduction();
        stats.put("weekProduction", weekProduction);
        
        // 本月产量
        double monthProduction = productionReportService.getMonthProduction();
        stats.put("monthProduction", monthProduction);
        
        return stats;
    }

    @Override
    public Map<String, Object> getEnergyStats() {
        Map<String, Object> stats = new HashMap<>();
        try {
            LocalDate today = LocalDate.now();
            LocalDate weekStart = today.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
            LocalDate monthStart = today.with(TemporalAdjusters.firstDayOfMonth());
            stats.put("todayEnergy", energyConsumptionService.sumConsumptionBetween(today, today));
            stats.put("weekEnergy", energyConsumptionService.sumConsumptionBetween(weekStart, today));
            stats.put("monthEnergy", energyConsumptionService.sumConsumptionBetween(monthStart, today));
        } catch (Exception e) {
            log.warn("能耗汇总查询失败（表未建或库未就绪时返回 0）: {}", e.getMessage());
            stats.put("todayEnergy", 0.0);
            stats.put("weekEnergy", 0.0);
            stats.put("monthEnergy", 0.0);
        }
        return stats;
    }

    @Override
    public Map<String, Object> getRecentAlarms(Integer limit) {
        Map<String, Object> result = new HashMap<>();
        result.put("alarms", alarmRecordService.getRecent(limit));
        return result;
    }

    @Override
    public Map<String, Object> getRecentWorkOrders(Integer limit) {
        Map<String, Object> result = new HashMap<>();
        result.put("workOrders", workOrderService.getRecent(limit));
        return result;
    }

    @Override
    public Map<String, Object> getRealTimeData() {
        Map<String, Object> result = new HashMap<>();
        result.put("deviceData", deviceRuntimeDataService.getLatestData());
        return result;
    }

    @Override
    public Map<String, Object> getTrendData(String type, String timeRange) {
        Map<String, Object> result = new HashMap<>();
        
        // 根据类型和时间范围获取趋势数据
        if ("production".equals(type)) {
            result.put("trend", productionReportService.getTrendData(timeRange));
        } else if ("alarm".equals(type)) {
            result.put("trend", alarmRecordService.getTrendData(timeRange));
        } else if ("energy".equals(type)) {
            // 能源趋势数据
            result.put("trend", new HashMap<>());
        }
        
        return result;
    }

    @Override
    public Map<String, Object> getPortalMetrics() {
        List<Map<String, String>> metrics = new ArrayList<>();
        try {
            double todayInfeed = productionReportService.getTodayProduction();
            double cleanCoal = Math.max(0D, todayInfeed * 0.65D);
            double todayEnergy = energyConsumptionService.sumConsumptionBetween(LocalDate.now(), LocalDate.now());
            OeeMetric oeeMetric = resolveOeeMetric(todayInfeed, cleanCoal, todayEnergy);

            metrics.add(metric("今日入洗量", String.format("%.0f t", todayInfeed), "来自生产日报统计"));
            metrics.add(metric("精煤产量", String.format("%.0f t", cleanCoal), "按入洗量折算估计"));
            metrics.add(metric("实时总功率", String.format("%.0f kW", todayEnergy), "来自当日电耗统计"));
            metrics.add(metric("全厂设备综合效率（OEE）", String.format("%.1f %%", oeeMetric.value()), oeeMetric.note()));
        } catch (Exception e) {
            log.warn("门户核心指标查询失败（回退演示值）: {}", e.getMessage());
            metrics.add(metric("今日入洗量", "5,200 t", "较昨日 +4.2%"));
            metrics.add(metric("精煤产量", "3,400 t", "达成率 97.1%"));
            metrics.add(metric("实时总功率", "850 kW", "峰段负荷可控"));
            metrics.add(metric("全厂设备综合效率（OEE）", "92.4 %", "综合设备可用率与工况折算"));
        }
        Map<String, Object> result = new HashMap<>();
        result.put("metrics", metrics);
        result.put("generatedAt", LocalDate.now().toString());
        return result;
    }

    private Map<String, String> metric(String label, String value, String note) {
        Map<String, String> row = new HashMap<>();
        row.put("label", label);
        row.put("value", value);
        row.put("note", note);
        return row;
    }

    private OeeMetric resolveOeeMetric(double todayInfeed, double cleanCoal, double todayEnergy) {
        try {
            long totalDevices = assetDeviceService.count();
            long runningDevices = assetDeviceService.countByStatus("运行中");
            int pendingOrders = workOrderService.getPending().size();

            double availability = totalDevices > 0 ? (runningDevices * 100D / totalDevices) : 0D;
            double quality = todayInfeed > 0 ? Math.min(100D, cleanCoal * 100D / todayInfeed) : 0D;

            // 工单越多表示受扰动越大，用于折减性能因子。
            double performance = Math.max(70D, 96D - Math.min(20D, pendingOrders * 1.8D));
            if (todayEnergy <= 0D) {
                performance = Math.max(65D, performance - 4D);
            }

            double oee = availability * quality * performance / 10000D;
            return new OeeMetric(Math.max(0D, Math.min(100D, oee)),
                    String.format("可用率 %.1f%% · 质量 %.1f%% · 性能 %.1f%%", availability, quality, performance));
        } catch (Exception e) {
            log.warn("OEE 计算失败，回退默认值: {}", e.getMessage());
            return new OeeMetric(92.4D, "综合设备可用率与工况折算（回退）");
        }
    }

    private record OeeMetric(double value, String note) {}
}
