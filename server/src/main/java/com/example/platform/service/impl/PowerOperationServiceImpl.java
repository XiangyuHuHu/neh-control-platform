package com.example.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.platform.dto.power.PowerActionRequest;
import com.example.platform.dto.power.PowerApplyRequest;
import com.example.platform.entity.PowerDeviceTagRecord;
import com.example.platform.entity.PowerOperationApplication;
import com.example.platform.entity.PowerOperationLog;
import com.example.platform.mapper.PowerDeviceTagRecordMapper;
import com.example.platform.mapper.PowerOperationApplicationMapper;
import com.example.platform.mapper.PowerOperationLogMapper;
import com.example.platform.service.PowerOperationService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class PowerOperationServiceImpl implements PowerOperationService {

    private static final String STATUS_PENDING = "pending";
    private static final String STATUS_APPROVED = "approved";
    private static final String STATUS_REJECTED = "rejected";
    private static final String STATUS_VERIFIED = "verified";
    private static final String STATUS_REPAIRING = "repairing";
    private static final String STATUS_REPAIR_COMPLETED = "repair_completed";
    private static final String STATUS_POWER_ON_APPLIED = "power_on_applied";
    private static final String STATUS_POWER_ON_REJECTED = "power_on_rejected";
    private static final String STATUS_COMPLETED = "completed";

    private final PowerOperationApplicationMapper applicationMapper;
    private final PowerOperationLogMapper logMapper;
    private final PowerDeviceTagRecordMapper tagRecordMapper;

    public PowerOperationServiceImpl(
            PowerOperationApplicationMapper applicationMapper,
            PowerOperationLogMapper logMapper,
            PowerDeviceTagRecordMapper tagRecordMapper
    ) {
        this.applicationMapper = applicationMapper;
        this.logMapper = logMapper;
        this.tagRecordMapper = tagRecordMapper;
    }

    @Override
    @Transactional
    public PowerOperationApplication applyPowerOff(PowerApplyRequest request) {
        LocalDateTime now = LocalDateTime.now();
        PowerOperationApplication app = new PowerOperationApplication();
        app.setApplicationNo(generateNo());
        app.setDeviceId(request.getDeviceId());
        app.setDeviceName(request.getDeviceName());
        app.setPowerRoom(request.getPowerRoom());
        app.setCabinetNo(request.getCabinetNo());
        app.setOperationType("power_off");
        app.setWorkflowStatus(STATUS_PENDING);
        app.setRiskLevel("medium");
        app.setReason(request.getReason());
        app.setRequestedBy(defaultOperator(request.getRequestedBy()));
        app.setRemainingTagCount(0);
        app.setPlannedPowerOffTime(request.getPlannedPowerOffTime());
        app.setPlannedPowerOnTime(request.getPlannedPowerOnTime());
        app.setCreatedAt(now);
        app.setUpdatedAt(now);
        applicationMapper.insert(app);
        writeLog(app.getId(), "create", null, STATUS_PENDING, app.getRequestedBy(), "停电申请提交");
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication approvePowerOff(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_PENDING);
        String next = isApproved(request) ? STATUS_APPROVED : STATUS_REJECTED;
        app.setApprovedBy(defaultOperator(request.getOperator()));
        app.setApprovedAt(LocalDateTime.now());
        app.setDispatchDecision(next);
        transit(app, next, "power_off_approve", request.getOperator(), request.getComment());
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication electricianVerify(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_APPROVED);
        String operator = defaultOperator(request.getOperator());
        app.setVerifiedBy(operator);
        app.setVerifiedAt(LocalDateTime.now());
        transit(app, STATUS_VERIFIED, "electrician_verify", operator, request.getComment());

        PowerDeviceTagRecord tag = new PowerDeviceTagRecord();
        tag.setApplicationId(app.getId());
        tag.setDeviceId(app.getDeviceId());
        tag.setTagUser(operator);
        tag.setTagStatus("active");
        tag.setTaggedAt(LocalDateTime.now());
        tagRecordMapper.insert(tag);

        app.setRemainingTagCount(countActiveTags(app.getId()));
        app.setUpdatedAt(LocalDateTime.now());
        applicationMapper.updateById(app);
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication startRepair(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_VERIFIED);
        app.setRepairedBy(defaultOperator(request.getOperator()));
        app.setRepairStartedAt(LocalDateTime.now());
        transit(app, STATUS_REPAIRING, "repair_start", request.getOperator(), request.getComment());
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication completeRepair(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_REPAIRING);
        app.setRepairCompletedAt(LocalDateTime.now());
        transit(app, STATUS_REPAIR_COMPLETED, "repair_end", request.getOperator(), request.getComment());
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication applyPowerOn(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_REPAIR_COMPLETED);
        String operator = defaultOperator(request.getOperator());

        List<PowerDeviceTagRecord> selfTags = tagRecordMapper.selectList(new LambdaQueryWrapper<PowerDeviceTagRecord>()
                .eq(PowerDeviceTagRecord::getApplicationId, app.getId())
                .eq(PowerDeviceTagRecord::getTagUser, operator)
                .eq(PowerDeviceTagRecord::getTagStatus, "active"));
        LocalDateTime now = LocalDateTime.now();
        for (PowerDeviceTagRecord tag : selfTags) {
            tag.setTagStatus("released");
            tag.setUntaggedAt(now);
            tagRecordMapper.updateById(tag);
        }

        int remaining = countActiveTags(app.getId());
        app.setRemainingTagCount(remaining);
        app.setPowerOnAppliedAt(now);
        if (remaining > 0) {
            app.setRiskLevel("high");
            app.setUpdatedAt(now);
            applicationMapper.updateById(app);
            writeLog(app.getId(), "power_on_blocked_by_tags", app.getWorkflowStatus(), app.getWorkflowStatus(), operator,
                    "仍有其他人员挂牌，禁止进入送电审批");
            return app;
        }

        transit(app, STATUS_POWER_ON_APPLIED, "power_on_apply", operator, request.getComment());
        return app;
    }

    @Override
    @Transactional
    public PowerOperationApplication approvePowerOn(PowerActionRequest request) {
        PowerOperationApplication app = getRequired(request.getApplicationId());
        ensureStatus(app, STATUS_POWER_ON_APPLIED);
        String next = isApproved(request) ? STATUS_COMPLETED : STATUS_POWER_ON_REJECTED;
        app.setPowerOnApprovedAt(LocalDateTime.now());
        app.setDispatchDecision(next);
        transit(app, next, "power_on_approve", request.getOperator(), request.getComment());
        return app;
    }

    @Override
    public List<PowerOperationApplication> list(String status, String powerRoom) {
        LambdaQueryWrapper<PowerOperationApplication> wrapper = new LambdaQueryWrapper<>();
        if (status != null && !status.isBlank()) {
            wrapper.eq(PowerOperationApplication::getWorkflowStatus, status);
        }
        if (powerRoom != null && !powerRoom.isBlank()) {
            wrapper.eq(PowerOperationApplication::getPowerRoom, powerRoom);
        }
        wrapper.orderByDesc(PowerOperationApplication::getCreatedAt);
        return applicationMapper.selectList(wrapper);
    }

    @Override
    public Map<String, Object> digitalTwinBoard(String powerRoom) {
        List<PowerOperationApplication> applications = list(null, powerRoom);
        Map<String, Long> statusCount = applications.stream()
                .collect(Collectors.groupingBy(PowerOperationApplication::getWorkflowStatus, Collectors.counting()));

        Map<String, Long> roomCount = applications.stream()
                .collect(Collectors.groupingBy(PowerOperationApplication::getPowerRoom, Collectors.counting()));

        List<PowerOperationApplication> topRisk = applications.stream()
                .filter(a -> "high".equalsIgnoreCase(a.getRiskLevel()) || (a.getRemainingTagCount() != null && a.getRemainingTagCount() > 0))
                .sorted(Comparator.comparing(PowerOperationApplication::getUpdatedAt, Comparator.nullsLast(Comparator.reverseOrder())))
                .limit(10)
                .collect(Collectors.toList());

        Map<String, Object> result = new HashMap<>();
        result.put("statusOverview", statusCount);
        result.put("powerRoomOverview", roomCount);
        result.put("highRiskApplications", topRisk);
        result.put("generatedAt", LocalDateTime.now());
        return result;
    }

    @Override
    public Map<String, Object> riskAnalytics(int recentDays) {
        int safeDays = Math.max(1, recentDays);
        LocalDateTime since = LocalDate.now().minusDays(safeDays).atStartOfDay();
        List<PowerOperationLog> logs = logMapper.selectList(new LambdaQueryWrapper<PowerOperationLog>()
                .ge(PowerOperationLog::getCreatedAt, since));

        Map<String, Long> actionTop = logs.stream()
                .collect(Collectors.groupingBy(PowerOperationLog::getActionType, Collectors.counting()));

        List<PowerOperationApplication> recentApps = applicationMapper.selectList(new LambdaQueryWrapper<PowerOperationApplication>()
                .ge(PowerOperationApplication::getCreatedAt, since));
        Map<String, Long> roomTop = recentApps.stream()
                .collect(Collectors.groupingBy(PowerOperationApplication::getPowerRoom, Collectors.counting()));
        long blockedByTags = logs.stream().filter(l -> "power_on_blocked_by_tags".equals(l.getActionType())).count();

        List<String> suggestions = new ArrayList<>();
        if (blockedByTags > 0) {
            suggestions.add("存在送电前挂牌未清风险，建议强化班组交接与解牌确认清单。");
        }
        if (actionTop.getOrDefault("power_off_approve", 0L) > actionTop.getOrDefault("power_on_approve", 0L) + 20) {
            suggestions.add("停电审批与送电审批数量差距较大，建议核查长周期未闭环工单。");
        }
        if (suggestions.isEmpty()) {
            suggestions.add("近期流程稳定，建议按月复盘高频配电室与关键设备风险点。");
        }

        Map<String, Object> result = new HashMap<>();
        result.put("recentDays", safeDays);
        result.put("actionTop", actionTop);
        result.put("powerRoomTop", roomTop);
        result.put("blockedByTagsCount", blockedByTags);
        result.put("suggestions", suggestions);
        return result;
    }

    private void ensureStatus(PowerOperationApplication app, String expected) {
        if (!expected.equals(app.getWorkflowStatus())) {
            throw new IllegalStateException("当前状态不允许该操作，期望状态: " + expected + ", 实际状态: " + app.getWorkflowStatus());
        }
    }

    private void transit(PowerOperationApplication app, String nextStatus, String action, String operator, String comment) {
        String before = app.getWorkflowStatus();
        app.setWorkflowStatus(nextStatus);
        app.setUpdatedAt(LocalDateTime.now());
        applicationMapper.updateById(app);
        writeLog(app.getId(), action, before, nextStatus, defaultOperator(operator), comment);
    }

    private PowerOperationApplication getRequired(Long id) {
        PowerOperationApplication app = applicationMapper.selectById(id);
        if (app == null) {
            throw new IllegalArgumentException("停送电工单不存在: " + id);
        }
        return app;
    }

    private void writeLog(Long appId, String action, String before, String after, String operator, String comment) {
        PowerOperationLog log = new PowerOperationLog();
        log.setApplicationId(appId);
        log.setActionType(action);
        log.setBeforeStatus(before);
        log.setAfterStatus(after);
        log.setOperatorName(defaultOperator(operator));
        log.setComment(comment);
        log.setCreatedAt(LocalDateTime.now());
        logMapper.insert(log);
    }

    private String generateNo() {
        String date = LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
        int count = Math.toIntExact(applicationMapper.selectCount(new LambdaQueryWrapper<PowerOperationApplication>()
                .ge(PowerOperationApplication::getCreatedAt, LocalDate.now().atStartOfDay())));
        return "PO-" + date + "-" + String.format("%04d", count + 1);
    }

    private int countActiveTags(Long appId) {
        return Math.toIntExact(tagRecordMapper.selectCount(new LambdaQueryWrapper<PowerDeviceTagRecord>()
                .eq(PowerDeviceTagRecord::getApplicationId, appId)
                .eq(PowerDeviceTagRecord::getTagStatus, "active")));
    }

    private String defaultOperator(String operator) {
        return (operator == null || operator.isBlank()) ? "system" : operator;
    }

    private boolean isApproved(PowerActionRequest request) {
        return Boolean.TRUE.equals(request.getApproved());
    }
}
