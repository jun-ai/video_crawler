<template>
  <div class="legal-page">
    <div class="legal-container">
      <!-- 顶部面包屑 -->
      <div class="legal-breadcrumb">
        <router-link to="/">首页</router-link>
        <span class="legal-breadcrumb__sep">/</span>
        <span>{{ title }}</span>
      </div>

      <!-- 标题 -->
      <h1 class="legal-title">{{ title }}</h1>
      <p class="legal-updated">最后更新：{{ updated }}</p>

      <!-- 内容卡片 -->
      <article class="legal-content">
        <slot />
      </article>

      <!-- 联系 CTA -->
      <div class="legal-contact">
        <p>有疑问？联系客服</p>
        <p class="legal-contact__small">
          在小红书私信 @Fluenty · 或邮件至 support@fluenty.cn
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  updated: { type: String, default: '2026-06-29' }
})
</script>

<style scoped>
.legal-page {
  min-height: calc(100vh - 64px - 200px);
  padding: 48px 24px 64px;
  background: var(--color-bg-base);
}

.legal-container {
  max-width: 760px;
  margin: 0 auto;
}

.legal-breadcrumb {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 20px;
}

.legal-breadcrumb a {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--sf-duration-normal);
}

.legal-breadcrumb a:hover {
  color: var(--color-brand);
}

.legal-breadcrumb__sep {
  margin: 0 8px;
  color: var(--color-border);
}

.legal-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  margin: 0 0 8px 0;
}

.legal-updated {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 32px 0;
}

.legal-content {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 36px 40px;
  box-shadow: var(--shadow-sm);
  line-height: 1.75;
  color: var(--color-text-primary);
  font-size: 15px;
}

.legal-content :deep(h2) {
  font-size: 19px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 32px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.legal-content :deep(h2:first-child) {
  margin-top: 0;
}

.legal-content :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 24px 0 8px 0;
}

.legal-content :deep(p) {
  margin: 0 0 12px 0;
  color: var(--color-text-primary);
}

.legal-content :deep(ul),
.legal-content :deep(ol) {
  padding-left: 24px;
  margin: 8px 0 16px 0;
}

.legal-content :deep(li) {
  margin: 4px 0;
}

.legal-content :deep(strong) {
  color: var(--color-text-primary);
  font-weight: 600;
}

.legal-content :deep(.highlight) {
  background: rgba(37, 99, 235, 0.08);
  border-left: 3px solid var(--color-brand);
  padding: 12px 16px;
  border-radius: 4px;
  margin: 16px 0;
  color: var(--color-text-primary);
}

.legal-content :deep(.warning) {
  background: rgba(245, 158, 11, 0.08);
  border-left: 3px solid #F59E0B;
  padding: 12px 16px;
  border-radius: 4px;
  margin: 16px 0;
  color: var(--color-text-primary);
}

.legal-contact {
  text-align: center;
  margin-top: 32px;
  padding: 24px;
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
}

.legal-contact p {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 15px;
  font-weight: 500;
}

.legal-contact__small {
  margin-top: 6px !important;
  font-size: 13px !important;
  color: var(--color-text-secondary) !important;
  font-weight: 400 !important;
}

@media (max-width: 640px) {
  .legal-page {
    padding: 24px 16px 48px;
  }
  .legal-content {
    padding: 24px 20px;
  }
  .legal-title {
    font-size: 24px;
  }
}
</style>
