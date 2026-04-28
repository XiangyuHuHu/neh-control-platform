package com.example.platform.controller;

import com.example.platform.service.DashboardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @GetMapping("/overview")
    public Map<String, Object> getOverview() {
        return dashboardService.getOverview();
    }

    @GetMapping("/device-stats")
    public Map<String, Object> getDeviceStats() {
        return dashboardService.getDeviceStats();
    }

    @GetMapping("/alarm-stats")
    public Map<String, Object> getAlarmStats() {
        return dashboardService.getAlarmStats();
    }

    @GetMapping("/production-stats")
    public Map<String, Object> getProductionStats() {
        return dashboardService.getProductionStats();
    }

    @GetMapping("/energy-stats")
    public Map<String, Object> getEnergyStats() {
        return dashboardService.getEnergyStats();
    }

    @GetMapping("/recent-alarms")
    public Map<String, Object> getRecentAlarms(@RequestParam(defaultValue = "10") Integer limit) {
        return dashboardService.getRecentAlarms(limit);
    }

    @GetMapping("/recent-work-orders")
    public Map<String, Object> getRecentWorkOrders(@RequestParam(defaultValue = "10") Integer limit) {
        return dashboardService.getRecentWorkOrders(limit);
    }

    @GetMapping("/real-time-data")
    public Map<String, Object> getRealTimeData() {
        return dashboardService.getRealTimeData();
    }

    @GetMapping("/trend-data")
    public Map<String, Object> getTrendData(
            @RequestParam String type,
            @RequestParam(defaultValue = "day") String timeRange
    ) {
        return dashboardService.getTrendData(type, timeRange);
    }

    @GetMapping("/portal-metrics")
    public Map<String, Object> getPortalMetrics() {
        return dashboardService.getPortalMetrics();
    }
}
