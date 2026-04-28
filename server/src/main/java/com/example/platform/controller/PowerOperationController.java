package com.example.platform.controller;

import com.example.platform.dto.power.PowerActionRequest;
import com.example.platform.dto.power.PowerApplyRequest;
import com.example.platform.entity.PowerOperationApplication;
import com.example.platform.service.PowerOperationService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/power-operation")
public class PowerOperationController {

    private final PowerOperationService powerOperationService;

    public PowerOperationController(PowerOperationService powerOperationService) {
        this.powerOperationService = powerOperationService;
    }

    @PostMapping("/apply")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication applyPowerOff(@RequestBody PowerApplyRequest request) {
        return powerOperationService.applyPowerOff(request);
    }

    @PostMapping("/approve-power-off")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication approvePowerOff(@RequestBody PowerActionRequest request) {
        return powerOperationService.approvePowerOff(request);
    }

    @PostMapping("/electrician-verify")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication electricianVerify(@RequestBody PowerActionRequest request) {
        return powerOperationService.electricianVerify(request);
    }

    @PostMapping("/start-repair")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication startRepair(@RequestBody PowerActionRequest request) {
        return powerOperationService.startRepair(request);
    }

    @PostMapping("/complete-repair")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication completeRepair(@RequestBody PowerActionRequest request) {
        return powerOperationService.completeRepair(request);
    }

    @PostMapping("/apply-power-on")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication applyPowerOn(@RequestBody PowerActionRequest request) {
        return powerOperationService.applyPowerOn(request);
    }

    @PostMapping("/approve-power-on")
    @PreAuthorize("@authz.insecure() or hasRole('PLATFORM_ADMIN')")
    public PowerOperationApplication approvePowerOn(@RequestBody PowerActionRequest request) {
        return powerOperationService.approvePowerOn(request);
    }

    @GetMapping("/list")
    @PreAuthorize("@authz.insecure() or hasAnyRole('PLATFORM_ADMIN','PLATFORM_READ')")
    public List<PowerOperationApplication> list(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String powerRoom
    ) {
        return powerOperationService.list(status, powerRoom);
    }

    @GetMapping("/digital-twin-board")
    @PreAuthorize("@authz.insecure() or hasAnyRole('PLATFORM_ADMIN','PLATFORM_READ')")
    public Map<String, Object> digitalTwinBoard(@RequestParam(required = false) String powerRoom) {
        return powerOperationService.digitalTwinBoard(powerRoom);
    }

    @GetMapping("/risk-analytics")
    @PreAuthorize("@authz.insecure() or hasAnyRole('PLATFORM_ADMIN','PLATFORM_READ')")
    public Map<String, Object> riskAnalytics(@RequestParam(defaultValue = "30") int recentDays) {
        return powerOperationService.riskAnalytics(recentDays);
    }
}
