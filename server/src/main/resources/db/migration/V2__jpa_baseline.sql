-- JPA 实体与备件表基线（PostgreSQL），与 Hibernate validate 对齐（V2：修复曾误开 baseline-on-migrate 的库）
-- 幂等：全部使用 IF NOT EXISTS

CREATE TABLE IF NOT EXISTS organization (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    description TEXT,
    parent_id BIGINT,
    level INTEGER,
    sort INTEGER,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    description TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    description TEXT,
    type VARCHAR(64),
    url VARCHAR(512),
    method VARCHAR(32),
    parent_id BIGINT,
    sort INTEGER,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    name VARCHAR(255),
    phone VARCHAR(64),
    email VARCHAR(255),
    status VARCHAR(64),
    organization_id BIGINT
);

CREATE TABLE IF NOT EXISTS user_role (
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS role_permission (
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS asset_location (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255) UNIQUE,
    description TEXT,
    parent_id BIGINT,
    level INTEGER,
    sort INTEGER,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS asset_category (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255) UNIQUE,
    description TEXT,
    parent_id BIGINT,
    level INTEGER,
    sort INTEGER,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS asset_supplier (
    id BIGSERIAL PRIMARY KEY,
    supplier_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    contact_person VARCHAR(255),
    contact_phone VARCHAR(255),
    email VARCHAR(255),
    address TEXT,
    description TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS asset_device (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    model VARCHAR(255),
    specification VARCHAR(512),
    manufacturer VARCHAR(255),
    supplier_id VARCHAR(255),
    purchase_date VARCHAR(64),
    install_date VARCHAR(64),
    commissioning_date VARCHAR(64),
    status VARCHAR(64),
    location_id VARCHAR(255),
    category_id VARCHAR(255),
    description TEXT,
    technical_parameters TEXT,
    serial_number VARCHAR(255),
    asset_number VARCHAR(255),
    responsible_person VARCHAR(255),
    maintenance_person VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS alarm_record (
    id BIGSERIAL PRIMARY KEY,
    alarm_id VARCHAR(255) UNIQUE,
    device_id VARCHAR(255),
    point_id VARCHAR(255),
    rule_id VARCHAR(255),
    alarm_type VARCHAR(255),
    alarm_level VARCHAR(64),
    alarm_message TEXT,
    current_value DOUBLE PRECISION,
    start_time VARCHAR(64),
    end_time VARCHAR(64),
    status VARCHAR(64),
    handler VARCHAR(255),
    handle_time VARCHAR(64),
    handle_result TEXT
);

CREATE TABLE IF NOT EXISTS alarm_notification (
    id BIGSERIAL PRIMARY KEY,
    notification_id VARCHAR(255),
    alarm_id VARCHAR(255),
    device_id VARCHAR(255),
    notification_type VARCHAR(255),
    notification_content TEXT,
    recipient VARCHAR(255),
    send_time VARCHAR(64),
    status VARCHAR(64),
    response_time VARCHAR(64),
    response_result TEXT
);

CREATE TABLE IF NOT EXISTS alarm_rule (
    id BIGSERIAL PRIMARY KEY,
    rule_id VARCHAR(255),
    device_id VARCHAR(255),
    point_id VARCHAR(255),
    rule_name VARCHAR(255),
    rule_type VARCHAR(255),
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    operator VARCHAR(64),
    duration INTEGER,
    level VARCHAR(64),
    description TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS coal_sample (
    id BIGSERIAL PRIMARY KEY,
    sample_id VARCHAR(255) UNIQUE,
    sample_name VARCHAR(255),
    sample_time VARCHAR(64),
    sample_location VARCHAR(255),
    sample_type VARCHAR(255),
    sample_weight DOUBLE PRECISION,
    operator VARCHAR(255),
    remark TEXT,
    status VARCHAR(64),
    batch_no VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS coal_analysis_result (
    id BIGSERIAL PRIMARY KEY,
    result_id VARCHAR(255),
    sample_id VARCHAR(255),
    analysis_time VARCHAR(64),
    moisture DOUBLE PRECISION,
    ash DOUBLE PRECISION,
    volatile_matter DOUBLE PRECISION,
    fixed_carbon DOUBLE PRECISION,
    sulfur DOUBLE PRECISION,
    calorific_value DOUBLE PRECISION,
    ash_fusion_temperature DOUBLE PRECISION,
    operator VARCHAR(255),
    remark TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS production_report (
    id BIGSERIAL PRIMARY KEY,
    report_id VARCHAR(255),
    report_type VARCHAR(255),
    report_date VARCHAR(64),
    shift_id VARCHAR(64),
    production_amount DOUBLE PRECISION,
    production_rate DOUBLE PRECISION,
    equipment_availability DOUBLE PRECISION,
    energy_consumption DOUBLE PRECISION,
    material_consumption DOUBLE PRECISION,
    operator VARCHAR(255),
    remark TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS shift (
    id BIGSERIAL PRIMARY KEY,
    shift_id VARCHAR(255),
    shift_name VARCHAR(255),
    start_time VARCHAR(64),
    end_time VARCHAR(64),
    description TEXT,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS point (
    id BIGSERIAL PRIMARY KEY,
    point_id VARCHAR(255),
    device_id VARCHAR(255),
    point_name VARCHAR(255),
    point_type VARCHAR(255),
    unit VARCHAR(64),
    description TEXT,
    collect_protocol VARCHAR(255),
    collect_address VARCHAR(512),
    collect_frequency INTEGER,
    data_type VARCHAR(64),
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    status VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS asset_file (
    id BIGSERIAL PRIMARY KEY,
    file_id VARCHAR(255),
    device_id VARCHAR(255),
    file_name VARCHAR(512),
    file_type VARCHAR(255),
    file_url VARCHAR(1024),
    description TEXT,
    upload_time VARCHAR(64),
    uploader VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS asset_event (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255),
    device_id VARCHAR(255),
    event_type VARCHAR(255),
    event_name VARCHAR(255),
    event_time VARCHAR(64),
    operator VARCHAR(255),
    description TEXT,
    status VARCHAR(64),
    related_document VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS asset_change_log (
    id BIGSERIAL PRIMARY KEY,
    log_id VARCHAR(255),
    device_id VARCHAR(255),
    before_status VARCHAR(255),
    after_status VARCHAR(255),
    operator VARCHAR(255),
    change_time VARCHAR(64),
    reason TEXT,
    related_document VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS asset_device_relation (
    id BIGSERIAL PRIMARY KEY,
    parent_device_id VARCHAR(255),
    child_device_id VARCHAR(255),
    level INTEGER,
    sort INTEGER
);

CREATE TABLE IF NOT EXISTS device_runtime_data (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255),
    point_id VARCHAR(255),
    point_name VARCHAR(255),
    point_type VARCHAR(255),
    unit VARCHAR(64),
    value DOUBLE PRECISION,
    status VARCHAR(64),
    timestamp VARCHAR(64),
    collection_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS iot_tag (
    id BIGSERIAL PRIMARY KEY,
    tag_code VARCHAR(128) NOT NULL UNIQUE,
    tag_name VARCHAR(128) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    source_path VARCHAR(255) NOT NULL,
    device_code VARCHAR(128),
    device_name VARCHAR(128),
    area_code VARCHAR(128),
    data_type VARCHAR(64),
    unit VARCHAR(32),
    scan_rate INTEGER,
    deadband DOUBLE PRECISION,
    quality_rule VARCHAR(64),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    remark VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS iot_tag_mapping (
    id BIGSERIAL PRIMARY KEY,
    mapping_id VARCHAR(64) NOT NULL UNIQUE,
    tag_code VARCHAR(128) NOT NULL,
    business_code VARCHAR(128) NOT NULL,
    business_name VARCHAR(128) NOT NULL,
    source_path VARCHAR(255) NOT NULL,
    transform_rule VARCHAR(64),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    remark VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS iot_realtime (
    tag_code VARCHAR(128) NOT NULL PRIMARY KEY,
    value DOUBLE PRECISION,
    quality SMALLINT,
    unit VARCHAR(32),
    device_code VARCHAR(128),
    area_code VARCHAR(128),
    source_type VARCHAR(64),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS iot_history (
    id BIGSERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    tag_code VARCHAR(128) NOT NULL,
    value DOUBLE PRECISION,
    quality SMALLINT,
    source_type VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS spare_part (
    id BIGSERIAL PRIMARY KEY,
    part_no VARCHAR(128),
    part_name VARCHAR(255),
    specification VARCHAR(512),
    device_id BIGINT,
    device_name VARCHAR(255),
    stock_quantity INTEGER,
    safety_stock INTEGER,
    unit VARCHAR(32),
    storage_location VARCHAR(255),
    supplier VARCHAR(255),
    unit_price DOUBLE PRECISION,
    service_life INTEGER,
    last_replace_date DATE,
    next_replace_date DATE,
    status VARCHAR(64),
    remark TEXT,
    create_by VARCHAR(64),
    create_time TIMESTAMP,
    update_by VARCHAR(64),
    update_time TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_spare_part_device_id ON spare_part(device_id);
CREATE INDEX IF NOT EXISTS idx_alarm_notification_alarm_id ON alarm_notification(alarm_id);

-- 演示种子：资产 + 备件（仅当设备表为空时插入）
INSERT INTO asset_location (id, name, code, description, parent_id, level, sort, status)
SELECT 1, '主洗车间', 'LOC-MAIN', '演示', NULL, 1, 1, 'ACTIVE'
WHERE NOT EXISTS (SELECT 1 FROM asset_location LIMIT 1);

INSERT INTO asset_category (id, name, code, description, parent_id, level, sort, status)
SELECT 1, '动设备', 'CAT-ROT', '演示', NULL, 1, 1, 'ACTIVE'
WHERE NOT EXISTS (SELECT 1 FROM asset_category LIMIT 1);

INSERT INTO asset_supplier (id, supplier_id, name, contact_person, contact_phone, email, address, description, status)
SELECT 1, 'SUP-DEMO', '演示供应商', '联系人', '13800000000', 'demo@example.com', '本地', '演示', 'ACTIVE'
WHERE NOT EXISTS (SELECT 1 FROM asset_supplier LIMIT 1);

INSERT INTO asset_device (id, device_id, name, model, specification, manufacturer, supplier_id, purchase_date, install_date, commissioning_date, status, location_id, category_id, description, technical_parameters, serial_number, asset_number, responsible_person, maintenance_person)
SELECT 1, 'EQ-311-002', '311中煤卧式离心机', 'LW530', 'LW530', '演示制造', 'SUP-DEMO', '2020-01-01', '2020-03-01', '2020-04-01', '检修', 'LOC-MAIN', 'CAT-ROT', '演示设备', NULL, 'SN-311', 'AN-311', '机电班', '机电班'
WHERE NOT EXISTS (SELECT 1 FROM asset_device WHERE id = 1);

INSERT INTO asset_device (id, device_id, name, model, specification, manufacturer, supplier_id, purchase_date, install_date, commissioning_date, status, location_id, category_id, description, technical_parameters, serial_number, asset_number, responsible_person, maintenance_person)
SELECT 2, 'EQ-325-003', '325矸石脱介筛', 'ZK1856', 'ZK1856', '演示制造', 'SUP-DEMO', '2019-06-01', '2019-08-01', '2019-09-01', '在用', 'LOC-MAIN', 'CAT-ROT', '演示设备', NULL, 'SN-325', 'AN-325', '生产三班', '生产三班'
WHERE NOT EXISTS (SELECT 1 FROM asset_device WHERE id = 2);

INSERT INTO asset_device (id, device_id, name, model, specification, manufacturer, supplier_id, purchase_date, install_date, commissioning_date, status, location_id, category_id, description, technical_parameters, serial_number, asset_number, responsible_person, maintenance_person)
SELECT 3, 'EQ-101-001', '101原煤皮带机', 'DTII-800', 'DTII-800', '演示制造', 'SUP-DEMO', '2018-01-01', '2018-02-01', '2018-03-01', '在用', 'LOC-MAIN', 'CAT-ROT', '演示设备', NULL, 'SN-101', 'AN-101', '生产二班', '生产二班'
WHERE NOT EXISTS (SELECT 1 FROM asset_device WHERE id = 3);

INSERT INTO spare_part (part_no, part_name, specification, device_id, device_name, stock_quantity, safety_stock, unit, storage_location, supplier, unit_price, service_life, last_replace_date, next_replace_date, status, remark, create_by, create_time, update_by, update_time)
SELECT 'SP-311-002', '离心机主轴轴承', 'SKF-23122', 1, '311中煤卧式离心机', 1, 3, '套', 'A-03', 'SKF', 1200.0, 8000, CURRENT_DATE - 200, CURRENT_DATE + 5, 'LOW_STOCK', '演示种子', 'system', now(), 'system', now()
WHERE NOT EXISTS (SELECT 1 FROM spare_part WHERE part_no = 'SP-311-002');

INSERT INTO spare_part (part_no, part_name, specification, device_id, device_name, stock_quantity, safety_stock, unit, storage_location, supplier, unit_price, service_life, last_replace_date, next_replace_date, status, remark, create_by, create_time, update_by, update_time)
SELECT 'SP-325-011', '筛板组件', 'ZK1856-筛板', 2, '325矸石脱介筛', 2, 2, '套', 'B-02', '本地', 800.0, 5000, CURRENT_DATE - 100, CURRENT_DATE + 30, 'NORMAL', '演示种子', 'system', now(), 'system', now()
WHERE NOT EXISTS (SELECT 1 FROM spare_part WHERE part_no = 'SP-325-011');

INSERT INTO spare_part (part_no, part_name, specification, device_id, device_name, stock_quantity, safety_stock, unit, storage_location, supplier, unit_price, service_life, last_replace_date, next_replace_date, status, remark, create_by, create_time, update_by, update_time)
SELECT 'SP-101-008', '皮带托辊', 'TD75-108', 3, '101原煤皮带机', 18, 12, '件', 'C-05', '本地', 35.0, NULL, NULL, NULL, 'NORMAL', '演示种子', 'system', now(), 'system', now()
WHERE NOT EXISTS (SELECT 1 FROM spare_part WHERE part_no = 'SP-101-008');
