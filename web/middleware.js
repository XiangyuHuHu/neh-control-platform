/**
 * Vercel Edge：将 /api/* 代理到现场后端（环境变量 API_PROXY_TARGET）。
 * 示例：https://neh.example.com  （不要末尾斜杠）
 */
export const config = {
  matcher: '/api/:path*',
}

export default async function middleware(request) {
  const backend = process.env.API_PROXY_TARGET
  if (!backend) {
    return new Response(
      JSON.stringify({
        error: 'API_PROXY_TARGET not configured',
        hint: '在 Vercel 项目 Settings → Environment Variables 添加 API_PROXY_TARGET，值为公网可访问的后端地址（如 Cloudflare 隧道域名）',
      }),
      { status: 502, headers: { 'content-type': 'application/json; charset=utf-8' } },
    )
  }

  const incoming = new URL(request.url)
  const base = backend.replace(/\/$/, '')
  const upstream = `${base}${incoming.pathname}${incoming.search}`

  const headers = new Headers(request.headers)
  try {
    headers.set('host', new URL(base).host)
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid API_PROXY_TARGET' }), { status: 502 })
  }
  headers.delete('connection')

  const init = {
    method: request.method,
    headers,
  }
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = request.body
  }

  return fetch(upstream, init)
}
