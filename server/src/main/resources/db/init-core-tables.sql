CREATE TABLE IF NOT EXISTS work_order (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(64),
    title VARCHAR(255),
    description TEXT,
    type VARCHAR(64),
    priority VARCHAR(32),
    status VARCHAR(32),
    device_id BIGINT,
    assignee_id BIGINT,
    creator_id BIGINT,
    planned_start_time TIMESTAMP,
    planned_end_time TIMESTAMP,
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    result TEXT,
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_work_order_status ON work_order(status);
CREATE INDEX IF NOT EXISTS idx_work_order_created_at ON work_order(created_at);

CREATE TABLE IF NOT EXISTS energy_consumption (
    id BIGSERIAL PRIMARY KEY,
    record_date DATE,
    shift VARCHAR(32),
    energy_type VARCHAR(64),
    consumption DOUBLE PRECISION,
    unit VARCHAR(32),
    unit_price DOUBLE PRECISION,
    cost DOUBLE PRECISION,
    related_output DOUBLE PRECISION,
    unit_consumption DOUBLE PRECISION,
    meter_reading DOUBLE PRECISION,
    meter_no VARCHAR(64),
    recorder VARCHAR(64),
    data_source VARCHAR(32),
    remark TEXT,
    create_by VARCHAR(64),
    create_time TIMESTAMP,
    update_by VARCHAR(64),
    update_time TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_energy_consumption_record_date ON energy_consumption(record_date);

INSERT INTO work_order (
    order_no, title, description, type, priority, status,
    device_id, assignee_id, creator_id,
    planned_start_time, planned_end_time, created_at, updated_at
)
SELECT *
FROM (
    VALUES
        ('WO-20260413-001', '主破碎机巡检', '例行巡检主破碎机振动与温度', '巡检', '中', '待处理', 1, 1001, 1000, now() - INTERVAL '2 hour', now() + INTERVAL '4 hour', now(), now()),
        ('WO-20260413-002', '皮带机润滑维护', '对给料皮带执行润滑维护', '保养', '中', '处理中', 2, 1002, 1000, now() - INTERVAL '6 hour', now() + INTERVAL '2 hour', now(), now()),
        ('WO-20260413-003', '筛分机异常复核', '复核筛分机报警并形成记录', '维修', '高', '已完成', 3, 1003, 1000, now() - INTERVAL '1 day', now() - INTERVAL '20 hour', now() - INTERVAL '1 day', now())
) AS seed(
    order_no, title, description, type, priority, status,
    device_id, assignee_id, creator_id,
    planned_start_time, planned_end_time, created_at, updated_at
)
WHERE NOT EXISTS (SELECT 1 FROM work_order LIMIT 1);

INSERT INTO energy_consumption (
    record_date, shift, energy_type, consumption, unit, unit_price, cost,
    related_output, unit_consumption, meter_reading, meter_no, recorder,
    data_source, remark, create_by, create_time, update_by, update_time
)
SELECT *
FROM (
    VALUES
        (CURRENT_DATE, 'DAY', 'ELECTRICITY', 1280.5, 'kWh', 0.72, 921.96, 560.0, 2.2866, 102345.2, 'ELEC-M-01', '系统', 'AUTO', '测试初始化数据', 'system', now(), 'system', now()),
        (CURRENT_DATE - 1, 'NIGHT', 'ELECTRICITY', 1198.0, 'kWh', 0.72, 862.56, 540.0, 2.2185, 101064.7, 'ELEC-M-01', '系统', 'AUTO', '测试初始化数据', 'system', now(), 'system', now()),
        (CURRENT_DATE - 2, 'DAY', 'WATER', 356.0, 't', 3.10, 1103.60, 525.0, 0.6781, 55672.4, 'WATER-M-02', '系统', 'AUTO', '测试初始化数据', 'system', now(), 'system', now())
) AS seed(
    record_date, shift, energy_type, consumption, unit, unit_price, cost,
    related_output, unit_consumption, meter_reading, meter_no, recorder,
    data_source, remark, create_by, create_time, update_by, update_time
)
WHERE NOT EXISTS (SELECT 1 FROM energy_consumption LIMIT 1);

CREATE TABLE IF NOT EXISTS power_operation_application (
    id BIGSERIAL PRIMARY KEY,
    application_no VARCHAR(64) UNIQUE,
    device_id BIGINT,
    device_name VARCHAR(255),
    power_room VARCHAR(128),
    cabinet_no VARCHAR(64),
    workflow_status VARCHAR(64),
    operation_type VARCHAR(64),
    risk_level VARCHAR(32),
    reason TEXT,
    requested_by VARCHAR(64),
    approved_by VARCHAR(64),
    verified_by VARCHAR(64),
    repaired_by VARCHAR(64),
    dispatch_decision VARCHAR(64),
    remaining_tag_count INTEGER DEFAULT 0,
    planned_power_off_time TIMESTAMP,
    planned_power_on_time TIMESTAMP,
    approved_at TIMESTAMP,
    verified_at TIMESTAMP,
    repair_started_at TIMESTAMP,
    repair_completed_at TIMESTAMP,
    power_on_applied_at TIMESTAMP,
    power_on_approved_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_power_operation_status ON power_operation_application(workflow_status);
CREATE INDEX IF NOT EXISTS idx_power_operation_room ON power_operation_application(power_room);
CREATE INDEX IF NOT EXISTS idx_power_operation_created_at ON power_operation_application(created_at);

CREATE TABLE IF NOT EXISTS power_operation_log (
    id BIGSERIAL PRIMARY KEY,
    application_id BIGINT NOT NULL,
    action_type VARCHAR(64),
    before_status VARCHAR(64),
    after_status VARCHAR(64),
    operator_name VARCHAR(64),
    comment TEXT,
    created_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_power_operation_log_app_id ON power_operation_log(application_id);
CREATE INDEX IF NOT EXISTS idx_power_operation_log_created_at ON power_operation_log(created_at);

CREATE TABLE IF NOT EXISTS power_device_tag_record (
    id BIGSERIAL PRIMARY KEY,
    application_id BIGINT NOT NULL,
    device_id BIGINT,
    tag_user VARCHAR(64),
    tag_status VARCHAR(32),
    tagged_at TIMESTAMP,
    untagged_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_power_device_tag_app_id ON power_device_tag_record(application_id);
CREATE INDEX IF NOT EXISTS idx_power_device_tag_status ON power_device_tag_record(tag_status);
