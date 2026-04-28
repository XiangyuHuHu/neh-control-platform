package com.example.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

@TableName("power_operation_application")
public class PowerOperationApplication {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String applicationNo;
    private Long deviceId;
    private String deviceName;
    private String powerRoom;
    private String cabinetNo;
    private String workflowStatus;
    private String operationType;
    private String riskLevel;
    private String reason;
    private String requestedBy;
    private String approvedBy;
    private String verifiedBy;
    private String repairedBy;
    private String dispatchDecision;
    private Integer remainingTagCount;
    private LocalDateTime plannedPowerOffTime;
    private LocalDateTime plannedPowerOnTime;
    private LocalDateTime approvedAt;
    private LocalDateTime verifiedAt;
    private LocalDateTime repairStartedAt;
    private LocalDateTime repairCompletedAt;
    private LocalDateTime powerOnAppliedAt;
    private LocalDateTime powerOnApprovedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getApplicationNo() {
        return applicationNo;
    }

    public void setApplicationNo(String applicationNo) {
        this.applicationNo = applicationNo;
    }

    public Long getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(Long deviceId) {
        this.deviceId = deviceId;
    }

    public String getDeviceName() {
        return deviceName;
    }

    public void setDeviceName(String deviceName) {
        this.deviceName = deviceName;
    }

    public String getPowerRoom() {
        return powerRoom;
    }

    public void setPowerRoom(String powerRoom) {
        this.powerRoom = powerRoom;
    }

    public String getCabinetNo() {
        return cabinetNo;
    }

    public void setCabinetNo(String cabinetNo) {
        this.cabinetNo = cabinetNo;
    }

    public String getWorkflowStatus() {
        return workflowStatus;
    }

    public void setWorkflowStatus(String workflowStatus) {
        this.workflowStatus = workflowStatus;
    }

    public String getOperationType() {
        return operationType;
    }

    public void setOperationType(String operationType) {
        this.operationType = operationType;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String getRequestedBy() {
        return requestedBy;
    }

    public void setRequestedBy(String requestedBy) {
        this.requestedBy = requestedBy;
    }

    public String getApprovedBy() {
        return approvedBy;
    }

    public void setApprovedBy(String approvedBy) {
        this.approvedBy = approvedBy;
    }

    public String getVerifiedBy() {
        return verifiedBy;
    }

    public void setVerifiedBy(String verifiedBy) {
        this.verifiedBy = verifiedBy;
    }

    public String getRepairedBy() {
        return repairedBy;
    }

    public void setRepairedBy(String repairedBy) {
        this.repairedBy = repairedBy;
    }

    public String getDispatchDecision() {
        return dispatchDecision;
    }

    public void setDispatchDecision(String dispatchDecision) {
        this.dispatchDecision = dispatchDecision;
    }

    public Integer getRemainingTagCount() {
        return remainingTagCount;
    }

    public void setRemainingTagCount(Integer remainingTagCount) {
        this.remainingTagCount = remainingTagCount;
    }

    public LocalDateTime getPlannedPowerOffTime() {
        return plannedPowerOffTime;
    }

    public void setPlannedPowerOffTime(LocalDateTime plannedPowerOffTime) {
        this.plannedPowerOffTime = plannedPowerOffTime;
    }

    public LocalDateTime getPlannedPowerOnTime() {
        return plannedPowerOnTime;
    }

    public void setPlannedPowerOnTime(LocalDateTime plannedPowerOnTime) {
        this.plannedPowerOnTime = plannedPowerOnTime;
    }

    public LocalDateTime getApprovedAt() {
        return approvedAt;
    }

    public void setApprovedAt(LocalDateTime approvedAt) {
        this.approvedAt = approvedAt;
    }

    public LocalDateTime getVerifiedAt() {
        return verifiedAt;
    }

    public void setVerifiedAt(LocalDateTime verifiedAt) {
        this.verifiedAt = verifiedAt;
    }

    public LocalDateTime getRepairStartedAt() {
        return repairStartedAt;
    }

    public void setRepairStartedAt(LocalDateTime repairStartedAt) {
        this.repairStartedAt = repairStartedAt;
    }

    public LocalDateTime getRepairCompletedAt() {
        return repairCompletedAt;
    }

    public void setRepairCompletedAt(LocalDateTime repairCompletedAt) {
        this.repairCompletedAt = repairCompletedAt;
    }

    public LocalDateTime getPowerOnAppliedAt() {
        return powerOnAppliedAt;
    }

    public void setPowerOnAppliedAt(LocalDateTime powerOnAppliedAt) {
        this.powerOnAppliedAt = powerOnAppliedAt;
    }

    public LocalDateTime getPowerOnApprovedAt() {
        return powerOnApprovedAt;
    }

    public void setPowerOnApprovedAt(LocalDateTime powerOnApprovedAt) {
        this.powerOnApprovedAt = powerOnApprovedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}
