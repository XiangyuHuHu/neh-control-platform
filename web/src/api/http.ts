/** 与后端 HTTP Basic 一致：登录成功后写入 sessionStorage */
const AUTH_KEY = 'apiBasicAuth'

export function getApiBasicAuthHeader(): Record<string, string> {
  if (typeof sessionStorage === 'undefined') {
    return {}
  }
  const raw = sessionStorage.getItem(AUTH_KEY)
  if (!raw) {
    return {}
  }
  return { Authorization: `Basic ${raw}` }
}

export function setApiBasicAuth(username: string, password: string) {
  if (typeof sessionStorage === 'undefined') {
    return
  }
  sessionStorage.setItem(AUTH_KEY, btoa(`${username}:${password}`))
}

export function clearApiBasicAuth() {
  if (typeof sessionStorage === 'undefined') {
    return
  }
  sessionStorage.removeItem(AUTH_KEY)
}

export function buildJsonHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    ...getApiBasicAuthHeader(),
    ...(extra || {}),
  }
}
