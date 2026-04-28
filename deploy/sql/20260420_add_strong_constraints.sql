-- 强约束迁移脚本（PostgreSQL）
-- 目标：为业务键补唯一约束，并补充外键约束，防止脏数据写入
-- 执行前请先完成备份

BEGIN;

-- 1) 唯一约束：被引用字段必须唯一（幂等）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_coal_sample_sample_id') THEN
        ALTER TABLE coal_sample ADD CONSTRAINT uk_coal_sample_sample_id UNIQUE (sample_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_asset_location_code') THEN
        ALTER TABLE asset_location ADD CONSTRAINT uk_asset_location_code UNIQUE (code);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_asset_category_code') THEN
        ALTER TABLE asset_category ADD CONSTRAINT uk_asset_category_code UNIQUE (code);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_asset_supplier_supplier_id') THEN
        ALTER TABLE asset_supplier ADD CONSTRAINT uk_asset_supplier_supplier_id UNIQUE (supplier_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_asset_device_device_id') THEN
        ALTER TABLE asset_device ADD CONSTRAINT uk_asset_device_device_id UNIQUE (device_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_alarm_record_alarm_id') THEN
        ALTER TABLE alarm_record ADD CONSTRAINT uk_alarm_record_alarm_id UNIQUE (alarm_id);
    END IF;
END $$;

-- 2) 外键约束：按业务键建立（幂等）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_coal_analysis_result_sample_id') THEN
        ALTER TABLE coal_analysis_result
            ADD CONSTRAINT fk_coal_analysis_result_sample_id
            FOREIGN KEY (sample_id) REFERENCES coal_sample(sample_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_asset_device_location_code') THEN
        ALTER TABLE asset_device
            ADD CONSTRAINT fk_asset_device_location_code
            FOREIGN KEY (location_id) REFERENCES asset_location(code);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_asset_device_category_code') THEN
        ALTER TABLE asset_device
            ADD CONSTRAINT fk_asset_device_category_code
            FOREIGN KEY (category_id) REFERENCES asset_category(code);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_asset_device_supplier_id') THEN
        ALTER TABLE asset_device
            ADD CONSTRAINT fk_asset_device_supplier_id
            FOREIGN KEY (supplier_id) REFERENCES asset_supplier(supplier_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_alarm_notification_alarm_id') THEN
        ALTER TABLE alarm_notification
            ADD CONSTRAINT fk_alarm_notification_alarm_id
            FOREIGN KEY (alarm_id) REFERENCES alarm_record(alarm_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_alarm_notification_device_id') THEN
        ALTER TABLE alarm_notification
            ADD CONSTRAINT fk_alarm_notification_device_id
            FOREIGN KEY (device_id) REFERENCES asset_device(device_id);
    END IF;
END $$;

COMMIT;
