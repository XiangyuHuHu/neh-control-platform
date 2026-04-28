package com.example.platform.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "coal_analysis_result")
public class CoalAnalysisResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String resultId;
    @Column(name = "sample_id")
    private String sampleId;
    private String analysisTime;
    private Double moisture;
    private Double ash;
    private Double volatileMatter;
    private Double fixedCarbon;
    private Double sulfur;
    private Double calorificValue;
    private Double ashFusionTemperature;
    private String operator;
    private String remark;
    private String status;

    @ManyToOne
    @JoinColumn(
            name = "sample_id",
            referencedColumnName = "sample_id",
            insertable = false,
            updatable = false
    )
    private CoalSample sample;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getResultId() {
        return resultId;
    }

    public void setResultId(String resultId) {
        this.resultId = resultId;
    }

    public String getSampleId() {
        return sampleId;
    }

    public void setSampleId(String sampleId) {
        this.sampleId = sampleId;
    }

    public String getAnalysisTime() {
        return analysisTime;
    }

    public void setAnalysisTime(String analysisTime) {
        this.analysisTime = analysisTime;
    }

    public Double getMoisture() {
        return moisture;
    }

    public void setMoisture(Double moisture) {
        this.moisture = moisture;
    }

    public Double getAsh() {
        return ash;
    }

    public void setAsh(Double ash) {
        this.ash = ash;
    }

    public Double getVolatileMatter() {
        return volatileMatter;
    }

    public void setVolatileMatter(Double volatileMatter) {
        this.volatileMatter = volatileMatter;
    }

    public Double getFixedCarbon() {
        return fixedCarbon;
    }

    public void setFixedCarbon(Double fixedCarbon) {
        this.fixedCarbon = fixedCarbon;
    }

    public Double getSulfur() {
        return sulfur;
    }

    public void setSulfur(Double sulfur) {
        this.sulfur = sulfur;
    }

    public Double getCalorificValue() {
        return calorificValue;
    }

    public void setCalorificValue(Double calorificValue) {
        this.calorificValue = calorificValue;
    }

    public Double getAshFusionTemperature() {
        return ashFusionTemperature;
    }

    public void setAshFusionTemperature(Double ashFusionTemperature) {
        this.ashFusionTemperature = ashFusionTemperature;
    }

    public String getOperator() {
        return operator;
    }

    public void setOperator(String operator) {
        this.operator = operator;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public CoalSample getSample() {
        return sample;
    }

    public void setSample(CoalSample sample) {
        this.sample = sample;
    }
}
