package com.example.platform.controller;

import com.example.platform.service.EquipmentPredictiveService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/equipment")
public class EquipmentPredictiveController {

    private final EquipmentPredictiveService equipmentPredictiveService;

    public EquipmentPredictiveController(EquipmentPredictiveService equipmentPredictiveService) {
        this.equipmentPredictiveService = equipmentPredictiveService;
    }

    @GetMapping("/predictive-board")
    @PreAuthorize("@authz.insecure() or hasAnyRole('PLATFORM_ADMIN','PLATFORM_READ')")
    public Map<String, Object> predictiveBoard() {
        return equipmentPredictiveService.predictiveBoard();
    }
}
