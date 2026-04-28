package com.example.platform.dto.power;

import java.time.LocalDateTime;

public class PowerApplyRequest {
    private Long deviceId;
    private String deviceName;
    private String powerRoom;
    private String cabinetNo;
    private String reason;
    private String requestedBy;
    private LocalDateTime plannedPowerOffTime;
    private LocalDateTime plannedPowerOnTime;

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
}
