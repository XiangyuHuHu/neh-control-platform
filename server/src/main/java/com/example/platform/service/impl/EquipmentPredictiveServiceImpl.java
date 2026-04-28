package com.example.platform.service.impl;

import com.example.platform.entity.AssetDevice;
import com.example.platform.entity.SparePart;
import com.example.platform.mapper.SparePartMapper;
import com.example.platform.service.AssetDeviceService;
import com.example.platform.service.EquipmentPredictiveService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

@Service
public class EquipmentPredictiveServiceImpl implements EquipmentPredictiveService {

    private static final Logger log = LoggerFactory.getLogger(EquipmentPredictiveServiceImpl.class);

    private final AssetDeviceService assetDeviceService;
    private final SparePartMapper sparePartMapper;

    public EquipmentPredictiveServiceImpl(AssetDeviceService assetDeviceService, SparePartMapper sparePartMapper) {
        this.assetDeviceService = assetDeviceService;
        this.sparePartMapper = sparePartMapper;
    }

    @Override
    public Map<String, Object> predictiveBoard() {
        String generatedAt = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);

        List<AssetDevice> devices = safeListDevices();
        List<SparePart> parts = safeListSpareParts();

        List<Map<String, Object>> predictiveRows;
        boolean predictiveFromDb = !devices.isEmpty();
        if (predictiveFromDb) {
            predictiveRows = buildPredictiveRows(devices);
        } else {
            predictiveRows = defaultPredictiveRows();
        }

        List<Map<String, Object>> spareLinkages;
        boolean spareFromDb = !parts.isEmpty();
        if (spareFromDb) {
            spareLinkages = buildSpareLinkages(parts, devices);
        } else {
            spareLinkages = defaultSpareLinkages();
        }

        String dataSource;
        if (predictiveFromDb && spareFromDb) {
            dataSource = "database";
        } else if (!predictiveFromDb && !spareFromDb) {
            dataSource = "fallback";
        } else {
            dataSource = "mixed";
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("generatedAt", generatedAt);
        result.put("dataSource", dataSource);
        result.put("predictiveRows", predictiveRows);
        result.put("spareLinkages", spareLinkages);
        return result;
    }

    private List<AssetDevice> safeListDevices() {
        try {
            List<AssetDevice> list = assetDeviceService.findAll();
            return list == null ? List.of() : list.stream()
                    .filter(d -> d.getName() != null && !d.getName().isBlank())
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.warn("equipment predictive: load asset_device failed, using fallback predictive rows", e);
            return List.of();
        }
    }

    private List<SparePart> safeListSpareParts() {
        try {
            List<SparePart> list = sparePartMapper.selectList(null);
            return list == null ? List.of() : list.stream()
                    .filter(p -> p.getPartNo() != null && !p.getPartNo().isBlank())
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.warn("equipment predictive: load spare_part failed, using fallback spare linkages", e);
            return List.of();
        }
    }

    private List<Map<String, Object>> buildPredictiveRows(List<AssetDevice> devices) {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (AssetDevice d : devices) {
            int health = estimateHealthScore(d);
            int riskPct = Math.min(95, Math.max(5, 100 - health + (hashNoise(d) % 7)));
            String rul = estimateRul(health);
            String maintPlan = maintPlanForHealth(health);
            String[] pr = priorityFor(health, d.getStatus());
            rows.add(predictiveRow(d.getName(), health, riskPct + "%", rul, maintPlan, pr[0], pr[1]));
        }
        rows.sort(Comparator.comparingInt(m -> (Integer) m.get("healthScore")));
        if (rows.size() > 20) {
            return rows.subList(0, 20);
        }
        return rows;
    }

    private int estimateHealthScore(AssetDevice d) {
        String st = d.getStatus() == null ? "" : d.getStatus();
        int base;
        if (st.contains("检修") || st.contains("故障") || st.contains("维修")) {
            base = 54;
        } else if (st.contains("停用")) {
            base = 42;
        } else if (st.contains("备用")) {
            base = 78;
        } else {
            base = 86;
        }
        int noise = hashNoise(d) % 11 - 5;
        return Math.min(98, Math.max(38, base + noise));
    }

    private static int hashNoise(AssetDevice d) {
        return Math.abs(Objects.hash(d.getId(), d.getDeviceId(), d.getName()));
    }

    private static String estimateRul(int health) {
        if (health < 58) {
            return "约 3–7 天";
        }
        if (health < 72) {
            return "约 8–18 天";
        }
        if (health < 85) {
            return "约 20–40 天";
        }
        return "约 40–90 天";
    }

    private static String maintPlanForHealth(int health) {
        if (health < 58) {
            return "建议 48 小时内安排检修或停机检查";
        }
        if (health < 72) {
            return "建议本周内安排维保窗口";
        }
        if (health < 85) {
            return "纳入月度保养计划并加强点检";
        }
        return "按周期保养跟踪即可";
    }

    private static String[] priorityFor(int health, String status) {
        String st = status == null ? "" : status;
        if (health < 60 || st.contains("检修") || st.contains("故障")) {
            return new String[]{"P1", "high"};
        }
        if (health < 78) {
            return new String[]{"P2", "medium"};
        }
        return new String[]{"P3", "low"};
    }

    private List<Map<String, Object>> buildSpareLinkages(List<SparePart> parts, List<AssetDevice> devices) {
        Map<Long, String> idToName = devices.stream()
                .filter(d -> d.getId() != null)
                .collect(Collectors.toMap(AssetDevice::getId, AssetDevice::getName, (a, b) -> a));

        List<Map<String, Object>> rows = new ArrayList<>();
        for (SparePart p : parts) {
            String deviceLabel = resolveDeviceLabel(p, idToName);
            int stock = p.getStockQuantity() == null ? 0 : p.getStockQuantity();
            int safety = p.getSafetyStock() == null ? 0 : p.getSafetyStock();
            String[] action = linkageAction(stock, safety);
            rows.add(spareLinkage(deviceLabel, nullToEmpty(p.getPartName()), p.getPartNo(), stock, safety, action[0], action[1]));
        }
        rows.sort(Comparator.comparingInt(this::linkageRank));
        if (rows.size() > 20) {
            return rows.subList(0, 20);
        }
        return rows;
    }

    private static String nullToEmpty(String s) {
        return s == null ? "" : s;
    }

    private static String resolveDeviceLabel(SparePart p, Map<Long, String> idToName) {
        if (p.getDeviceName() != null && !p.getDeviceName().isBlank()) {
            return p.getDeviceName();
        }
        if (p.getDeviceId() != null) {
            String n = idToName.get(p.getDeviceId());
            if (n != null && !n.isBlank()) {
                return n;
            }
            return "设备ID " + p.getDeviceId();
        }
        return "未关联设备";
    }

    private static String[] linkageAction(int stock, int safety) {
        if (safety <= 0) {
            if (stock <= 0) {
                return new String[]{"库存为零，请紧急补库", "high"};
            }
            if (stock < 3) {
                return new String[]{"未设安全库存，建议设定基线并补货", "medium"};
            }
            return new String[]{"库存可用（建议维护安全库存）", "low"};
        }
        if (stock < safety) {
            return new String[]{"立即采购补库", "high"};
        }
        if (stock == safety) {
            return new String[]{"锁定本周备件", "medium"};
        }
        int margin = Math.max(1, safety / 4);
        if (stock <= safety + margin) {
            return new String[]{"关注补货", "medium"};
        }
        return new String[]{"库存充足", "low"};
    }

    private int linkageRank(Map<String, Object> row) {
        String level = String.valueOf(row.get("actionLevel"));
        return switch (level) {
            case "high" -> 0;
            case "medium" -> 1;
            default -> 2;
        };
    }

    private Map<String, Object> predictiveRow(
            String device,
            int healthScore,
            String failureRisk,
            String rul,
            String maintPlan,
            String priority,
            String priorityLevel
    ) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("device", device);
        map.put("healthScore", healthScore);
        map.put("failureRisk", failureRisk);
        map.put("rul", rul);
        map.put("maintPlan", maintPlan);
        map.put("priority", priority);
        map.put("priorityLevel", priorityLevel);
        return map;
    }

    private Map<String, Object> spareLinkage(
            String device,
            String partName,
            String partNo,
            int stock,
            int safetyStock,
            String action,
            String actionLevel
    ) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("device", device);
        map.put("partName", partName);
        map.put("partNo", partNo);
        map.put("stock", stock);
        map.put("safetyStock", safetyStock);
        map.put("action", action);
        map.put("actionLevel", actionLevel);
        return map;
    }

    private List<Map<String, Object>> defaultPredictiveRows() {
        return List.of(
                predictiveRow("311中煤卧式离心机", 64, "78%", "4 天", "24小时内停机检修", "P1", "high"),
                predictiveRow("325矸石脱介筛", 79, "42%", "11 天", "本周末窗口维保", "P2", "medium"),
                predictiveRow("602精煤压滤机入料泵", 92, "18%", "35 天", "按月保养即可", "P3", "low")
        );
    }

    private List<Map<String, Object>> defaultSpareLinkages() {
        return List.of(
                spareLinkage("311中煤卧式离心机", "主轴轴承", "SP-311-002", 1, 3, "立即采购补库", "high"),
                spareLinkage("325矸石脱介筛", "筛板组件", "SP-325-011", 2, 2, "锁定本周备件", "medium"),
                spareLinkage("101原煤皮带机", "托辊组件", "SP-101-008", 18, 12, "库存充足", "low")
        );
    }
}
