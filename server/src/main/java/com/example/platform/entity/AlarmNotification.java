package com.example.platform.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "alarm_notification")
public class AlarmNotification {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String notificationId;
    @Column(name = "alarm_id")
    private String alarmId;
    @Column(name = "device_id")
    private String deviceId;
    private String notificationType;
    private String notificationContent;
    private String recipient;
    private String sendTime;
    private String status;
    private String responseTime;
    private String responseResult;

    @ManyToOne
    @JoinColumn(
            name = "alarm_id",
            referencedColumnName = "alarm_id",
            insertable = false,
            updatable = false
    )
    private AlarmRecord alarm;

    @ManyToOne
    @JoinColumn(
            name = "device_id",
            referencedColumnName = "device_id",
            insertable = false,
            updatable = false
    )
    private AssetDevice device;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNotificationId() {
        return notificationId;
    }

    public void setNotificationId(String notificationId) {
        this.notificationId = notificationId;
    }

    public String getAlarmId() {
        return alarmId;
    }

    public void setAlarmId(String alarmId) {
        this.alarmId = alarmId;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getNotificationType() {
        return notificationType;
    }

    public void setNotificationType(String notificationType) {
        this.notificationType = notificationType;
    }

    public String getNotificationContent() {
        return notificationContent;
    }

    public void setNotificationContent(String notificationContent) {
        this.notificationContent = notificationContent;
    }

    public String getRecipient() {
        return recipient;
    }

    public void setRecipient(String recipient) {
        this.recipient = recipient;
    }

    public String getSendTime() {
        return sendTime;
    }

    public void setSendTime(String sendTime) {
        this.sendTime = sendTime;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getResponseTime() {
        return responseTime;
    }

    public void setResponseTime(String responseTime) {
        this.responseTime = responseTime;
    }

    public String getResponseResult() {
        return responseResult;
    }

    public void setResponseResult(String responseResult) {
        this.responseResult = responseResult;
    }

    public AlarmRecord getAlarm() {
        return alarm;
    }

    public void setAlarm(AlarmRecord alarm) {
        this.alarm = alarm;
    }

    public AssetDevice getDevice() {
        return device;
    }

    public void setDevice(AssetDevice device) {
        this.device = device;
    }
}
