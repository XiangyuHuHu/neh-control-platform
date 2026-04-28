package com.example.platform.service;

import java.util.Map;

public interface DashboardService {

    Map<String, Object> getOverview();

    Map<String, Object> getDeviceStats();

    Map<String, Object> getAlarmStats();

    Map<String, Object> getProductionStats();

    Map<String, Object> getEnergyStats();

    Map<String, Object> getRecentAlarms(Integer limit);

    Map<String, Object> getRecentWorkOrders(Integer limit);

    Map<String, Object> getRealTimeData();

    Map<String, Object> getTrendData(String type, String timeRange);

    Map<String, Object> getPortalMetrics();
}
