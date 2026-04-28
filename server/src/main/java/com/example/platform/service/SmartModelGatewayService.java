package com.example.platform.service;

import com.example.platform.config.ModelServiceProperties;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class SmartModelGatewayService {

    private final ModelServiceProperties properties;
    private final ObjectMapper objectMapper;
    private final HttpClient httpClient;

    public SmartModelGatewayService(ModelServiceProperties properties, ObjectMapper objectMapper) {
        this.properties = properties;
        this.objectMapper = objectMapper;
        this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();
    }

    public List<Map<String, Object>> smartDensityOverview() {
        List<Map<String, Object>> rows = new ArrayList<>();
        rows.add(unitRow("3207", "主洗二段", "运行中", "1.43", "43%", "11.6", "自动控制"));
        rows.add(unitRow("3208", "主洗三段", "运行中", "1.47", "46%", "12.3", "自动控制"));
        rows.add(unitRow("316", "末煤系统", "待校正", "1.38", "38%", "9.8", "人工确认"));
        return rows;
    }

    public List<Map<String, Object>> smartReagentOverview() {
        List<Map<String, Object>> rows = new ArrayList<>();
        rows.add(reagentRow("601", "末煤一号加药泵", "运行中", "42", "1", "18", "自动"));
        rows.add(reagentRow("602", "末煤二号加药泵", "运行中", "45", "0", "20", "自动"));
        rows.add(reagentRow("5201", "块煤一号加药泵", "待观察", "38", "1", "16", "人工确认"));
        rows.add(reagentRow("5202", "块煤二号加药泵", "运行中", "40", "0", "17", "自动"));
        return rows;
    }

    public Map<String, Object> predictSmartDensity(String unit, Map<String, Object> payload) {
        String endpoint = switch (unit) {
            case "3207" -> "/mikong3207_predict";
            case "3208" -> "/mikong3208_predict";
            case "316" -> "/mikong316_predict";
            default -> "";
        };
        if (!endpoint.isEmpty()) {
            Map<String, Object> remote = post(properties.getSmartDensity(), endpoint, payload);
            if (remote != null) {
                return normalizeDensityResponse(unit, remote);
            }
        }
        return densityFallback(unit, payload);
    }

    public Map<String, Object> predictDensitySetpoint(Map<String, Object> payload) {
        Map<String, Object> remote = post(properties.getSmartDensity(), "/predictRhoSD", Map.of("data", payload.getOrDefault("data", List.of())));
        if (remote != null) {
            Object data = remote.get("data");
            if (data instanceof Map<?, ?> raw) {
                Map<String, Object> result = new LinkedHashMap<>();
                result.put("predMiddlingDensity", rawValue(raw, "pred_MMrho_SD", 1.46));
                result.put("predCleanDensity", rawValue(raw, "pred_KMrho_SD", 1.38));
                result.put("mode", properties.getSmartDensity().isEnabled() ? "模型服务" : "演示回退");
                return result;
            }
        }
        return Map.of(
                "predMiddlingDensity", 1.46,
                "predCleanDensity", 1.38,
                "mode", "演示回退"
        );
    }

    public Map<String, Object> predictSmartReagent(String unit, Map<String, Object> payload) {
        String endpoint = switch (unit) {
            case "601" -> "/jiayao601_predict";
            case "602" -> "/jiayao602_predict";
            case "5201" -> "/jiayao5201_predict";
            case "5202" -> "/jiayao5202_predict";
            default -> "";
        };
        if (!endpoint.isEmpty()) {
            Map<String, Object> remote = post(properties.getSmartReagent(), endpoint, payload);
            if (remote != null) {
                return normalizeReagentResponse(unit, remote);
            }
        }
        return reagentFallback(unit, payload);
    }

    public Map<String, Object> smartDensityHealth() {
        return health(properties.getSmartDensity(), "/openapi.json", "智能密控");
    }

    public Map<String, Object> smartReagentHealth() {
        return health(properties.getSmartReagent(), "/openapi.json", "智能加药");
    }

    private Map<String, Object> post(ModelServiceProperties.Endpoint endpoint, String path, Map<String, Object> payload) {
        if (!endpoint.isEnabled() || endpoint.getBaseUrl() == null || endpoint.getBaseUrl().isBlank()) {
            return null;
        }
        try {
            String body = objectMapper.writeValueAsString(payload);
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(endpoint.getBaseUrl() + path))
                    .timeout(Duration.ofMillis(endpoint.getTimeoutMs()))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                return null;
            }
            return objectMapper.readValue(response.body(), new TypeReference<>() {});
        } catch (IOException | InterruptedException ex) {
            if (ex instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            return null;
        }
    }

    private Map<String, Object> normalizeDensityResponse(String unit, Map<String, Object> remote) {
        Object data = remote.get("data");
        if (!(data instanceof Map<?, ?> raw)) {
            return densityFallback(unit, Map.of());
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("unit", unit);
        result.put("predDiverter", rawValue(raw, "pred_d", 42));
        result.put("predWater", rawValue(raw, "pred_w", 12.4));
        result.put("predDensity", rawValue(raw, "pred_rho", 1.43));
        result.put("state", rawValue(raw, "state", 0));
        result.put("stateName", rawValue(raw, "state_name", "运行中"));
        result.put("mode", "模型服务");
        return result;
    }

    private Map<String, Object> normalizeReagentResponse(String unit, Map<String, Object> remote) {
        Object data = remote.get("data");
        if (!(data instanceof Map<?, ?> raw)) {
            return reagentFallback(unit, Map.of());
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("unit", unit);
        result.put("predPump", rawValue(raw, "pred_pump", 42));
        result.put("numPump", rawValue(raw, "numPump", 1));
        result.put("predBackupPump", rawValue(raw, "pred_bkpump", 0));
        result.put("valveMN", rawValue(raw, "valveMN", 18));
        result.put("state", rawValue(raw, "state", 0));
        result.put("stateName", rawValue(raw, "state_name", "运行中"));
        result.put("mode", "模型服务");
        return result;
    }

    private Object rawValue(Map<?, ?> raw, String key, Object fallback) {
        Object value = raw.get(key);
        return value != null ? value : fallback;
    }

    private Map<String, Object> health(ModelServiceProperties.Endpoint endpoint, String path, String serviceName) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("service", serviceName);
        result.put("enabled", endpoint.isEnabled());
        result.put("baseUrl", endpoint.getBaseUrl());
        if (!endpoint.isEnabled() || endpoint.getBaseUrl() == null || endpoint.getBaseUrl().isBlank()) {
            result.put("reachable", false);
            result.put("mode", "演示回退");
            result.put("message", "未启用模型服务");
            return result;
        }

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(endpoint.getBaseUrl() + path))
                    .timeout(Duration.ofMillis(endpoint.getTimeoutMs()))
                    .GET()
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            result.put("reachable", response.statusCode() >= 200 && response.statusCode() < 300);
            result.put("mode", "模型服务");
            result.put("statusCode", response.statusCode());
            result.put("message", response.statusCode() >= 200 && response.statusCode() < 300 ? "连接正常" : "服务返回异常");
            return result;
        } catch (IOException | InterruptedException ex) {
            if (ex instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            result.put("reachable", false);
            result.put("mode", "模型服务");
            result.put("message", ex.getMessage());
            return result;
        }
    }

    private Map<String, Object> densityFallback(String unit, Map<String, Object> payload) {
        double density = switch (unit) {
            case "3208" -> 1.47;
            case "316" -> 1.38;
            default -> 1.43;
        };
        double water = switch (unit) {
            case "3208" -> 12.8;
            case "316" -> 9.6;
            default -> 11.8;
        };
        int diverter = switch (unit) {
            case "3208" -> 46;
            case "316" -> 38;
            default -> 43;
        };
        return Map.of(
                "unit", unit,
                "predDiverter", diverter,
                "predWater", water,
                "predDensity", density,
                "state", 0,
                "stateName", "演示运行",
                "mode", "演示回退",
                "payloadEcho", payload
        );
    }

    private Map<String, Object> reagentFallback(String unit, Map<String, Object> payload) {
        int pump = switch (unit) {
            case "602" -> 45;
            case "5201" -> 38;
            case "5202" -> 40;
            default -> 42;
        };
        return Map.of(
                "unit", unit,
                "predPump", pump,
                "numPump", 1,
                "predBackupPump", 0,
                "valveMN", 18,
                "state", 0,
                "stateName", "演示运行",
                "mode", "演示回退",
                "payloadEcho", payload
        );
    }

    private Map<String, Object> unitRow(
            String unit,
            String area,
            String status,
            String density,
            String diverter,
            String water,
            String mode
    ) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("unit", unit);
        row.put("area", area);
        row.put("status", status);
        row.put("density", density);
        row.put("diverter", diverter);
        row.put("water", water);
        row.put("mode", mode);
        return row;
    }

    private Map<String, Object> reagentRow(
            String unit,
            String area,
            String status,
            String pump,
            String backupPump,
            String valve,
            String mode
    ) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("unit", unit);
        row.put("area", area);
        row.put("status", status);
        row.put("pump", pump);
        row.put("backupPump", backupPump);
        row.put("valve", valve);
        row.put("mode", mode);
        return row;
    }
}
