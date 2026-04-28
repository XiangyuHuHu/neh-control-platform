package com.example.platform.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 方法级安全 SpEL：未开启 API 认证时放行业务注解。
 */
@Component("authz")
public class AuthzExpressions {

    @Value("${platform.security.secure-api:false}")
    private boolean secureApi;

    /** 未启用 {@code platform.security.secure-api} 时为 true，与 {@code @PreAuthorize} 组合使用 */
    public boolean insecure() {
        return !secureApi;
    }
}
