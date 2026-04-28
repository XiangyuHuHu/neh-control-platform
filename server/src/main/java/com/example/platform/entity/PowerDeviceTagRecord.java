package com.example.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

@TableName("power_device_tag_record")
public class PowerDeviceTagRecord {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long applicationId;
    private Long deviceId;
    private String tagUser;
    private String tagStatus;
    private LocalDateTime taggedAt;
    private LocalDateTime untaggedAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getApplicationId() {
        return applicationId;
    }

    public void setApplicationId(Long applicationId) {
        this.applicationId = applicationId;
    }

    public Long getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(Long deviceId) {
        this.deviceId = deviceId;
    }

    public String getTagUser() {
        return tagUser;
    }

    public void setTagUser(String tagUser) {
        this.tagUser = tagUser;
    }

    public String getTagStatus() {
        return tagStatus;
    }

    public void setTagStatus(String tagStatus) {
        this.tagStatus = tagStatus;
    }

    public LocalDateTime getTaggedAt() {
        return taggedAt;
    }

    public void setTaggedAt(LocalDateTime taggedAt) {
        this.taggedAt = taggedAt;
    }

    public LocalDateTime getUntaggedAt() {
        return untaggedAt;
    }

    public void setUntaggedAt(LocalDateTime untaggedAt) {
        this.untaggedAt = untaggedAt;
    }
}
