package com.example.platform.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import jakarta.persistence.*;

@Entity
@Table(name = "asset_device")
public class AssetDevice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "device_id", unique = true)
    private String deviceId;
    private String name;
    private String model;
    private String specification;
    private String manufacturer;
    @Column(name = "supplier_id")
    private String supplierId;
    private String purchaseDate;
    private String installDate;
    private String commissioningDate;
    private String status;
    @Column(name = "location_id")
    private String locationId;
    @Column(name = "category_id")
    private String categoryId;
    private String description;
    private String technicalParameters;
    private String serialNumber;
    private String assetNumber;
    private String responsiblePerson;
    private String maintenancePerson;

    @ManyToOne
    @JoinColumn(
            name = "location_id",
            referencedColumnName = "code",
            insertable = false,
            updatable = false
    )
    @TableField(exist = false)
    private AssetLocation location;

    @ManyToOne
    @JoinColumn(
            name = "category_id",
            referencedColumnName = "code",
            insertable = false,
            updatable = false
    )
    @TableField(exist = false)
    private AssetCategory category;

    @ManyToOne
    @JoinColumn(
            name = "supplier_id",
            referencedColumnName = "supplier_id",
            insertable = false,
            updatable = false
    )
    @TableField(exist = false)
    private AssetSupplier supplier;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getSpecification() {
        return specification;
    }

    public void setSpecification(String specification) {
        this.specification = specification;
    }

    public String getManufacturer() {
        return manufacturer;
    }

    public void setManufacturer(String manufacturer) {
        this.manufacturer = manufacturer;
    }

    public String getSupplierId() {
        return supplierId;
    }

    public void setSupplierId(String supplierId) {
        this.supplierId = supplierId;
    }

    public String getPurchaseDate() {
        return purchaseDate;
    }

    public void setPurchaseDate(String purchaseDate) {
        this.purchaseDate = purchaseDate;
    }

    public String getInstallDate() {
        return installDate;
    }

    public void setInstallDate(String installDate) {
        this.installDate = installDate;
    }

    public String getCommissioningDate() {
        return commissioningDate;
    }

    public void setCommissioningDate(String commissioningDate) {
        this.commissioningDate = commissioningDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getLocationId() {
        return locationId;
    }

    public void setLocationId(String locationId) {
        this.locationId = locationId;
    }

    public String getCategoryId() {
        return categoryId;
    }

    public void setCategoryId(String categoryId) {
        this.categoryId = categoryId;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getTechnicalParameters() {
        return technicalParameters;
    }

    public void setTechnicalParameters(String technicalParameters) {
        this.technicalParameters = technicalParameters;
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public void setSerialNumber(String serialNumber) {
        this.serialNumber = serialNumber;
    }

    public String getAssetNumber() {
        return assetNumber;
    }

    public void setAssetNumber(String assetNumber) {
        this.assetNumber = assetNumber;
    }

    public String getResponsiblePerson() {
        return responsiblePerson;
    }

    public void setResponsiblePerson(String responsiblePerson) {
        this.responsiblePerson = responsiblePerson;
    }

    public String getMaintenancePerson() {
        return maintenancePerson;
    }

    public void setMaintenancePerson(String maintenancePerson) {
        this.maintenancePerson = maintenancePerson;
    }

    public AssetLocation getLocation() {
        return location;
    }

    public void setLocation(AssetLocation location) {
        this.location = location;
    }

    public AssetCategory getCategory() {
        return category;
    }

    public void setCategory(AssetCategory category) {
        this.category = category;
    }

    public AssetSupplier getSupplier() {
        return supplier;
    }

    public void setSupplier(AssetSupplier supplier) {
        this.supplier = supplier;
    }

}
