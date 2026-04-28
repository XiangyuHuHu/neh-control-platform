package com.example.platform.service;

import com.example.platform.dto.power.PowerActionRequest;
import com.example.platform.dto.power.PowerApplyRequest;
import com.example.platform.entity.PowerOperationApplication;

import java.util.List;
import java.util.Map;

public interface PowerOperationService {
    PowerOperationApplication applyPowerOff(PowerApplyRequest request);

    PowerOperationApplication approvePowerOff(PowerActionRequest request);

    PowerOperationApplication electricianVerify(PowerActionRequest request);

    PowerOperationApplication startRepair(PowerActionRequest request);

    PowerOperationApplication completeRepair(PowerActionRequest request);

    PowerOperationApplication applyPowerOn(PowerActionRequest request);

    PowerOperationApplication approvePowerOn(PowerActionRequest request);

    List<PowerOperationApplication> list(String status, String powerRoom);

    Map<String, Object> digitalTwinBoard(String powerRoom);

    Map<String, Object> riskAnalytics(int recentDays);
}
