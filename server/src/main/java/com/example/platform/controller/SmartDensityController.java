package com.example.platform.controller;

import com.example.platform.service.SmartModelGatewayService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/smart-density")
public class SmartDensityController {

    private final SmartModelGatewayService gatewayService;

    public SmartDensityController(SmartModelGatewayService gatewayService) {
        this.gatewayService = gatewayService;
    }

    @GetMapping("/overview")
    public Map<String, Object> overview() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("units", gatewayService.smartDensityOverview());
        result.put("setpoint", gatewayService.predictDensitySetpoint(Map.of("data", List.of(1.42, 1.44, 1.46))));
        return result;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return gatewayService.smartDensityHealth();
    }

    @PostMapping("/predict")
    public Map<String, Object> predict(@RequestBody Map<String, Object> payload) {
        String unit = String.valueOf(payload.getOrDefault("unit", "3207"));
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("data_long", payload.getOrDefault("dataLong", List.of()));
        request.put("data_short", payload.getOrDefault("dataShort", List.of()));
        request.put("para", payload.getOrDefault("params", Map.of()));
        return gatewayService.predictSmartDensity(unit, request);
    }

    @PostMapping("/predict-setpoint")
    public Map<String, Object> predictSetpoint(@RequestBody Map<String, Object> payload) {
        return gatewayService.predictDensitySetpoint(payload);
    }
}
