export function loginRoute(currentFullPath) {
  const redirect = typeof currentFullPath === 'string' && currentFullPath.startsWith('/')
    ? currentFullPath
    : '/'
  return { path: '/login', query: { redirect } }
}

export function goLogin(router, currentFullPath) {
  return router.push(loginRoute(currentFullPath))
}
