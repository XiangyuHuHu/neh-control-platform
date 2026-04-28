package com.example.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "platform.model-services")
public class ModelServiceProperties {

    private final Endpoint smartDensity = new Endpoint();
    private final Endpoint smartReagent = new Endpoint();

    public Endpoint getSmartDensity() {
        return smartDensity;
    }

    public Endpoint getSmartReagent() {
        return smartReagent;
    }

    public static class Endpoint {
        private boolean enabled = false;
        private String baseUrl = "";
        private int timeoutMs = 3000;

        public boolean isEnabled() {
            return enabled;
        }

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }

        public int getTimeoutMs() {
            return timeoutMs;
        }

        public void setTimeoutMs(int timeoutMs) {
            this.timeoutMs = timeoutMs;
        }
    }
}
